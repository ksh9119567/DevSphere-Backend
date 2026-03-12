import logging
import uuid

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.modules.users.models import User
from app.core.security import get_current_admin_user, get_current_user
from app.core.exception import PermissionDeniedException

from .service import ActivityService
from .schemas import ActivityLogResponse

router = APIRouter(prefix="/activities", tags=["Activity Tracking"])
logger = logging.getLogger(__name__)


@router.get("/all", response_model=List[ActivityLogResponse])
async def get_all_activities(limit: int = Query(100, ge=1, le=1000),
                             offset: int = Query(0, ge=0),
                             db: AsyncSession = Depends(get_db),
                             admin_user: User = Depends(get_current_admin_user)):
    """Get all activities (Admin only)"""
    logger.info(f"Admin {admin_user.email} is fetching all activities with limit={limit}, offset={offset}")
    activities = await ActivityService.get_all_activities(db, limit=limit, offset=offset)
    return activities


@router.get("/user/", response_model=List[ActivityLogResponse])
async def get_user_activities(user_email: str = Query(..., description="Email of the user to filter by"),
                              limit: int = Query(100, ge=1, le=1000),
                              offset: int = Query(0, ge=0),
                              db: AsyncSession = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    """Get activities for a specific user (User can view own, Admin can view any)"""
    if current_user.email != user_email and not current_user.is_admin:
        logger.warning(f"User {current_user.email} attempted unauthorized access to user {user_email} activities")
        raise PermissionDeniedException("You can only view your own activities")
    
    logger.info(f"User {current_user.email} is fetching activities for user_email={user_email}")
    activities = await ActivityService.get_user_activities(db, user_email=user_email, limit=limit, offset=offset)
    return activities


@router.get("/endpoint", response_model=List[ActivityLogResponse])
async def get_endpoint_activities(endpoint: str = Query(..., description="Endpoint path to filter by"),
                                  limit: int = Query(100, ge=1, le=1000),
                                  offset: int = Query(0, ge=0),
                                  db: AsyncSession = Depends(get_db),
                                  admin_user: User = Depends(get_current_admin_user)):
    """Get activities for a specific endpoint (Admin only)"""
    logger.info(f"Admin {admin_user.email} is fetching activities for endpoint={endpoint}")
    activities = await ActivityService.get_endpoint_activities(db, endpoint=endpoint, limit=limit, offset=offset)
    return activities


@router.get("/filter", response_model=List[ActivityLogResponse])
async def get_filtered_activities(user_email: Optional[str] = Query(None),
                                  endpoint: Optional[str] = Query(None),
                                  method: Optional[str] = Query(None),
                                  status_code: Optional[int] = Query(None),
                                  start_date: Optional[datetime] = Query(None),
                                  end_date: Optional[datetime] = Query(None),
                                  limit: int = Query(100, ge=1, le=1000),
                                  offset: int = Query(0, ge=0),
                                  db: AsyncSession = Depends(get_db),
                                  admin_user: User = Depends(get_current_admin_user)):
    """Get filtered activities (Admin only)"""
    logger.info(
        f"Admin {admin_user.email} is fetching filtered activities: "
        f"user_email={user_email}, endpoint={endpoint}, method={method}, status_code={status_code}"
    )
    activities = await ActivityService.get_filtered_activities(
        db, user_email=user_email, endpoint=endpoint, method=method, status_code=status_code, start_date=start_date,
        end_date=end_date, limit=limit,offset=offset,
    )
    return activities


@router.get("/stats", response_model=dict)
async def get_activity_stats(db: AsyncSession = Depends(get_db),
                             admin_user: User = Depends(get_current_admin_user)):
    """Get activity statistics (Admin only)"""
    logger.info(f"Admin {admin_user.email} is fetching activity statistics")
    stats = await ActivityService.get_activity_stats(db)
    return stats
