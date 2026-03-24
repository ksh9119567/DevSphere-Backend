import logging

from app.events.events.user_events import (
    UserRegisteredEvent, 
    UserUpdatedEvent, UserDeletedEvent
)
from app.tasks.user_task import (
    send_welcome_email_task, send_account_deletion_email_task,
    send_profile_update_email_task
)

logger = logging.getLogger(__name__)


def handle_user_registered(event: UserRegisteredEvent) -> dict:
    """Handle user registration event and return task ID."""
    try:
        task_result = send_welcome_email_task.delay(event.email)
        logger.info(f"Welcome email task queued with ID: {task_result.id}")
        return {"task_id": task_result.id, "event_type": "welcome_email"}
    except Exception as e:
        logger.error(f"Failed to queue welcome email task: {str(e)}")
        raise    
    
def handle_user_updated(event: UserUpdatedEvent) -> dict:
    """Handle user update event and return task ID."""
    try:
        task_result = send_profile_update_email_task.delay(event.email)
        logger.info(f"Profile Update email task queued with ID: {task_result.id}")
        return {"task_id": task_result.id, "event_type": "profile_update_email"}
    except Exception as e:
        logger.error(f"Failed to queue profile update email task: {str(e)}")
        raise
    
def handle_user_deleted(event: UserDeletedEvent) -> dict:
    """Handle user deletion event and return task ID."""
    try:
        task_result = send_account_deletion_email_task.delay(event.email)
        logger.info(f"Account deletion email task queued with ID: {task_result.id}")
        return {"task_id": task_result.id, "event_type": "account_deletion_email"}
    except Exception as e:
        logger.error(f"Failed to queue account deletion email task: {str(e)}")
        raise