from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from apps.api.models.base import Base, IdMixin, TimestampMixin


class Job(Base, IdMixin, TimestampMixin):
    __tablename__ = "jobs"

    name: Mapped[str]
    owner_id: Mapped[str]
    team_id: Mapped[str]
    priority: Mapped[str] = mapped_column(default="normal")
    spec: Mapped[dict] = mapped_column(JSONB)
    state: Mapped[str] = mapped_column(default="QUEUED")
    queued_at: Mapped[datetime | None]
    started_at: Mapped[datetime | None]
    finished_at: Mapped[datetime | None]
    runner_id: Mapped[str | None]
    exit_code: Mapped[int | None]
    error: Mapped[str | None]

