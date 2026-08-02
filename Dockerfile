# Simple Dockerfile for running the POC (not optimized for large models)
FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
EXPOSE 8000
CMD ["uvicorn", "api.agent_api:app", "--host", "0.0.0.0", "--port", "8000"]
