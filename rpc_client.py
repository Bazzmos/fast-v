import asyncio
import msgpack
import numpy as np

# RPC 消息类型
REQUEST = 0
RESPONSE = 1
NOTIFICATION = 2

class RpcClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.message_id = 0
        self.futures = {}

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(
            self.host, self.port
        )
        # 启动一个异步任务来监听响应
        self.response_task = asyncio.create_task(self._read_responses())

    async def _read_responses(self):
        try:
            while True:
                data = await self.reader.read(4)
                if not data:
                    break
                msg_len = int.from_bytes(data, 'big')
                body = await self.reader.readexactly(msg_len)
                response = msgpack.unpackb(body, raw=False)
                
                msg_type, msg_id, error, result = response
                
                if msg_id in self.futures:
                    future = self.futures.pop(msg_id)
                    if error:
                        future.set_exception(Exception(error))
                    else:
                        future.set_result(result)
        except asyncio.IncompleteReadError:
            pass # 连接断开
        except Exception as e:
            print(f"Error reading response: {e}")

    async def call(self, method, *params):
        """发起 RPC 调用"""
        self.message_id += 1
        msg_id = self.message_id
        
        request = [REQUEST, msg_id, method, list(params)]
        packed_request = msgpack.packb(request, use_bin_type=True)
        
        request_len = len(packed_request).to_bytes(4, 'big')
        
        self.writer.write(request_len + packed_request)
        await self.writer.drain()
        
        future = asyncio.Future()
        self.futures[msg_id] = future
        
        return await future

async def main_client():
    client = RpcClient('127.0.0.1', 8000)
    await client.connect()

    # 1. 调用 add_vectors 方法
    print("Calling 'add_vectors'...")
    new_vectors = np.random.rand(5, 1000).astype(np.float32).tolist()
    add_result = await client.call('add_vectors', new_vectors)
    print("Add vectors result:", add_result)

    # 2. 调用 search 方法
    print("\nCalling 'search'...")
    queries = np.random.rand(2, 1000).astype(np.float32).tolist()
    search_result = await client.call('search', queries, 3)
    print("Search result:", search_result)

    # 3. 调用 trigger_update 方法
    print("\nCalling 'trigger_update'...")
    update_result = await client.call('trigger_update')
    print("Trigger update result:", update_result)

if __name__ == "__main__":
    asyncio.run(main_client())