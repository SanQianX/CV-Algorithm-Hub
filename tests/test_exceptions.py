"""Unit tests for shared exceptions"""
import pytest
from src.shared.common.exceptions import (
    CVHubException,
    ValidationError,
    NotFoundError,
    AuthenticationError,
    TaskError,
)


def test_cvhub_exception():
    """Test base exception."""
    exc = CVHubException("Test error", code="TEST_ERROR")
    assert exc.message == "Test error"
    assert exc.code == "TEST_ERROR"


def test_validation_error():
    """Test ValidationError."""
    exc = ValidationError("Invalid input", field="name")
    assert exc.code == "VALIDATION_ERROR"
    assert exc.details["field"] == "name"


def test_not_found_error():
    """Test NotFoundError."""
    exc = NotFoundError("User", "123")
    assert exc.code == "NOT_FOUND"
    assert exc.details["resource_type"] == "User"
    assert exc.details["resource_id"] == "123"


def test_authentication_error():
    """Test AuthenticationError."""
    exc = AuthenticationError()
    assert exc.code == "AUTHENTICATION_ERROR"


def test_task_error():
    """Test TaskError."""
    exc = TaskError("task_123", "Execution failed")
    assert exc.code == "TASK_ERROR"
    assert exc.details["task_id"] == "task_123"
