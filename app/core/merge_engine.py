from jinja2.sandbox import SandboxedEnvironment
from jinja2 import FileSystemLoader, StrictUndefined
from pydantic import BaseModel

from app.templates.registry import get_template_entry, TemplateEntry, TEMPLATES_DIR

env = SandboxedEnvironment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    undefined=StrictUndefined,
    autoescape=False,
)

class RenderedEmail(BaseModel):
    subject: str
    body: str

def render(entry: TemplateEntry, data: BaseModel) -> RenderedEmail:
    subject_template = env.from_string(entry.subject_template)
    body_template = env.get_template(entry.file_name)

    subject = subject_template.render(**data.dict())
    body = body_template.render(**data.dict())

    return RenderedEmail(subject=subject.strip(), body=body.strip())