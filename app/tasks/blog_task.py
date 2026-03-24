from app.core.celery import celery
from app.services.email_service import (
    send_blog_created_email, send_blog_updated_email, send_blog_deleted_email
)

@celery.task(name="send_blog_created_email_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_blog_created_email_task(email: str):
    send_blog_created_email(email)
    
@celery.task(name="send_blog_updated_email_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})    
def send_blog_updated_email_task(email: str):
    send_blog_updated_email(email)

@celery.task(name="send_blog_deleted_email_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_blog_deleted_email_task(email: str):
    send_blog_deleted_email(email)