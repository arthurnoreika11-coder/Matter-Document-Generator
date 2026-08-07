from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError

from app.templates.registry import TEMPLATE_REGISTRY, get_template
from app.core.merge_engine import render as merge_render
from app.core.email_sender import send_email

mcp = FastMCP("matter-document-generator", "1.0.0")

@mcp.resource("templates://list")
def list_templates() -> dict:
    """List every registered email template ID and its required parameters."""
    return{
        template_id: list(template_entry.schema.model_fields.keys())
        for template_id, template_entry in TEMPLATE_REGISTRY.items()
    }

@mcp.tool()
def render_email(template_id: str, payload: dict) -> dict:
    """
    Render (but do not send) an email from a registered template.
    template_id must match one of the IDs from templates://list.
    payload must satisfy that template's exact field schema — no extra
    or missing fields are permitted.
    """
    entry = get_template(template_id)
    if entry is None:
        return {"error": f"Unknown template_id '{template_id}'"}

    try:
        data = entry.schema.model_validate(payload)
    except ValidationError as exc:
        return {"error": exc.errors()}

    result = merge_render(entry, data)
    return {"subject": result.subject, "body": result.body}


@mcp.tool()
def send_email_tool(template_id: str, to: str, payload: dict, confirm: bool) -> dict:
    """
    Send an email from a registered template. Sends real client
    correspondence — confirm must be explicitly set to true, and this
    should only be called after the caller has shown the rendered
    preview (via render_email) to a human for approval.
    """
    if not confirm:
        return {"error": "confirm must be true to send an email"}

    entry = get_template(template_id)
    if entry is None:
        return {"error": f"Unknown template_id '{template_id}'"}

    try:
        data = entry.schema.model_validate(payload)
    except ValidationError as exc:
        return {"error": exc.errors()}

    result = merge_render(entry, data)
    send_email(to=to, subject=result.subject, body=result.body)
    return {"status": "sent", "subject": result.subject}


if __name__ == "__main__":
    mcp.run()
