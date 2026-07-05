"""
Standardized API response wrapper for consistent response format across the application.

Response format:
{
    "message": "Success message",
    "data": {...},
    "status": "success|error",
    "task_id": "optional-task-id"
}
"""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict


class ApiResponse(BaseModel):
    """Standard API response wrapper for all endpoints."""
    message: str
    data: Any = None
    status: str  # "success" or "error"
    task_id: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "message": "Operation completed successfully",
            "data": {"id": "123", "name": "Example"},
            "status": "success",
            "task_id": None
        }
    })


def success_response(
        message: str,
        data: Any = None,
    ) -> dict:
    
    """
    Create a success response.
    
    Args:
        message: Success message
        data: Response data (can be any type)
    
    Returns:
        Dictionary with standardized response format
    """
    return {
        "message": message,
        "data": data,
        "status": "success",
    }


def error_response(
        message: str,
        data: Any = None,
        task_id: Optional[str] = None
    ) -> dict:
    """
    Create an error response.
    
    Args:
        message: Error message
        data: Additional error details (optional)
        task_id: Optional async task ID
    
    Returns:
        Dictionary with standardized response format
    """
    return {
        "message": message,
        "data": data,
        "status": "error",
        "task_id": task_id
    }
