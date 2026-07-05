from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import ActivityService

from app.db.database import get_db


def get_activity_service(db: AsyncSession = Depends(get_db)) -> ActivityService:
    return ActivityService(db)
