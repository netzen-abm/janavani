# Use a highly secure, minimized slim python container layer baseline
FROM python:3.11-slim

# Enforce direct write-to-terminal outputs without stream buffering delays
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /workspace

# Install underlying operating system dependencies safely
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency mappings across layer borders
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bring repository codebase modules under internal scope boundaries
COPY src/ ./src/

EXPOSE 8000

# Execute server bound with production Uvicorn configurations
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000"]


# -----------------------------

# Simple Dockerfile for running the POC (not optimized for large models)
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "api.agent_api:app", "--host", "0.0.0.0", "--port", "8000"]
