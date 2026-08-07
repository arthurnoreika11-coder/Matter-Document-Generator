import resend 
from app/config import settings

resend.api_key = settings.RESEND_API_KEY

def send_email(to:str, subject: str, body: str) -> None:
    resend.emails.send({
        "from": settings.FROM_EMAIL,
        "to": [to],
        "subject": subject,
        "text": body,
    })