import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exception import NotFoundException


class BaseService:
    """
    Base service providing common helper utilities for all services.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    async def get_or_404(self, entity: Any, resource_name: str):
        """
        Utility method to validate entity existence.
        """
        if not entity:
            self.logger.warning(f"{resource_name} not found")
            raise NotFoundException(resource_name)
        return entity