from typing import Union
import uuid
from app.events.base import BaseEvent


class EmailOTPRequestedEvent(BaseEvent):
    def __init__(self, email: str, otp: str):
        super().__init__()
        self.email = email
        self.otp = otp


class UserRegisteredEvent(BaseEvent):
    def __init__(self, email: str, user_id: Union[str, uuid.UUID] = None):
        super().__init__()
        self.email = email
        self.user_id = user_id


class UserUpdatedEvent(BaseEvent):
    def __init__(self, user_id: Union[str, uuid.UUID], email: str = None):
        super().__init__()
        self.user_id = user_id
        self.email = email


class UserDeletedEvent(BaseEvent):
    def __init__(self, user_id: Union[str, uuid.UUID], email: str = None):
        super().__init__()
        self.user_id = user_id
        self.email = email