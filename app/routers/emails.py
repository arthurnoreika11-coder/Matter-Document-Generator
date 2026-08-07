from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import ValidationError
from requests import session
from sqlmodel import Session

from app.templates.registry import get_template
from app.core.merge_engine import render
from app.core.email_sender import send_email
from app.models.audit import AuditLog, hash_payload
from app.db import get_session

router = APIRouter(prefix="/emails", tags=["emails"])

@router.post("/{template_id}/render")
def render_email(
    template_id: str,
    payload: dict = Body(...),
    session: Session = Depends(get_session),
):
    template_entry = get_template(template_id)
    if template_entry is None:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        data = template_entry.schema.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())

    result = render(template_entry, data)

    session.add(AuditLog(
        template_id=template_id,
        payload_hash=hash_payload(payload),
        status="rendered",
    ))
    session.commit()

    return result

@router.post("/{template_id}/send")
def send_rendered_email(
    template_id: str,
    to: str,
    payload: dict = Body(...),
    session: Session = Depends(get_session),
):
    entry = get_template(template_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        data = entry.schema.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())

    result = render(entry, data)

    try:
        send_email(to=to, subject=result.subject, body=result.body)
        status = "sent"
    except Exception as exc:
        status = f"failed: {str(exc)}"
        session.add(AuditLog(
            template_id=template_id,
            payload_hash=hash_payload(payload),
            status=status,
        ))
        session.commit()
        raise HTTPException(status_code=502, detail=f"Failed to send email: {str(exc)}")

    session.add(AuditLog(
        template_id=template_id,
        payload_hash=hash_payload(payload),
        status=status,
    ))
    session.commit()

    return {"status": "sent", "subject": result.subject}
