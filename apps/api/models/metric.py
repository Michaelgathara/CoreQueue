from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.models.base import Base, IdMixin


class RunnerMetric(Base, IdMixin):
    __tablename__ = "runner_metrics"

    runner_id: Mapped[str] = mapped_column(ForeignKey("runners.id"))
    cpu_usage: Mapped[float]
    gpu_usage: Mapped[float]
    mem_gb: Mapped[float]
    thermal_state: Mapped[str]
    recorded_at: Mapped[datetime]
