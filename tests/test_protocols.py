"""Unit tests for shared protocols"""
from src.shared.protocols.api import (
    TaskCreateRequest,
    TaskResponse,
    AlgorithmInfo,
    TaskType,
    AlgorithmStatus,
)


def test_task_create_request():
    """Test TaskCreateRequest validation."""
    request = TaskCreateRequest(
        algorithm_id="test-algo",
        input_data={"image": "base64..."},
        priority=50,
    )
    assert request.algorithm_id == "test-algo"
    assert request.priority == 50


def test_task_response():
    """Test TaskResponse model."""
    response = TaskResponse(
        task_id="task_123",
        status="pending",
        task_type="image_classification",
        algorithm_id="test-algo",
        progress=0,
    )
    assert response.task_id == "task_123"
    assert response.status == "pending"


def test_algorithm_info():
    """Test AlgorithmInfo model."""
    algo = AlgorithmInfo(
        id="test-algo",
        name="Test Algorithm",
        version="1.0.0",
        description="A test algorithm",
        task_type=TaskType.OBJECT_DETECTION,
        status=AlgorithmStatus.AVAILABLE,
        gpu_required=False,
    )
    assert algo.id == "test-algo"
    assert algo.gpu_required is False


def test_task_type_enum():
    """Test TaskType enum values."""
    assert TaskType.IMAGE_CLASSIFICATION.value == "image_classification"
    assert TaskType.OBJECT_DETECTION.value == "object_detection"
