from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime, UniqueConstraint
from apps.api.models.base import Base, IdMixin, TimestampMixin


class Runner(Base, IdMixin, TimestampMixin):
    __tablename__ = "runners"
    __table_args__ = (
        UniqueConstraint("name", "host", name="uq_runner_name_host"),
    )

    name: Mapped[str]
    host: Mapped[str]
    arch: Mapped[str]
    gpu_class: Mapped[str]
    status: Mapped[str] = mapped_column(default="idle")
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(), nullable=True)
    team_id: Mapped[str | None]

