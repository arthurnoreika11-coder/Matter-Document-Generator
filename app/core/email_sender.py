import resend 
from app.config import settings

resend.api_key = settings.resend_api_key

def send_email(to:str, subject: str, body: str) -> None:
    resend.emails.send({
        "from": settings.from_email,
        "to": [to],
        "subject": subject,
        "text": body,
    })
