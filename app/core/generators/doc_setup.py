from pathlib import Path
import re


def _safe_doc_filename(name: str, extension: str) -> str:
    base_name = Path(name).name
    stem = Path(base_name).stem
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")

    if not safe_stem:
        safe_stem = "generated-file"

    return f"{safe_stem}.{extension.lstrip('.')}"


def _safe_docx_filename(name: str) -> str:
    return _safe_doc_filename(name, "docx")


def _safe_pdf_filename(name: str) -> str:
    return _safe_doc_filename(name, "pdf")
