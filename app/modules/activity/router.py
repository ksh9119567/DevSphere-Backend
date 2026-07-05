import logging
import uuid

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.core.security import get_current_admin_user, get_current_user
from app.core.exception import PermissionDeniedException
from app.core.response import success_response

from .service import ActivityService
from .dependency import get_activity_service
from .schemas import ActivityLogResponse

router = APIRouter(prefix="/activities", tags=["Activity Tracking"])
logger = logging.getLogger(__name__)


def convert_activity_to_dict(activity) -> dict:
    """Convert ActivityLog ORM object to dictionary for Pydantic serialization."""
    return {
        'id': activity.id,
        'user_email': activity.user_email,
        'endpoint': activity.endpoint,
        'method': activity.method,
        'status_code': activity.status_code,
        'ip_address': activity.ip_address,
        'user_agent': activity.user_agent,
        'response_time_ms': activity.response_time_ms,
        'timestamp': activity.timestamp,
        'action_description': activity.action_description,
        'error_message': activity.error_message,
    }


@router.get("/all", response_model=List[ActivityLogResponse])
async def get_all_activities(limit: int = Query(100, ge=1, le=1000),
                             offset: int = Query(0, ge=0),
                             activity_service: ActivityService = Depends(get_activity_service),
                             admin_user: User = Depends(get_current_admin_user)):
    """Get all activities (Admin only)"""
    logger.info(f"Admin {admin_user.email} is fetching all activities with limit={limit}, offset={offset}")
    activities = await activity_service.get_all_activities(limit=limit, offset=offset)
    return [ActivityLogResponse.model_validate(convert_activity_to_dict(activity)) for activity in activities]


@router.get("/user/", response_model=List[ActivityLogResponse])
async def get_user_activities(user_email: str = Query(..., description="Email of the user to filter by"),
                              limit: int = Query(100, ge=1, le=1000),
                              offset: int = Query(0, ge=0),
                              activity_service: ActivityService = Depends(get_activity_service),
                              current_user: User = Depends(get_current_user)):
    """Get activities for a specific user (User can view own, Admin can view any)"""
    if current_user.email != user_email and not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted unauthorized access to user {user_email} activities")
        raise PermissionDeniedException("You can only view your own activities")
    
    logger.info(f"User {current_user.email} is fetching activities for user_email={user_email}")
    activities = await activity_service.get_user_activities(user_email=user_email, limit=limit, offset=offset)
    return [ActivityLogResponse.model_validate(convert_activity_to_dict(activity)) for activity in activities]


@router.get("/endpoint", response_model=List[ActivityLogResponse])
async def get_endpoint_activities(endpoint: str = Query(..., description="Endpoint path to filter by"),
                                  limit: int = Query(100, ge=1, le=1000),
                                  offset: int = Query(0, ge=0),
                                  activity_service: ActivityService = Depends(get_activity_service),
                                  admin_user: User = Depends(get_current_admin_user)):
    """Get activities for a specific endpoint (Admin only)"""
    logger.info(f"Admin {admin_user.email} is fetching activities for endpoint={endpoint}")
    activities = await activity_service.get_endpoint_activities(endpoint=endpoint, limit=limit, offset=offset)
    return [ActivityLogResponse.model_validate(convert_activity_to_dict(activity)) for activity in activities]


@router.get("/filter", response_model=List[ActivityLogResponse])
async def get_filtered_activities(user_email: Optional[str] = Query(None),
                                  endpoint: Optional[str] = Query(None),
                                  method: Optional[str] = Query(None),
                                  status_code: Optional[int] = Query(None),
                                  start_date: Optional[datetime] = Query(None),
                                  end_date: Optional[datetime] = Query(None),
                                  limit: int = Query(100, ge=1, le=1000),
                                  offset: int = Query(0, ge=0),
                                  activity_service: ActivityService = Depends(get_activity_service),
                                  admin_user: User = Depends(get_current_admin_user)):
    """Get filtered activities (Admin only)"""
    logger.info(
        f"Admin {admin_user.email} is fetching filtered activities: "
        f"user_email={user_email}, endpoint={endpoint}, method={method}, status_code={status_code}"
    )
    activities = await activity_service.get_filtered_activities(
        user_email=user_email, endpoint=endpoint, method=method, status_code=status_code, start_date=start_date,
        end_date=end_date, limit=limit, offset=offset,
    )
    return [ActivityLogResponse.model_validate(convert_activity_to_dict(activity)) for activity in activities]


@router.get("/stats", response_model=dict)
async def get_activity_stats(activity_service: ActivityService = Depends(get_activity_service),
                             admin_user: User = Depends(get_current_admin_user)):
    """Get activity statistics (Admin only)"""
    logger.info(f"Admin {admin_user.email} is fetching activity statistics")
    stats = await activity_service.get_activity_stats()
    return success_response("Activity statistics retrieved successfully", stats)
