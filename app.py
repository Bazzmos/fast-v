import numpy as np
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from apscheduler.schedulers.background import BackgroundScheduler
from main_faiss import (
    build_and_load_index_task,
    get_current_index,
    lock,
    add_vectors_to_queue,
)

# 假设向量维度
d = 1000

# Pydantic 模型，用于验证输入数据
class VectorSearchRequest(BaseModel):
    queries: List[List[float]]
    k: int = 10

class AddVectorsRequest(BaseModel):
    vectors: List[List[float]]

class UpdateResponse(BaseModel):
    message: str
    status: str

# 初始化 FastAPI 应用和 APScheduler
app = FastAPI()
scheduler = BackgroundScheduler()

# ----------------- 应用生命周期管理 -----------------

@app.on_event("startup")
async def startup_event():
    """在应用启动时执行的逻辑"""
    print("应用启动中...")
    
    # 立即启动一次后台索引构建任务，以确保首次加载索引
    threading.Thread(target=build_and_load_index_task, daemon=True).start()
    
    # 配置并启动 APScheduler 定时任务
    # 定时任务每隔2小时运行一次，调用 build_and_load_index_task
    scheduler.add_job(build_and_load_index_task, 'interval', hours=2)
    scheduler.start()
    print("APScheduler 定时任务已启动，每2小时更新一次索引。")

@app.on_event("shutdown")
async def shutdown_event():
    """在应用关闭时执行的逻辑"""
    print("应用正在关闭...")
    scheduler.shutdown()
    print("APScheduler 已关闭。")

# ----------------- HTTP 接口 -----------------

@app.post("/search")
async def search_vectors(request: VectorSearchRequest):
    """
    通过 POST 请求接收一个或多个查询向量，并返回最近邻。
    """
    current_idx = get_current_index()
    
    if current_idx is None:
        raise HTTPException(status_code=503, detail="索引尚未加载，请稍候。")

    query_vectors = np.array(request.queries, dtype=np.float32)
    k = request.k
    
    try:
        # 在 GPU 上执行查询
        with lock:
            D, I = current_idx.search(query_vectors, k)
        
        # 将结果转换为 Python 列表以便 JSON 序列化
        results = [
            {"distances": row_d.tolist(), "indices": row_i.tolist()}
            for row_d, row_i in zip(D, I)
        ]
        return {"results": results}
    except Exception as e:
        print(f"查询失败: {e}")
        raise HTTPException(status_code=500, detail="向量比对失败。")

@app.post("/add_vectors", response_model=UpdateResponse)
async def add_vectors(request: AddVectorsRequest):
    """
    接收批量新增向量，并将其放入队列，等待后台处理。
    """
    if not request.vectors:
        return {"message": "请求中没有向量。", "status": "no_change"}
    
    # 将批量新增的向量添加到队列
    add_vectors_to_queue(request.vectors)
    
    return {"message": f"已将 {len(request.vectors)} 条向量添加到队列，将在下次更新中处理。", "status": "queued"}

@app.post("/trigger_update", response_model=UpdateResponse)
async def trigger_index_update():
    """
    手动触发后台索引更新。
    """
    # 启动一个独立的线程来执行更新任务
    threading.Thread(target=build_and_load_index_task, daemon=True).start()
    return {"message": "索引更新任务已在后台启动。", "status": "processing"}

# ----------------- 运行指令 -----------------
# 保存此文件为 app.py
# 终端中运行: uvicorn app:app --host 0.0.0.0 --port 8000