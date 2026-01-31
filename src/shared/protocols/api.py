"""Protocol definitions - 协议定义模块"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class TaskType(str, Enum):
    """Task type enumeration"""
    IMAGE_CLASSIFICATION = "image_classification"
    OBJECT_DETECTION = "object_detection"
    SEMANTIC_SEGMENTATION = "semantic_segmentation"
    INSTANCE_SEGMENTATION = "instance_segmentation"
    CUSTOM = "custom"


class AlgorithmStatus(str, Enum):
    """Algorithm status"""
    AVAILABLE = "available"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class TaskCreateRequest(BaseModel):
    """Task creation request"""
    algorithm_id: str = Field(..., description="Algorithm identifier")
    input_data: Dict[str, Any] = Field(..., description="Input data for the algorithm")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Algorithm parameters")
    priority: int = Field(default=0, ge=0, le=100, description="Task priority")
    callback_url: Optional[str] = Field(default=None, description="Callback URL for completion notification")


class TaskResponse(BaseModel):
    """Task response"""
    task_id: str
    status: str
    task_type: str
    algorithm_id: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: int = Field(default=0, ge=0, le=100)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class AlgorithmInfo(BaseModel):
    """Algorithm information"""
    id: str
    name: str
    version: str
    description: str
    task_type: TaskType
    status: AlgorithmStatus
    parameters: Dict[str, Any] = Field(default_factory=dict)
    requirements: List[str] = Field(default_factory=list)
    gpu_required: bool = False
    gpu_memory_mb: int = 0
    average_execution_time_ms: int = 0


class AlgorithmCreateRequest(BaseModel):
    """Algorithm registration request"""
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    description: str = Field(..., max_length=1000)
    task_type: TaskType
    entry_point: str = Field(..., description="Python entry point module:function")
    parameters: Optional[Dict[str, Any]] = None
    requirements: List[str] = Field(default_factory=list)
    gpu_required: bool = False
    gpu_memory_mb: int = 0


class AlgorithmRegisterResponse(BaseModel):
    """Algorithm registration response"""
    algorithm_id: str
    name: str
    version: str
    status: AlgorithmStatus
    created_at: datetime


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime
    components: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
