import numpy as np
import threading
import msgpack
from fastapi import FastAPI, Request, Response, HTTPException
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

# ----------------- FastAPI 应用和调度器配置 -----------------
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

# ----------------- 接口实现 -----------------

@app.post("/search")
async def search_vectors(request: Request):
    """
    接收 MessagePack 编码的查询向量，执行比对并返回 MessagePack 结果。
    """
    try:
        # 1. 解析 MessagePack 请求体
        body = await request.body()
        data = msgpack.unpackb(body, raw=False)
        
        # 2. 从解析后的数据中获取参数
        queries = np.array(data["queries"], dtype=np.float32)
        k = data.get("k", 10)  # 如果没有 k，默认为 10

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"MessagePack 解码失败或数据格式错误: {e}")

    current_idx = get_current_index()
    if current_idx is None:
        raise HTTPException(status_code=503, detail="索引尚未加载，请稍候。")

    try:
        with lock:
            D, I = current_idx.search(queries, k)
        
        # 3. 将结果打包成 MessagePack 格式并返回
        # 注意：np.ndarray 需要先转换为列表
        response_data = {
            "distances": D.tolist(),
            "indices": I.tolist()
        }
        return Response(content=msgpack.packb(response_data, use_bin_type=True), media_type="application/x-msgpack")

    except Exception as e:
        print(f"查询失败: {e}")
        raise HTTPException(status_code=500, detail="向量比对失败。")

@app.post("/add_vectors")
async def add_vectors(request: Request):
    """
    接收 MessagePack 编码的批量向量，并将其放入队列。
    """
    try:
        body = await request.body()
        data = msgpack.unpackb(body, raw=False)
        vectors = data.get("vectors")

        if not vectors:
            return Response(content=msgpack.packb({"message": "请求中没有向量。", "status": "no_change"}), media_type="application/x-msgpack")

        add_vectors_to_queue(vectors)

        response_data = {"message": f"已将 {len(vectors)} 条向量添加到队列，将在下次更新中处理。", "status": "queued"}
        return Response(content=msgpack.packb(response_data, use_bin_type=True), media_type="application/x-msgpack")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"MessagePack 解码失败或数据格式错误: {e}")

@app.post("/trigger_update")
async def trigger_index_update():
    """
    手动触发后台索引更新。
    """
    threading.Thread(target=build_and_load_index_task, daemon=True).start()
    
    response_data = {"message": "索引更新任务已在后台启动。", "status": "processing"}
    return Response(content=msgpack.packb(response_data, use_bin_type=True), media_type="application/x-msgpack")

# ----------------- 运行指令 -----------------
# 保存此文件为 app_msgpack.py
# 终端中运行: uvicorn app_msgpack:app --host 0.0.0.0 --port 8000