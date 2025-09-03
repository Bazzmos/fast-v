# fast-v  Vector Search Service

This project implements a high-performance vector search and storage service using **Faiss-GPU**, built on an efficient **MessagePack RPC** protocol. The service is designed to handle a dynamically changing vector database with real-time updates and lightning-fast search capabilities, leveraging the power of an NVIDIA GPU.

## Key Features

* **High-Performance Search**: Utilizes Faiss-GPU to perform near-instantaneous similarity search on a large-scale vector database.

* **Efficient Communication**: Employs the compact and fast MessagePack RPC protocol for binary data serialization, minimizing network overhead.

* **Dynamic Vector Management**: A robust architecture allows for real-time vector additions and scheduled database updates without interrupting the search service.

* **Data Persistence**: The service persists the vector database to disk, ensuring data is not lost upon a restart.

* **Automated CI/CD**: A GitHub Actions workflow automates the building and pushing of a Docker image, ensuring a consistent and up-to-date deployment.

* **Containerized Deployment**: The entire application is packaged in a Docker container for easy, portable, and reproducible deployment on any machine with an NVIDIA GPU.

## Technologies Used

* **Faiss-GPU**: The core library for vector search acceleration.

* **Python**: The programming language for the service logic.

* **asyncio**: For asynchronous I/O and high concurrency.

* **msgpack**: For efficient binary data serialization.

* **APScheduler**: To manage and schedule background tasks, such as database updates.

* **Docker**: For containerization.

* **GitHub Actions**: For automated continuous integration.

## Getting Started

### Prerequisites

* A machine with an **NVIDIA GPU** (e.g., RTX A5000).

* NVIDIA driver installed.

* **NVIDIA Container Toolkit** for Docker.

* **Docker** installed.

* Python 3.8+

### 1. Build the Docker Image

Navigate to the project root directory and use the provided `build-and-run.sh` script to build the Docker image. This script will automatically use the `Dockerfile` to create the container.

```bash
chmod +x build-and-run.sh
./build-and-run.sh
````

The script will build a Docker image named `faiss-gpu-rpc-service` and start a container.

### 2\. Run the Service

The `build-and-run.sh` script automatically starts the service. If you want to run it again, you can use the following command:

```bash
docker run --gpus all --name faiss-service --rm -it -p 8000:8000 faiss-gpu-rpc-service
```

The service will listen on port `8000`.

### 3\. Client Interaction

You can now interact with the service using a MessagePack RPC client. Here's a simple Python client example to demonstrate how to call the service methods.

```python
# (Code from rpc_client.py)
# ... see rpc_client.py file for the full code
```

This client code demonstrates calling the `search`, `add_vectors`, and `trigger_update` methods.

## API Endpoints (RPC Methods)

The service exposes the following RPC methods:

| Method Name | Parameters | Description |
|---|---|---|
| `search` | `queries: List[List[float]]`, `k: int` | Searches for the `k` nearest neighbors. |
| `add_vectors` | `vectors: List[List[float]]` | Adds a batch of new vectors to the update queue. |
| `trigger_update` | None | Manually triggers a background index rebuild. |

## Continuous Integration

This project is configured with a GitHub Actions workflow to automate the build and push of the Docker image to Docker Hub. This workflow is defined in the `.github/workflows/ci-cd.yml` file.

To use the CI/CD pipeline, ensure you have set up the following GitHub Secrets in your repository settings:

  * `DOCKERHUB_USERNAME`

  * `DOCKERHUB_TOKEN`

The workflow will automatically run on every push and pull request to the `main` branch.



