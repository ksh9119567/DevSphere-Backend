from collections import defaultdict
from typing import Callable, Dict, List, Type
from app.events.base import BaseEvent


class EventRegistry:
    def __init__(self):
        self._handlers: Dict[Type[BaseEvent], List[Callable]] = defaultdict(list)

    def register(self, event_type: Type[BaseEvent], handler: Callable):
        self._handlers[event_type].append(handler)

    def get_handlers(self, event: BaseEvent):
        return self._handlers.get(type(event), [])