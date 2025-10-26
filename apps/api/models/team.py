from sqlalchemy.orm import Mapped, mapped_column

from apps.api.models.base import Base, IdMixin, TimestampMixin


class Team(Base, IdMixin, TimestampMixin):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(unique=True)
    tier: Mapped[str] = mapped_column(default="standard")

