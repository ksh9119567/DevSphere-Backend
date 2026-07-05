from pydantic.generics import GenericModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')


class StandardResponse(GenericModel, Generic[T]):
    """
    Standardized API response wrapper for consistent response format across the application.
    """
    message: str
    data: Optional[T]
    status: str
    