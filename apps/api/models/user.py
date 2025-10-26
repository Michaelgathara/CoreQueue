from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from apps.api.models.base import Base, IdMixin, TimestampMixin


class User(Base, IdMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str]
    team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"))

