from app.core.celery import celery
from app.services.email_service import send_email_otp


@celery.task(name="send_email_otp_task", autoretry_for=(Exception,), retry_kwargs={'max_retries': 3})
def send_email_otp_task(email: str, otp: str):
    send_email_otp(email, otp)