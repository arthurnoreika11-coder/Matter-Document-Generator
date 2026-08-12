from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.core.generators.docx_gen import create_lba as create_lba_docx
from app.core.generators.pdf_gen import create_lba as create_lba_pdf
from app.core.email_sender import send_email
from app.core.merge_engine import render
from app.templates.registry import get_template_entry


TRUTHY_VALUES = {"true", "yes", "1"}
DOC_REQUIRED_FIELDS = ("lba_name", "recipient_name", "legal_basis", "demands")


def bulk_action(file_path: str | Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    with Path(file_path).open(mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row_number, raw_row in enumerate(reader, start=2):
            row = _normalise_row(raw_row)
            action_type = row.get("action_type", "").lower().strip()

            if not action_type:
                results.append(_error_result(row_number, "", "Missing required field: action_type"))
                continue

            try:
                match action_type:
                    case "send_email":
                        result = _send_email_action(row)
                    case "generate_docx":
                        result = _generate_docx_action(row)
                    case "generate_pdf":
                        result = _generate_pdf_action(row)
                    case _:
                        result = {
                            "status": "error",
                            "error": f"Unknown action_type: {action_type}",
                        }
            except Exception as exc:
                result = {"status": "error", "error": str(exc)}

            results.append({
                "row_number": row_number,
                "action_type": action_type,
                **result,
            })

    return results


def _normalise_row(row: dict[str, str | None]) -> dict[str, str]:
    return {
        key.strip(): (value or "").strip()
        for key, value in row.items()
        if key is not None
    }


def _send_email_action(row: dict[str, str]) -> dict[str, Any]:
    template_id = _required_value(row, "template_id")
    to = _required_value(row, "to")
    confirm = _required_value(row, "confirm").lower()

    if confirm not in TRUTHY_VALUES:
        return {
            "status": "error",
            "error": "confirm must be true, yes, or 1 to send an email",
        }

    entry = get_template_entry(template_id)
    if entry is None:
        return {
            "status": "error",
            "error": f"Unknown template_id: {template_id}",
        }

    payload = {
        field_name: row.get(field_name, "")
        for field_name in entry.schema.model_fields
    }

    try:
        data = entry.schema.model_validate(payload)
    except ValidationError as exc:
        return {"status": "error", "error": exc.errors()}

    rendered = render(entry, data)
    attachment_paths = _parse_attachment_paths(row.get("attachment_paths", ""))

    send_email(
        to=to,
        subject=rendered.subject,
        body=rendered.body,
        attachments=attachment_paths,
    )

    return {
        "status": "sent",
        "template_id": template_id,
        "to": to,
        "subject": rendered.subject,
        "attachment_count": len(attachment_paths),
    }


def _generate_docx_action(row: dict[str, str]) -> dict[str, Any]:
    kwargs = _document_kwargs(row)
    docx_path = create_lba_docx(**kwargs)

    return {
        "status": "success",
        "docx_name": docx_path.name,
        "docx_path": str(docx_path),
    }


def _generate_pdf_action(row: dict[str, str]) -> dict[str, Any]:
    kwargs = _document_kwargs(row)
    pdf_path = create_lba_pdf(**kwargs)

    return {
        "status": "success",
        "pdf_name": pdf_path.name,
        "pdf_path": str(pdf_path),
    }


def _document_kwargs(row: dict[str, str]) -> dict[str, str]:
    kwargs = {
        field_name: _required_value(row, field_name)
        for field_name in DOC_REQUIRED_FIELDS
    }

    if row.get("output_dir"):
        kwargs["output_dir"] = row["output_dir"]

    return kwargs


def _required_value(row: dict[str, str], field_name: str) -> str:
    value = row.get(field_name, "")
    if not value:
        raise ValueError(f"Missing required field: {field_name}")

    return value


def _parse_attachment_paths(value: str) -> list[str]:
    if not value:
        return []

    return [
        path.strip()
        for path in value.split(";")
        if path.strip()
    ]


def _error_result(row_number: int, action_type: str, error: str) -> dict[str, Any]:
    return {
        "row_number": row_number,
        "action_type": action_type,
        "status": "error",
        "error": error,
    }
