# 使用一个官方的 NVIDIA CUDA 镜像作为基础
# 这个镜像包含了 CUDA Toolkit 和 cuDNN，非常适合 GPU 计算任务
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# 设置工作目录
WORKDIR /app

# 安装必要的系统依赖，如 Python3 和 pip
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# 为 python3 创建软连接
RUN ln -s /usr/bin/python3 /usr/bin/python

# 复制 requirements.txt 到容器中
COPY requirements.txt .

# 使用 pip 安装所有 Python 依赖
# --no-cache-dir 减少镜像大小
RUN pip3 install --no-cache-dir -r requirements.txt

# 复制所有应用代码
COPY rpc_server.py .
COPY main_faiss.py .
COPY requirements.txt .

# 暴露服务端口
EXPOSE 8000

# 启动服务器的命令
# --host 0.0.0.0 确保容器内的服务可以从外部访问
CMD ["python3", "rpc_server.py"]
