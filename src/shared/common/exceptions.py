"""Shared Exceptions - 共享异常定义"""
from typing import Optional


class CVHubException(Exception):
    """Base exception for CV Algorithm Hub"""

    def __init__(self, message: str, code: str = "INTERNAL_ERROR", details: Optional[dict] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(CVHubException):
    """Validation error"""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, code="VALIDATION_ERROR", details=details)


class NotFoundError(CVHubException):
    """Resource not found error"""

    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            f"{resource_type} with id '{resource_id}' not found",
            code="NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class AuthenticationError(CVHubException):
    """Authentication error"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, code="AUTHENTICATION_ERROR")


class AuthorizationError(CVHubException):
    """Authorization error"""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message, code="AUTHORIZATION_ERROR")


class TaskError(CVHubException):
    """Task execution error"""

    def __init__(self, task_id: str, message: str):
        super().__init__(
            message,
            code="TASK_ERROR",
            details={"task_id": task_id}
        )


class GPUError(CVHubException):
    """GPU related error"""

    def __init__(self, message: str):
        super().__init__(message, code="GPU_ERROR")


class TimeoutError(CVHubException):
    """Timeout error"""

    def __init__(self, operation: str, timeout: int):
        super().__init__(
            f"Operation '{operation}' timed out after {timeout} seconds",
            code="TIMEOUT"
        )
