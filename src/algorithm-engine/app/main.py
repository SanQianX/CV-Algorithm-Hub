"""Algorithm Engine - Main Application"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Algorithm Engine starting...")
    gpu_enabled = os.getenv("CVHUB_GPU_ENABLED", "false")
    logger.info(f"GPU enabled: {gpu_enabled}")
    yield
    logger.info("Algorithm Engine shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="CV Algorithm Hub Algorithm Engine",
        description="GPU-enabled Algorithm Execution Service",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health():
        """Health check endpoint with GPU validation"""
        import torch
        gpu_available = torch.cuda.is_available()
        gpu_count = torch.cuda.device_count() if gpu_available else 0
        return {
            "status": "healthy",
            "service": "algorithm-engine",
            "gpu_available": gpu_available,
            "gpu_count": gpu_count
        }

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "service": "algorithm-engine",
            "version": "1.0.0",
            "gpu_enabled": os.getenv("CVHUB_GPU_ENABLED", "false")
        }

    return app


# Create default app instance
app = create_app()
