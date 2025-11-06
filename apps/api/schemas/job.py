from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class JobSpec(BaseModel):
    name: str
    owner: str
    team: str
    priority: Literal["low", "normal", "high"] = "normal"
    resources: dict[str, Any] | None = None
    limits: dict[str, Any] | None = None
    env: dict[str, str] | None = None
    runtime: dict[str, Any]
    artifacts: list[str] | None = None
    tags: list[str] | None = None


class JobCreate(BaseModel):
    yaml: str | None = None
    spec: JobSpec | None = None


class JobOut(BaseModel):
    id: str
    name: str
    team_id: str
    owner_id: str
    priority: str
    state: str
    queued_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

    class Config:
        from_attributes = True


class JobListOut(BaseModel):
    items: list[JobOut]
    total: int
    page: int
    limit: int
