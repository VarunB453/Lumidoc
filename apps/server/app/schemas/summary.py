"""Summary-related Pydantic schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.schemas.common import ORMModel

SummaryStatus = Literal["pending", "processing", "ready", "failed"]


class SummaryResponse(ORMModel):
    id: str
    file_id: str
    user_id: str
    content: str
    status: SummaryStatus = "ready"
    model_used: str
    generated_at: datetime


class SummaryStatusResponse(ORMModel):
    file_id: str
    status: SummaryStatus
    task_id: str | None = None
    message: str | None = None
