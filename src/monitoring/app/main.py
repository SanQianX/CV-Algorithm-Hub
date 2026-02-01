"""Monitoring - Main Application"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    logger.info("Monitoring service starting...")
    yield
    logger.info("Monitoring service shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="CV Algorithm Hub Monitoring",
        description="Monitoring & Analysis Service",
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
        """Health check endpoint"""
        return {"status": "healthy", "service": "monitoring"}

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {"service": "monitoring", "version": "1.0.0"}

    return app


# Create default app instance
app = create_app()
