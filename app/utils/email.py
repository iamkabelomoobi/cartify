from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings
import logging

logger = logging.getLogger("uvicorn.error")

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_HOST,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=False,
)


async def send_email(subject: str, recipients: list[str], body: str):
    """
    Sends an email using FastAPI-Mail configured for Mailhog.
    """
    try:
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="html",
        )

        fm = FastMail(mail_config)
        await fm.send_message(message)
        logger.info(f"Email sent successfully to {recipients}")
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {str(e)}")
