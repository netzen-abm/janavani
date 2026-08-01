# Use a slim Python image
FROM python:3.11-slim

# Simple cache-bust arg to force rebuild when updated
ARG CACHEBUST=2026-08-01T16:25:00Z

# Avoid buffering (helps logs stream)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Minimal system deps and native libraries needed by weasyprint
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libcairo2 \
      libpango-1.0-0 \
      libgdk-pixbuf-xlib-2.0-0 \
      libffi-dev \
      shared-mime-info && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps first for better caching
COPY ["requirements.txt", "."]
# Echo the cachebust value so changing it invalidates the layer cache
RUN echo "CACHEBUST=$CACHEBUST"
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh || true

# Start the entrypoint which launches bot (background) + health web server (foreground)
CMD ["/app/entrypoint.sh"]
