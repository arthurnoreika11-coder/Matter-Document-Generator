from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

from app.templates.schemas import WelcomeEmailSchema, CaseUpdateEmailSchema

TEMPLATES_DIR = Path(__file__).parent / "files"

@dataclass(frozen=True)
class TemplateEntry:
    template_id: str
    file_name: str
    subject_template: str
    schema: type[BaseModel]

TEMPLATES: dict[str, TemplateEntry] = {
    "welcome_email": TemplateEntry(
        template_id="welcome_email",
        file_name="welcome_email.jinja",
        subject_template="Welcome to Our Service, {{ client_name }}!",
        schema=WelcomeEmailSchema,
    ),
    "case_update_email": TemplateEntry(
        template_id="case_update_email",
        file_name="case_update_email.jinja",
        subject_template="Case Update for Matter {{ matter_reference }}",
        schema=CaseUpdateEmailSchema,
    ),
}

def get_template_entry(template_id: str) -> Optional[TemplateEntry]:
    return TEMPLATES.get(template_id)
