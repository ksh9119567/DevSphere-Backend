import logging
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc

from .models import ActivityLog
from .schemas import ActivityLogResponse, ActivityLogCreate

logger = logging.getLogger(__name__)


class ActivityService:
    @staticmethod
    async def log_activity(request: ActivityLogCreate, 
                           db: AsyncSession) -> ActivityLog:
        """Log user activity to database"""
        try:
            activity = ActivityLog(
                user_email=request.user_email, endpoint=request.endpoint, method=request.method,
                status_code=request.status_code, ip_address=request.ip_address, user_agent=request.user_agent,
                request_body=request.request_body, response_body=request.response_body, 
                response_time_ms=request.response_time_ms, action_description=request.action_description,
                error_message=request.error_message,
            )
            db.add(activity)
            await db.commit()
            await db.refresh(activity)
            logger.info(
                f"Activity logged: user_email={request.user_email}, endpoint={request.endpoint}, "
                f"method={request.method}, status_code={request.status_code}, response_time={request.response_time_ms}ms"
            )
            return activity
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
            await db.rollback()
            raise

    @staticmethod
    async def get_all_activities(db: AsyncSession, 
                                 limit: int = 100, 
                                 offset: int = 0) -> List[ActivityLogResponse]:
        """Get all activities with pagination"""
        try:
            query = select(ActivityLog).order_by(desc(ActivityLog.timestamp)).limit(limit).offset(offset)
            result = await db.execute(query)
            activities = result.scalars().all()
            logger.info(f"Retrieved {len(activities)} activities")
            return activities
        except Exception as e:
            logger.error(f"Failed to retrieve activities: {str(e)}")
            raise

    @staticmethod
    async def get_user_activities(db: AsyncSession, 
                                  user_email: str, 
                                  limit: int = 100, 
                                  offset: int = 0) -> List[ActivityLogResponse]:
        """Get activities for a specific user"""
        try:
            query = (
                select(ActivityLog).where(ActivityLog.user_email == user_email)
                .order_by(desc(ActivityLog.timestamp)).limit(limit).offset(offset)
            )
            result = await db.execute(query)
            activities = result.scalars().all()
            logger.info(f"Retrieved {len(activities)} activities for user_email={user_email}")
            return activities
        except Exception as e:
            logger.error(f"Failed to retrieve user activities: {str(e)}")
            raise

    @staticmethod
    async def get_endpoint_activities(db: AsyncSession,
                                      endpoint: str,
                                      limit: int = 100,
                                      offset: int = 0) -> List[ActivityLogResponse]:
        """Get activities for a specific endpoint"""
        try:
            query = (
                select(ActivityLog).where(ActivityLog.endpoint == endpoint)
                .order_by(desc(ActivityLog.timestamp)).limit(limit).offset(offset)
            )
            result = await db.execute(query)
            activities = result.scalars().all()
            logger.info(f"Retrieved {len(activities)} activities for endpoint={endpoint}")
            return activities
        except Exception as e:
            logger.error(f"Failed to retrieve endpoint activities: {str(e)}")
            raise

    @staticmethod
    async def get_filtered_activities(db: AsyncSession,
                                      user_email: Optional[str] = None,
                                      endpoint: Optional[str] = None,
                                      method: Optional[str] = None,
                                      status_code: Optional[int] = None,
                                      start_date: Optional[datetime] = None,
                                      end_date: Optional[datetime] = None,
                                      limit: int = 100,
                                      offset: int = 0) -> List[ActivityLogResponse]:
        """Get activities with multiple filters"""
        try:
            filters = []
            
            if user_email is not None:
                filters.append(ActivityLog.user_email == user_email)
            if endpoint is not None:
                filters.append(ActivityLog.endpoint == endpoint)
            if method is not None:
                filters.append(ActivityLog.method == method)
            if status_code is not None:
                filters.append(ActivityLog.status_code == status_code)
            if start_date is not None:
                filters.append(ActivityLog.timestamp >= start_date)
            if end_date is not None:
                filters.append(ActivityLog.timestamp <= end_date)

            query = select(ActivityLog)
            if filters:
                query = query.where(and_(*filters))
            
            query = query.order_by(desc(ActivityLog.timestamp)).limit(limit).offset(offset)
            result = await db.execute(query)
            activities = result.scalars().all()
            logger.info(f"Retrieved {len(activities)} filtered activities")
            return activities
        except Exception as e:
            logger.error(f"Failed to retrieve filtered activities: {str(e)}")
            raise

    @staticmethod
    async def get_activity_stats(db: AsyncSession) -> dict:
        """Get activity statistics"""
        try:
            # Total activities
            total_query = select(ActivityLog)
            total_result = await db.execute(total_query)
            total_activities = len(total_result.scalars().all())

            # Activities by status code
            status_query = select(ActivityLog.status_code)
            status_result = await db.execute(status_query)
            status_codes = status_result.scalars().all()
            status_distribution = {}
            for code in status_codes:
                status_distribution[code] = status_distribution.get(code, 0) + 1

            logger.info(f"Activity stats: total={total_activities}, status_distribution={status_distribution}")
            return {
                "total_activities": total_activities,
                "status_distribution": status_distribution,
            }
        except Exception as e:
            logger.error(f"Failed to retrieve activity stats: {str(e)}")
            raise
