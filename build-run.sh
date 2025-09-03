#!/bin/bash

# 定义镜像名称
IMAGE_NAME="faiss-gpu-rpc-service"

echo "--- 正在构建 Docker 镜像: $IMAGE_NAME ---"
# -t: 为镜像打标签
# .: 指定 Dockerfile 所在的上下文路径
docker build -t $IMAGE_NAME .

echo "--- 镜像构建完成。开始运行容器... ---"
# --gpus all: 将所有可用的 GPU 暴露给容器，这是使用 Faiss-GPU 的关键
# --name: 为容器指定一个名称，方便管理
# -p 8000:8000: 将主机的 8000 端口映射到容器的 8000 端口
# -it: 以交互模式运行，方便查看日志
# --rm: 容器退出时自动删除
docker run --gpus all --name faiss-service --rm -it -p 8000:8000 $IMAGE_NAME

echo "--- 容器已停止并删除 ---"
