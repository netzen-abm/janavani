FROM ghcr.io/weasyprint/weasyprint:63.1

WORKDIR /app

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all code
COPY .

# Run the bot
CMD ["python3", "-m", "src.bot_telegram"]
