from pydantic import BaseModel, Field
from typing import Any, Literal


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
    queued_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None

    class Config:
        from_attributes = True

