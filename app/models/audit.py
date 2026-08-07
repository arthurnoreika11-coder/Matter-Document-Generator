from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    template_id: str
    payload_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str

def hash_payload(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
