# Matter Document Generator

A robust, audit-first FastAPI and MCP service for strict legal email rendering and sending, with optional Letter Before Action (LBA) DOCX generation. Designed for legal teams requiring compliance, security, and auditability.

**Key features:** Sandboxed template rendering, strict payload validation, comprehensive audit logging, MCP server integration, and bulk processing capabilities.

## 🔒 Why "Strict"

Security and compliance are at the core of this project:

- **Closed template registry** — Templates are versioned in `app/templates/files/` and reviewed like code, eliminating Server-Side Template Injection (SSTI) vulnerabilities entirely.
- **Strict JSON schemas** — Each template pairs with a Pydantic model configured with `extra="forbid"`. Unknown fields, missing fields, or type mismatches are rejected with a 422 response before rendering.
- **Sandboxed rendering** — Jinja2 runs in `SandboxedEnvironment` with `StrictUndefined`, so undefined variables fail loudly rather than silently rendering blanks into client correspondence.
- **Comprehensive audit log** — Every render and send operation is recorded (template ID, payload hash, timestamp, status) in SQLite via SQLModel, enabling full compliance tracking.

## 📋 Requirements

- Python 3.11 or later
- [Resend](https://resend.com) API key for email delivery (optional if only rendering)
- pip for dependency management

## ⚡ Quick Start

### Installation

```bash
git clone <repo-url> matter-document-generator
cd matter-document-generator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root for email sending and database customization:

```env
# Email configuration
RESEND_API_KEY=your_resend_api_key_here
FROM_EMAIL=sender@example.com

# Database configuration (optional)
DATABASE_URL=sqlite:///./audit.db
```

**Note:** If `DATABASE_URL` is omitted, the app defaults to `sqlite:///./audit.db`.

### Running the Server

```bash
# FastAPI server (development)
uvicorn app.main:app --reload

# FastAPI server (production)
uvicorn app.main:app --host 0.0.0.0 --port 8000

# MCP server
python -m app.mcp_server
```

The FastAPI server is accessible at `http://127.0.0.1:8000` with interactive docs at `/docs`.

## 🚀 FastAPI Usage

The HTTP API exposes email rendering and sending routes under `/emails`.

### Render a Template (Without Sending)

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

### Send a Rendered Template

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

### API Response Codes

| Code | Meaning |
|------|---------|
| 200  | Template rendered or email sent successfully |
| 404  | Template ID not found |
| 422  | Invalid payload (missing fields, extra fields, wrong type) |
| 500  | Server error (check logs and audit database) |

## 📧 Built-in Templates

### welcome_email
**Required fields:** `email`, `matter_reference`, `client_name`, `fee_earner_name`

Welcome message introducing a new matter to the client.

### case_update_email
**Required fields:** `email`, `matter_reference`, `client_name`, `fee_earner_name`, `case_update_summary`

Case update notification with summary of recent progress.

## 🔧 Adding a New Template

Templates follow a three-step registration process:

1. **Define the schema** — Add a Pydantic model to `app/templates/schemas.py`:
   ```python
   class MyEmailSchema(BaseModel):
       email: str
       matter_reference: str
       client_name: str
       # Add other required fields
       
       model_config = ConfigDict(extra="forbid")
   ```

2. **Create the Jinja2 template** — Add a `.jinja` file to `app/templates/files/`:
   ```jinja
   <html>
     <body>
       <p>Dear {{ client_name }},</p>
       <p>Matter Reference: {{ matter_reference }}</p>
     </body>
   </html>
   ```

3. **Register in the template registry** — Add an entry to `TEMPLATES` in `app/templates/registry.py`:
   ```python
   "my_email": TemplateEntry(
       template_id="my_email",
       file_name="my_email.jinja",
       subject_template="Subject for {{ client_name }}",
       schema=MyEmailSchema,
   ),
   ```

## 🔌 MCP Server

The MCP server provides the same template rendering and sending capabilities plus local DOCX generation, designed for AI/agent integration.

### Running the MCP Server

```bash
python -m app.mcp_server
```

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `templates://list` | Lists all template IDs and their required payload fields |
| `render_email` | Renders a registered email template |
| `generate_lba_docx` | Generates a local Letter Before Action `.docx` file |
| `send_email_tool` | Sends a rendered email; requires `confirm=true` and can attach local files |

## 📄 DOCX Generation

Generate Letter Before Action documents locally via Python or the MCP server (not exposed as a FastAPI route).

### Python Usage

```python
from app.core.docx_gen import create_lba
from app.core.email_sender import send_email

# Generate LBA document
docx_path = create_lba(
    lba_name="letter-before-action",
    recipient_name="Jane Client",
    legal_basis="Breach of contract resulting from a breach of Section 49 Consumer Rights Act 2015 - services to be performed with reasonable care and skill.",
    demands="Return and carry out remedial works within 14 days.",
)

# Send with attachment
send_email(
    to="recipient@example.com",
    subject="Letter Before Action",
    body="Please find attached our formal letter before action.",
    attachment_path=docx_path
)
```

### MCP Usage

Use the MCP server tools to generate and send documents:

```
Tool: generate_lba_docx
Input: {
  "lba_name": "letter-before-action",
  "recipient_name": "Jane Client",
  "legal_basis": "...",
  "demands": "..."
}
```

## 📊 Project Structure

```
matter-document-generator/
├── app/
│   ├── main.py                    # FastAPI application entry point
│   ├── mcp_server.py              # MCP server definition
│   ├── config.py                  # Configuration management
│   ├── db.py                      # Database initialization
│   ├── core/
│   │   ├── email_sender.py        # Email sending logic
│   │   ├── merge_engine.py        # Document merging
│   │   ├── bulk_action.py         # Bulk processing
│   │   └── generators/
│   │       ├── doc_setup.py       # Document setup utilities
│   │       ├── docx_gen.py        # DOCX generation
│   │       └── pdf_gen.py         # PDF generation
│   ├── models/
│   │   └── audit.py               # Audit log data models
│   ├── routers/
│   │   └── emails.py              # Email API routes
│   └── templates/
│       ├── schemas.py             # Pydantic validation schemas
│       ├── registry.py            # Template registry
│       └── files/                 # Jinja2 template files
├── tests/
│   └── test_bulk_action.py        # Unit and integration tests
├── requirements.txt               # Python dependencies
├── LICENSE                        # MIT License
└── README.md                      # This file
```

## 🧪 Testing

Run the test suite:

```bash
python -m pytest tests/ -v
```

Run with coverage:

```bash
python -m pytest tests/ --cov=app --cov-report=html
```

## 🏗️ Architecture

### Data Flow

1. **Request Validation** — Incoming payloads are validated against the template's Pydantic schema.
2. **Template Lookup** — The template registry retrieves the corresponding Jinja2 template.
3. **Sandboxed Rendering** — Jinja2 renders the template in a restricted environment.
4. **Audit Logging** — Render and send operations are logged to the SQLite database.
5. **Email Delivery** — Via Resend API (optional).

### Security Considerations

- Templates are code-reviewed before deployment
- All templates run in a sandboxed Jinja2 environment
- Strict validation prevents injection attacks
- Audit logs enable forensic analysis
- No dynamic template uploads via the API

## 📝 Environment Variables

| Variable | Default | Required | Purpose |
|----------|---------|----------|---------|
| `RESEND_API_KEY` | — | Yes (for sending) | Resend API key for email delivery |
| `FROM_EMAIL` | — | Yes (for sending) | Sender email address |
| `DATABASE_URL` | `sqlite:///./audit.db` | No | SQLite database URL for audit logs |

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Jinja2 Documentation](https://jinja.palletsprojects.com)
- [Pydantic Documentation](https://docs.pydantic.dev)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io)
- [Resend Email API](https://resend.com/docs)

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
MIT See [LICENSE](LICENSE) for details.
