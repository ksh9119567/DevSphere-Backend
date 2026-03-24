import asyncio
from app.events.base import BaseEvent
from app.events.registry import EventRegistry


class EventDispatcher:
    def __init__(self, registry: EventRegistry):
        self.registry = registry

    async def dispatch(self, event: BaseEvent) -> list | None:
        """Dispatch event to all registered handlers and return results."""
        handlers = self.registry.get_handlers(event)

        if not handlers:
            return None

        tasks = []
        for handler in handlers:
            if asyncio.iscoroutinefunction(handler):
                tasks.append(handler(event))
            else:
                # sync handler fallback
                loop = asyncio.get_event_loop()
                tasks.append(loop.run_in_executor(None, handler, event))

        results = await asyncio.gather(*tasks)
        return results