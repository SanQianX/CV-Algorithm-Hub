"""Common utilities - 通用工具模块"""
import asyncio
import hashlib
import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ResultStatus(str, Enum):
    """Result status enumeration"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"


def generate_task_id() -> str:
    """Generate unique task ID"""
    return f"task_{uuid.uuid4().hex[:16]}"


def generate_request_id() -> str:
    """Generate unique request ID"""
    return f"req_{uuid.uuid4().hex[:16]}"


def calculate_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_timestamp(timestamp: datetime) -> str:
    """Format timestamp to ISO format"""
    return timestamp.isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """Parse ISO format timestamp"""
    return datetime.fromisoformat(timestamp_str)


async def gather_with_concurrency(n: int, *tasks) -> List[Any]:
    """Run tasks with limited concurrency"""
    semaphore = asyncio.Semaphore(n)

    async def sem_task(task):
        async with semaphore:
            return await task

    return await asyncio.gather(*(sem_task(task) for task in))


class Singleton:
    """Singleton metaclass"""
    _instances: Dict[type, Any] = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls, *args, **kwargs)
        return cls._instances[cls]


def setup_logging(
    name: str = "cv_algorithm_hub",
    level: str = "INFO",
    log_file: Optional[str] = None
) -> logging.Logger:
    """Setup logging configuration"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
