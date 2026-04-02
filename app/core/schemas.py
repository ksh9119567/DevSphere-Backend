from pydantic.generics import GenericModel
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class StandardResponse(GenericModel, Generic[T]):
    message: str
    data: Optional[T]
    status: str
    