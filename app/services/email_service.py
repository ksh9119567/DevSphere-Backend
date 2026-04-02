import os
import smtplib
import logging

from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


logger = logging.getLogger(__name__)

# Base templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def load_template(template_name: str) -> str:
    """Load email template from file."""
    template_path = TEMPLATES_DIR / template_name
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Template file not found: {template_path}")
        raise

def send_email(subject: str, text: str,  html: str, recipient_email: str) -> bool:
    from_email = os.getenv("DEFAULT_FROM_EMAIL")
    sender_email = os.getenv("EMAIL_USERNAME")
    password = os.getenv("EMAIL_PASSWORD")
    host = os.getenv("EMAIL_HOST")
    port = int(os.getenv("EMAIL_PORT_NUMBER", 587))

    # Subject and headers
    msg = MIMEMultipart("alternative")    
    
    msg['From'] = from_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    text = text
    html = html
    
    msg.attach(MIMEText(text, 'plain'))
    msg.attach(MIMEText(html, 'html'))

    try:
        server = smtplib.SMTP(host, port)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(from_email, recipient_email, msg.as_string())
        server.quit()
        logger.info("Email sent successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}", exc_info=True)
        return False

def send_email_otp(recipient_email: str, otp: str) -> bool:
    subject = "You One-Time Password (OTP)"
    
    # Load templates and format with OTP
    text = load_template("otp_email.txt").format(otp=otp)
    html = load_template("otp_email.html").format(otp=otp)
    
    logger.info(f"Sending OTP email to {recipient_email}")
    return send_email(subject, text, html, recipient_email)

#---------------------
# Emails for Users
#---------------------
def send_welcome_email(recipient_email: str) -> bool:
    subject = 'Welcome to DevSphere!'

    # Load templates
    text = load_template("welcome_email.txt")
    html = load_template("welcome_email.html")

    logger.info(f"Sending welcome email to {recipient_email}")
    return send_email(subject, text, html, recipient_email)

def send_profile_update_email(recipient_email: str) -> bool:
    subject = 'Your DevSphere profile has been updated'

    # Load templates
    text = load_template("profile_update.txt")
    html = load_template("profile_update.html")

    logger.info(f"Sending profile update email to {recipient_email}")
    return send_email(subject, text, html, recipient_email)

def send_account_deletion_email(recipient_email: str) -> bool:
    subject = 'Your DevSphere account has been deleted'

    # Load templates
    text = load_template("account_delete.txt")
    html = load_template("account_delete.html")

    logger.info(f"Sending account deletion email to {recipient_email}")
    return send_email(subject, text, html, recipient_email)

#---------------------
# Emails for Blogs
#---------------------
def send_blog_created_email(recipient_email: str) -> bool:
    subject = 'A new blog has been created'

    # Load templates
    text = load_template("blog_created.txt")
    html = load_template("blog_created.html")

    logger.info(f"Sending blog created email to {recipient_email}")
    return send_email(subject, text, html, recipient_email)

def send_blog_updated_email(recipient_email: str) -> bool:
    subject = 'A blog has been updated'

    # Load templates
    text = load_template("blog_updated.txt")
    html = load_template("blog_updated.html")

    logger.info(f"Sending blog updated email to {recipient_email}")
    return send_email(subject, text, html, recipient_email)

def send_blog_deleted_email(recipient_email: str) -> bool:
    subject = 'A blog has been deleted'

    # Load templates
    text = load_template("blog_deleted.txt")
    html = load_template("blog_deleted.html")

    logger.info(f"Sending blog deleted email to {recipient_email}")
    return send_email(subject, text, html, recipient_email)

def send_all_blogs_deleted_email(recipient_email: str) -> bool:
    subject = 'All your blogs have been deleted'

    # Load templates
    text = load_template("all_blogs_deleted.txt")
    html = load_template("all_blogs_deleted.html")

    logger.info(f"Sending all blogs deleted email to {recipient_email}")
    return send_email(subject, text, html, recipient_email)
