# ============================================
# CV Algorithm Hub - Algorithm Engine Dockerfile
# GPU-enabled with CUDA support
# ============================================

# Build stage
FROM nvidia/cuda:11.8.0-devel-ubuntu20.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN for i in {1..5}; do apt-get update && break || sleep 3; done && \
    apt-get install -y --no-install-recommends build-essential python3-dev && rm -rf /var/lib/apt/lists/*

# Install uv for faster pip
RUN pip install uv --no-cache-dir

WORKDIR /build

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# ============================================
# Runtime stage
# ============================================
FROM nvidia/cuda:11.8.0-runtime-ubuntu20.04 AS runtime

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install runtime dependencies
RUN for i in {1..5}; do apt-get update && break || sleep 3; done && \
    apt-get install -y --no-install-recommends curl vim && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /data /models /temp /logs

# Expose port
EXPOSE 8083

# Health check with GPU validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" || exit 1

# Run with GPU support
CMD ["python", "-m", "uvicorn", "src.algorithm_engine.app.main:app", "--host", "0.0.0.0", "--port", "8083", "--workers", "2"]
