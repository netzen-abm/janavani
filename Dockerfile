FROM python:3.11-slim

WORKDIR /app

# Install system deps for weasyprint PDF
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libgdk-pixbuf2.0-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY .

CMD ["python", "-m", "src.bot_telegram"]
