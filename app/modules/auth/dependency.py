from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .service import AuthService

from app.db.database import get_db


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)
