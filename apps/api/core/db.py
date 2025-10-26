from sqlalchemy.orm.session import Session


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from typing import Iterator

from apps.api.core.config import get_settings


def get_engine():
    settings = get_settings()
    return create_engine(settings.database_url, pool_pre_ping=True, poolclass=NullPool)


engine = get_engine()
SessionLocal = sessionmaker[Session](bind=engine, autoflush=False, autocommit=False)


def get_session() -> Iterator["Session"]:
    from sqlalchemy.orm import Session

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

