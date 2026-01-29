
import smtplib
from email.message import EmailMessage
import logging
import os

logger = logging.getLogger(__name__)

# Placeholder configuration - User needs to update this or provide env vars
from app.core.config import settings

# Configuration from settings
SMTP_HOST = settings.SMTP_HOST
SMTP_PORT = settings.SMTP_PORT
SMTP_USER = settings.SMTP_USER
SMTP_PASSWORD = settings.SMTP_PASSWORD

def send_email(to_email: str, subject: str, body: str, attachment_paths: list[str] = None):
    """
    Sends an email to the specified recipient with optional attachments.
    """
    if not to_email:
        logger.warning("No email address provided. Skipping send.")
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to_email
    msg.set_content(body)

    if attachment_paths:
        for file_path in attachment_paths:
            if not os.path.exists(file_path):
                logger.warning(f"Attachment not found: {file_path}")
                continue
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
            
            msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

    try:
        # For development/demo purposes, if password is "CHANGE_ME", we might just log it
        if SMTP_PASSWORD == "CHANGE_ME":
            logger.info(f"[MOCK SEND] Email to {to_email} with subject '{subject}'")
            return True

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False
