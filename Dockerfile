# Janavani canonical web/API runtime image
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

# General Janavani API deployments use the canonical assembly directly.
# Channel processes remain independently deployable and are not started here.
CMD ["uvicorn", "src.web.canonical_app:app", "--host", "0.0.0.0", "--port", "8000"]
