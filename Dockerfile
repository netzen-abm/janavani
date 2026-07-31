FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for weasyprint PDF generation
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libgdk-pixbuf-xlib-2.0-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY .

# Run the bot
CMD ["python", "-m", "src.bot_telegram"]
