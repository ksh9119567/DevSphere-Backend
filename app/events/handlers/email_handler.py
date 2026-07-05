import logging

from app.events.events.user_events import (
    EmailOTPRequestedEvent
)
from app.tasks.email_task import (
    send_email_otp_task
)

logger = logging.getLogger(__name__)


def handle_email_otp(event: EmailOTPRequestedEvent) -> dict:
    """Handle OTP email event and return task ID."""
    try:
        task_result = send_email_otp_task.delay(event.email, event.otp)
        logger.info(f"OTP email task queued with ID: {task_result.id}")
        return {"task_id": task_result.id, "event_type": "email_otp"}
    except Exception as e:
        logger.error(f"Failed to queue OTP email task: {str(e)}")
        raise