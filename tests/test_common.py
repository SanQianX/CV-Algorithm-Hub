"""Unit tests for API Gateway"""
import pytest
from src.shared.common.utils import TaskStatus, generate_task_id


def test_task_id_generation():
    """Test task ID generation."""
    task_id = generate_task_id()
    assert task_id.startswith("task_")
    assert len(task_id) == 21  # "task_" + 16 hex chars


def test_task_status_enum():
    """Test TaskStatus enum values."""
    assert TaskStatus.PENDING.value == "pending"
    assert TaskStatus.RUNNING.value == "running"
    assert TaskStatus.COMPLETED.value == "completed"
    assert TaskStatus.FAILED.value == "failed"
    assert TaskStatus.CANCELLED.value == "cancelled"


def test_settings_default_values():
    """Test Settings default values."""
    from src.shared.common.config import Settings

    settings = Settings()
    assert settings.app_name == "CV Algorithm Hub"
    assert settings.environment == "development"
    assert settings.database.host == "localhost"
