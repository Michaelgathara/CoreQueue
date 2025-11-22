from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    allowed_origins: str = Field(
        default="http://localhost:3000", alias="ALLOWED_ORIGINS"
    )
    jwt_secret: str = Field(default="change_me", alias="JWT_SECRET")
    jwt_expire_min: int = Field(default=60, alias="JWT_EXPIRE_MIN")
    data_root: str = Field(default="/data", alias="DATA_ROOT")
    max_concurrent_running_per_team: int = Field(
        default=2, alias="MAX_CONCURRENT_RUNNING_PER_TEAM"
    )
    max_wall_time_sec: int = Field(default=7200, alias="MAX_WALL_TIME_SEC")

    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")  # local, s3
    s3_endpoint_url: str | None = Field(default=None, alias="S3_ENDPOINT_URL")
    s3_bucket_name: str | None = Field(default=None, alias="S3_BUCKET_NAME")
    s3_access_key_id: str | None = Field(default=None, alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str | None = Field(default=None, alias="S3_SECRET_ACCESS_KEY")
    s3_region: str | None = Field(default="us-east-1", alias="S3_REGION")

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[arg-type]
