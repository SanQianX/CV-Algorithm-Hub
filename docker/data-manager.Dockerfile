# ============================================
# CV Algorithm Hub - Data Manager Dockerfile
# ============================================

FROM python:3.10-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN for i in {1..5}; do apt-get update && break || sleep 3; done && \
    apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8084

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8084/health || exit 1

CMD ["uvicorn", "src.data_manager.app.main:app", "--host", "0.0.0.0", "--port", "8084", "--workers", "2"]
