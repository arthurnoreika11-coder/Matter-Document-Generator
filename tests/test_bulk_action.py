from __future__ import annotations

import csv

from app.core import bulk_action as bulk_action_module
from app.core.bulk_action import bulk_action


def write_csv(path, rows, fieldnames):
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_bulk_action_processes_mixed_valid_actions(tmp_path, monkeypatch):
    sent_messages = []

    monkeypatch.setattr(
        bulk_action_module,
        "send_email",
        lambda **kwargs: sent_messages.append(kwargs),
    )

    csv_path = tmp_path / "bulk.csv"
    output_dir = tmp_path / "generated"
    write_csv(
        csv_path,
        [
            {
                "action_type": "generate_docx",
                "lba_name": "doc letter",
                "recipient_name": "Jane Client",
                "legal_basis": "Breach of contract",
                "demands": "Refund within 14 days",
                "output_dir": str(output_dir),
            },
            {
                "action_type": "generate_pdf",
                "lba_name": "pdf letter",
                "recipient_name": "Jane Client",
                "legal_basis": "Breach of contract",
                "demands": "Refund within 14 days",
                "output_dir": str(output_dir),
            },
            {
                "action_type": "send_email",
                "template_id": "welcome_email",
                "to": "client@example.com",
                "confirm": "true",
                "email": "client@example.com",
                "matter_reference": "MAT-001",
                "client_name": "Jane Client",
                "fee_earner_name": "Alex Solicitor",
            },
        ],
        [
            "action_type",
            "template_id",
            "to",
            "confirm",
            "email",
            "matter_reference",
            "client_name",
            "fee_earner_name",
            "lba_name",
            "recipient_name",
            "legal_basis",
            "demands",
            "output_dir",
        ],
    )

    results = bulk_action(csv_path)

    assert [result["status"] for result in results] == ["success", "success", "sent"]
    assert results[0]["docx_path"].endswith(".docx")
    assert results[1]["pdf_path"].endswith(".pdf")
    assert len(sent_messages) == 1
    assert sent_messages[0]["to"] == "client@example.com"


def test_unknown_action_type_returns_error(tmp_path):
    csv_path = tmp_path / "bulk.csv"
    write_csv(csv_path, [{"action_type": "not_real"}], ["action_type"])

    results = bulk_action(csv_path)

    assert results == [
        {
            "row_number": 2,
            "action_type": "not_real",
            "status": "error",
            "error": "Unknown action_type: not_real",
        }
    ]


def test_missing_required_field_returns_error_and_continues(tmp_path):
    csv_path = tmp_path / "bulk.csv"
    write_csv(
        csv_path,
        [
            {
                "action_type": "generate_docx",
                "lba_name": "letter",
                "recipient_name": "Jane Client",
                "legal_basis": "",
                "demands": "Refund within 14 days",
            },
            {
                "action_type": "generate_docx",
                "lba_name": "letter",
                "recipient_name": "Jane Client",
                "legal_basis": "Breach of contract",
                "demands": "Refund within 14 days",
            },
        ],
        ["action_type", "lba_name", "recipient_name", "legal_basis", "demands"],
    )

    results = bulk_action(csv_path)

    assert results[0]["status"] == "error"
    assert results[0]["error"] == "Missing required field: legal_basis"
    assert results[1]["status"] == "success"


def test_send_email_without_confirmation_does_not_send(tmp_path, monkeypatch):
    sent_messages = []
    monkeypatch.setattr(
        bulk_action_module,
        "send_email",
        lambda **kwargs: sent_messages.append(kwargs),
    )

    csv_path = tmp_path / "bulk.csv"
    write_csv(
        csv_path,
        [
            {
                "action_type": "send_email",
                "template_id": "welcome_email",
                "to": "client@example.com",
                "confirm": "false",
                "email": "client@example.com",
                "matter_reference": "MAT-001",
                "client_name": "Jane Client",
                "fee_earner_name": "Alex Solicitor",
            }
        ],
        [
            "action_type",
            "template_id",
            "to",
            "confirm",
            "email",
            "matter_reference",
            "client_name",
            "fee_earner_name",
        ],
    )

    results = bulk_action(csv_path)

    assert results[0]["status"] == "error"
    assert "confirm must be true" in results[0]["error"]
    assert sent_messages == []


def test_send_email_with_confirmation_renders_and_sends(tmp_path, monkeypatch):
    sent_messages = []
    monkeypatch.setattr(
        bulk_action_module,
        "send_email",
        lambda **kwargs: sent_messages.append(kwargs),
    )

    csv_path = tmp_path / "bulk.csv"
    write_csv(
        csv_path,
        [
            {
                "action_type": "send_email",
                "template_id": "welcome_email",
                "to": "client@example.com",
                "confirm": "yes",
                "email": "client@example.com",
                "matter_reference": "MAT-001",
                "client_name": "Jane Client",
                "fee_earner_name": "Alex Solicitor",
            }
        ],
        [
            "action_type",
            "template_id",
            "to",
            "confirm",
            "email",
            "matter_reference",
            "client_name",
            "fee_earner_name",
        ],
    )

    results = bulk_action(csv_path)

    assert results[0]["status"] == "sent"
    assert results[0]["subject"] == "Welcome to Our Service, Jane Client!"
    assert sent_messages[0]["subject"] == "Welcome to Our Service, Jane Client!"


def test_generate_docx_and_pdf_return_correct_extensions(tmp_path):
    csv_path = tmp_path / "bulk.csv"
    write_csv(
        csv_path,
        [
            {
                "action_type": "generate_docx",
                "lba_name": "letter",
                "recipient_name": "Jane Client",
                "legal_basis": "Breach of contract",
                "demands": "Refund within 14 days",
                "output_dir": str(tmp_path),
            },
            {
                "action_type": "generate_pdf",
                "lba_name": "letter",
                "recipient_name": "Jane Client",
                "legal_basis": "Breach of contract",
                "demands": "Refund within 14 days",
                "output_dir": str(tmp_path),
            },
        ],
        ["action_type", "lba_name", "recipient_name", "legal_basis", "demands", "output_dir"],
    )

    results = bulk_action(csv_path)

    assert results[0]["docx_path"].endswith(".docx")
    assert results[1]["pdf_path"].endswith(".pdf")
