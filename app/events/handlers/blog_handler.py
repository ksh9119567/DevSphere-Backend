import logging

from app.events.events.blog_events import (
    BlogCreatedEvent, BlogUpdatedEvent, BlogDeletedEvent
)
from app.tasks.blog_task import (
    send_blog_created_email_task, send_blog_updated_email_task, 
    send_blog_deleted_email_task
)

logger = logging.getLogger(__name__)


def handle_blog_created(event: BlogCreatedEvent) -> dict:
    """Handle user registration event and return task ID."""
    try:
        task_result = send_blog_created_email_task.delay(event.email)
        logger.info(f"Welcome email task queued with ID: {task_result.id}")
        return {"task_id": task_result.id, "event_type": "welcome_email"}
    except Exception as e:
        logger.error(f"Failed to queue welcome email task: {str(e)}")
        raise    
    
def handle_blog_updated(event: BlogUpdatedEvent) -> dict:
    """Handle user update event and return task ID."""
    try:
        task_result = send_blog_updated_email_task.delay(event.email)
        logger.info(f"Profile Update email task queued with ID: {task_result.id}")
        return {"task_id": task_result.id, "event_type": "profile_update_email"}
    except Exception as e:
        logger.error(f"Failed to queue profile update email task: {str(e)}")
        raise
    
def handle_blog_deleted(event: BlogDeletedEvent) -> dict:
    """Handle user deletion event and return task ID."""
    try:
        task_result = send_blog_deleted_email_task.delay(event.email)
        logger.info(f"Account deletion email task queued with ID: {task_result.id}")
        return {"task_id": task_result.id, "event_type": "account_deletion_email"}
    except Exception as e:
        logger.error(f"Failed to queue account deletion email task: {str(e)}")
        raise