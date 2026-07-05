from app.core.celery import celery
from app.services.email_service import (
    send_welcome_email, send_account_deletion_email,
    send_profile_update_email
)


@celery.task(name="send_welcome_email_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_welcome_email_task(email: str):
    send_welcome_email(email)
    
@celery.task(name="send_profile_update_email_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_profile_update_email_task(email: str):
    send_profile_update_email(email)

@celery.task(name="send_account_deletion_email_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_account_deletion_email_task(email: str):
    send_account_deletion_email(email)