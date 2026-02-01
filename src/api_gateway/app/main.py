"""API Gateway - Main Application"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.shared.common.config import settings
from src.api_gateway.routes.auth import router as auth_router
from src.api_gateway.routes.monitor import router as monitor_router
from src.api_gateway.routes.db_manager import router as db_manager_router
from src.api_gateway.routes.finance import router as finance_router
from src.api_gateway.routes.finance_manager import router as finance_manager_router
from src.api_gateway.routes.user_manager import router as user_manager_router
from src.api_gateway.routes.data_explorer import router as data_explorer_router
from src.api_gateway.db.database import init_db

# Import models to register them with Base.metadata
from src.api_gateway.db.models import FundHistory, StockHistory, FundDetail, MonitorList, MonitorItem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    yield
    # Shutdown


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="CV Algorithm Hub API Gateway",
        description="Unified API Gateway for CV Algorithm Hub",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(monitor_router)
    app.include_router(db_manager_router)
    app.include_router(finance_router)
    app.include_router(finance_manager_router)
    app.include_router(user_manager_router)
    app.include_router(data_explorer_router)

    return app


# Create default app instance
app = create_app()
