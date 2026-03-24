# Tasks package
from app.tasks.email_task import send_email_otp_task
from app.tasks.user_task import (
    send_welcome_email_task, send_profile_update_email_task, send_account_deletion_email_task
)
from app.tasks.blog_task import (
    send_blog_created_email_task, send_blog_updated_email_task, send_blog_deleted_email_task
)

__all__ = [
    "send_email_otp_task",
    "send_welcome_email_task",
    "send_profile_update_email_task",
    "send_account_deletion_email_task",
    "send_blog_created_email_task",
    "send_blog_updated_email_task",
    "send_blog_deleted_email_task"
]
