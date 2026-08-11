from __future__ import annotations

import base64
from pathlib import Path
from typing import Iterable

import resend

from app.config import settings

resend.api_key = settings.resend_api_key


AttachmentPath = str | Path


def _build_resend_attachments(attachments: Iterable[AttachmentPath]) -> list[dict[str, str]]:
    resend_attachments: list[dict[str, str]] = []

    for attachment in attachments:
        path = Path(attachment)
        if not path.is_file():
            raise FileNotFoundError(f"Attachment not found: {path}")

        content = base64.b64encode(path.read_bytes()).decode("ascii")
        resend_attachments.append({
            "filename": path.name,
            "content": content,
        })

    return resend_attachments


def send_email(
    to: str,
    subject: str,
    body: str,
    attachments: Iterable[AttachmentPath] | None = None,
) -> None:
    message = {
        "from": settings.from_email,
        "to": [to],
        "subject": subject,
        "text": body,
    }

    if attachments:
        message["attachments"] = _build_resend_attachments(attachments)

    resend.emails.send(message)
