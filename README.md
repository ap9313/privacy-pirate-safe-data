# Safe-Data

**Safe-Data** is a high-performance microservice designed to anonymize sensitive information across various formats, including images, PDFs, text, and structured data. By transforming raw input into privacy-preserving vectors, it enables the secure integration of sensitive data into recommendation systems and downstream AI pipelines.


## 🚀 Quick Start

### 1. Prerequisites

Ensure you have the following installed on your system:

* **Python (3.11.14)** --» (most stable for ML)
* **Node (v25.5.0)**
* **Docker & Docker Compose**
* **Poetry** (for local backend development)
* **Ollama** (for local LLM and Embedding support)

### 2. Ollama Configuration

Safe-Data leverages local AI models via Ollama. Follow these steps to initialize the environment:

**Step A: Environment Setup**
To optimize performance, especially when using a GPU, set the following environment variables:

```bash
# Keep the model in memory indefinitely
export OLLAMA_KEEP_ALIVE=-1

# Enable GPU acceleration (Recommended)
export OLLAMA_NUM_GPU=1

```

*Note: Ensure no other Ollama instances are running before starting the server (`pgrep ollama | xargs kill -9`).*

**Step B: Start Server & Pull Models**
Open a terminal and launch the server:

```bash
ollama serve

```

In a separate terminal, download the required models:

```bash
ollama pull llama3.2-vision
ollama pull nomic-embed-text

```

---

## 🛠️ Installation & Setup

### ML Model Initialization

We use **GLiNER** for Named Entity Recognition (NER) and **YuNet** for face detection. Download these artifacts using the provided helper script:

```bash
cd backend
poetry install
poetry run python download_models.py

```

### Running the Full Stack

Deploy the entire ecosystem using Docker Compose:

```bash
docker-compose up --build

```

---

## 🌐 Service Overview

Once the containers are active, you can access the following endpoints:

| Service | URL |
| --- | --- |
| **Frontend** | `http://localhost:3000` |
| **Backend** | `http://localhost:8000` |

---

Note: The first run might be slow on the PDF and on the image anonimisation. The ollama has to load the model first.

## 🛑 Termination

To stop all running services and clean up containers:

```bash
docker-compose down

```