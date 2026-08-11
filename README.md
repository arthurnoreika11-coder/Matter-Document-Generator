# Matter Document Generator

A FastAPI and MCP service for strict legal email rendering and sending, with optional Letter Before Action DOCX generation. It is built for auditability: every email template is checked into the codebase, every payload is validated field-by-field against a strict schema, and every FastAPI render and send is logged.

## Why "strict"
- **Closed template registry** — templates aren't uploaded via the API; they live in `app/templates/files/` and get reviewed like code. This closes off Server-Side Template Injection (SSTI) as an attack surface entirely.
- **Strict JSON schemas** — each template has a matching Pydantic model with `extra="forbid"`. Unknown fields, missing fields, or wrong types are rejected with a 422 before anything is rendered.
- **Sandboxed rendering** — Jinja2 runs in `SandboxedEnvironment` with `StrictUndefined`, so a template referencing an undefined variable fails loudly instead of rendering a blank into client correspondence.
- **Audit log** — every render and send is recorded (template ID, payload hash, timestamp, status) in SQLite via SQLModel.

## Requirements
- Python 3.11+
- A [Resend](https://resend.com) API key for sending email

## Setup
```bash
git clone <repo-url> matter-document-generator
cd matter-document-generator
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Create a `.env` file when sending email or changing the audit database location:
```env
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=sender@example.com
DATABASE_URL=sqlite:///./audit.db
```

If `DATABASE_URL` is omitted, the app uses `sqlite:///./audit.db`.

## FastAPI usage
The HTTP API exposes email rendering and sending routes under `/emails`.

Render a registered template without sending:
```bash
curl -X POST "http://127.0.0.1:8000/emails/welcome_email/render" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "matter_reference": "MAT-001",
    "client_name": "Jane Client",
    "fee_earner_name": "Alex Solicitor"
  }'
```

Send a rendered template through Resend:
```bash
curl -X POST "http://127.0.0.1:8000/emails/case_update_email/send?to=client@example.com" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "client@example.com",
    "matter_reference": "MAT-001",
    "client_name": "Jane Client",
    "fee_earner_name": "Alex Solicitor",
    "case_update_summary": "We have received the signed documents and will file them today."
  }'
```

Unknown template IDs return `404`. Invalid payloads, missing fields, wrong types, or extra fields return `422`.

## Built-in templates
- `welcome_email` requires `email`, `matter_reference`, `client_name`, and `fee_earner_name`.
- `case_update_email` requires `email`, `matter_reference`, `client_name`, `fee_earner_name`, and `case_update_summary`.

## Adding a new template
1. Add a strict Pydantic schema to `app/templates/schemas.py`.
2. Add the `.jinja` file to `app/templates/files/`.
3. Register both in `TEMPLATES` in `app/templates/registry.py`.

No other code changes needed - validation, rendering, and auditing all flow through the registry automatically.

## MCP server
The MCP server exposes the same registered email templates plus local DOCX generation and attachment sending tools.

Run it with:
```bash
python -m app.mcp_server
```

Available MCP capabilities:
- `templates://list` lists template IDs and required payload fields.
- `render_email` renders a registered email template.
- `generate_lba_docx` creates a local Letter Before Action `.docx`.
- `send_email_tool` sends a rendered email, requires `confirm=true`, and can attach local files such as generated DOCX documents.

## DOCX generation
DOCX generation is available through direct Python usage and through the MCP server. It is not currently exposed as a FastAPI route.

```python
from app.core.docx_gen import create_lba
from app.core.email_sender import send_email

docx_path = create_lba(
    lba_name="letter-before-action",
    recipient_name="Jane Client",
    legal_basis="Breach of contract resulting from a breach of Section 49 Consumer Rights Act 2015 - services to be performed with reasonable care and skill.",
    demands="Return and carry out remedial works within 14 days.",
)

send_email(
    to="client@example.com",
    subject="Letter Before Action",
    body="Please see attached.",
    attachments=[docx_path],
)
```

## Audit log
FastAPI render and send calls are written to SQLite via SQLModel. Each audit record stores the template ID, a SHA-256 hash of the payload, a timestamp, and the render or send status. Failed send attempts are also logged before the API returns a `502`.

## License
MIT
