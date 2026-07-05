from pydantic import BaseModel
from app.core.celery import celery


class TaskResponse(BaseModel):
    """Response model for async celery tasks."""
    task_id: str
    message: str = "Task queued successfully"

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123def456",
                "message": "Task queued successfully"
            }
        }


class TaskStatusResponse(BaseModel):
    """Response model for task status."""
    task_id: str
    status: str  # PENDING, STARTED, SUCCESS, FAILURE, RETRY
    result: dict | None = None
    error: str | None = None

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "abc123def456",
                "status": "SUCCESS",
                "result": None,
                "error": None
            }
        }


def get_task_status(task_id: str) -> TaskStatusResponse:
    """Get the status of a celery task by ID."""
    task_result = celery.AsyncResult(task_id)
    
    status = task_result.status
    result = None
    error = None
    
    if status == 'SUCCESS':
        result = task_result.result
    elif status == 'FAILURE':
        error = str(task_result.info)
    
    return TaskStatusResponse(
        task_id=task_id,
        status=status,
        result=result,
        error=error
    )

