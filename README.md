# Matter Document Generator API

A closed-registry, JSON-only mail-merge service for generating templated legal correspondence. Built for auditability: every template is checked into the codebase (no user uploads), every payload is validated field-by-field against a strict schema, and every render/send is logged.

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
git clone <repo-url> strict-mail-merge
cd strict-mail-merge
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your RESEND_API_KEY and FROM_EMAIL
uvicorn app.main:app --reload
```

## Adding a new template
1. Add a strict Pydantic schema to app/templates/schema.py
2. Add the .jinja file to app/templates/files
3. Register both in TEMPLATE_REGISTRY in app/templates/registry.py

No other code changes needed - validation, rendering, and auditing all flow through the registry automatically.

## License
MIT
