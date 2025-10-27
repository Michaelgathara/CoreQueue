from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB

from apps.api.models.base import Base, IdMixin, TimestampMixin


class Policy(Base, IdMixin, TimestampMixin):
    __tablename__ = "policies"

    name: Mapped[str]
    match: Mapped[dict] = mapped_column(JSONB)
    rules: Mapped[dict] = mapped_column(JSONB)
    version: Mapped[int] = mapped_column(default=1)
    created_by: Mapped[str] = mapped_column(default="system")

