# ====================================
# CV Algorithm Hub - API Gateway Dockerfile
# ====================================

# Base image
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create working directory
WORKDIR /app

# Copy requirements first for better caching
COPY src/api_gateway/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8080

# Run the application - use the correct module path
CMD ["uvicorn", "src.api_gateway.app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
