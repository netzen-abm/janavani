# Use a slim Python image
FROM python:3.11-slim

# Avoid buffering (helps logs stream)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Minimal system deps for packages that may need compilation
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first for better caching
COPY ["requirements.txt", "."]
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh || true

# Start the entrypoint which launches bot (background) + health web server (foreground)
CMD ["/app/entrypoint.sh"]
