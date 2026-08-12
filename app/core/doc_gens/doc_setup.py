import re

def _safe_doc_filename(name: str) -> str:
    base_name = Path(name).name
    stem = Path(base_name).stem
    safe_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", stem).strip("._-")

    if not safe_stem:
        safe_stem = "Generatered File - "

    return f"{safe_stem}.docx"