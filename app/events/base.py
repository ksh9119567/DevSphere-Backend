from datetime import datetime
from uuid import uuid4


class BaseEvent:
    def __init__(self):
        self.event_id = str(uuid4())
        self.created_at = datetime.utcnow()

    @property
    def event_name(self) -> str:
        return self.__class__.__name__