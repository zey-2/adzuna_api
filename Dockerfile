# Use official Python runtime as base image
FROM python:3.13-slim

# Set working directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt /code/requirements.txt

# Install Python dependencies (production only)
RUN pip install --no-cache-dir --upgrade \
    fastapi>=0.115.0 \
    fastapi-mcp>=0.4.0 \
    uvicorn>=0.32.0 \
    requests>=2.32.0 \
    pydantic>=2.0.0

# Copy application code
COPY server.py /code/server.py
COPY adzuna_example.py /code/adzuna_example.py
COPY README.md /code/README.md

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /code
USER appuser

# Cloud Run sets PORT environment variable
# Use exec form for proper signal handling
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-7000}"]
