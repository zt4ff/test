import os

from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from pydantic import EmailStr

load_dotenv()
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    MAIL_STARTTLS=os.getenv("MAIL_STARTTLS", "False").lower() == "true",
    MAIL_SSL_TLS=os.getenv("MAIL_SSL_TLS", "True").lower() == "true",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)
class EmailService:
    @staticmethod
    async def send_email(email: EmailStr, subject: str, body: str, retry: int = 0):
        message = MessageSchema(
            subject=subject,
            recipients=[email],
            body=body,
            subtype="html"
        )
        fm = FastMail(conf)
        try:
            await fm.send_message(message)
        except Exception as e:
            if retry >= 3:
                print(f"Failed to send email to {email} after 3 retries: {e}")
                return
            print(f"Failed to send email to {email}: {e}")
            await EmailService.send_email(
                email=email,
                subject=subject,
                body=body,
                retry=retry + 1
            )

email_service = EmailService()