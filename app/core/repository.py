import logging

from typing import Any, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from sqlalchemy.engine import Result
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class BaseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(
            self, query: Select
        ) -> Result:
        
        """Execute a SQLAlchemy query."""
        return await self.db.execute(query)

    async def get_one(
            self, query: Select
        ) -> Optional[Any]:
        
        """Return single record or None."""
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(
            self, query: Select
        ) -> Sequence[Any]:
        
        """Return list of records."""
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(
            self, obj: Any
        ) -> Any:
        
        """Create a new record with transaction management."""
        try:
            self.db.add(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error creating record: {str(e)}")
            raise

    async def update(
            self, obj: Any
        ) -> Any:
        
        """Update existing record with transaction management."""
        try:
            await self.db.merge(obj)
            await self.db.commit()
            await self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error updating record: {str(e)}")
            raise

    async def soft_delete(
            self, obj: Any, fields: dict
        ) -> None:
        
        """
        Soft delete by updating provided fields with transaction management.
        Example: {"is_deleted": True}
        """
        try:
            for key, value in fields.items():
                setattr(obj, key, value)

            await self.db.merge(obj)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error soft deleting record: {str(e)}")
            raise
        
    async def delete(
            self, obj: Any
        ) -> None:
        
        """Hard delete a record with transaction management."""
        try:
            await self.db.delete(obj)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Error deleting record: {str(e)}")
            raise