import requests
import msgpack
import numpy as np

BASE_URL = "http://127.0.0.1:8000"

def search_vectors_msgpack(queries, k=10):
    """
    发送 MessagePack 格式的搜索请求
    """
    # 准备请求数据
    request_data = {
        "queries": queries.tolist(),
        "k": k
    }
    # 打包为 MessagePack
    packed_data = msgpack.packb(request_data, use_bin_type=True)
    
    headers = {"Content-Type": "application/x-msgpack"}
    
    try:
        response = requests.post(f"{BASE_URL}/search", data=packed_data, headers=headers)
        response.raise_for_status() # 如果请求失败，抛出异常
        
        # 解包 MessagePack 响应
        unpacked_response = msgpack.unpackb(response.content, raw=False)
        return unpacked_response
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

def add_vectors_msgpack(vectors):
    """
    发送 MessagePack 格式的批量新增向量请求
    """
    request_data = {
        "vectors": vectors.tolist()
    }
    packed_data = msgpack.packb(request_data, use_bin_type=True)
    
    headers = {"Content-Type": "application/x-msgpack"}

    try:
        response = requests.post(f"{BASE_URL}/add_vectors", data=packed_data, headers=headers)
        response.raise_for_status()
        unpacked_response = msgpack.unpackb(response.content, raw=False)
        return unpacked_response
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        return None

if __name__ == "__main__":
    # 示例用法
    # 1. 模拟新增一些向量
    new_vectors = np.random.rand(5, 1000).astype(np.float32)
    print("添加向量结果:", add_vectors_msgpack(new_vectors))

    # 2. 模拟比对查询
    query_vectors = np.random.rand(2, 1000).astype(np.float32)
    search_results = search_vectors_msgpack(query_vectors, k=3)
    
    if search_results:
        print("\n搜索结果:")
        print(search_results)