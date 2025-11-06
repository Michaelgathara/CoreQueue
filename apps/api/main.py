from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.core.config import get_settings
from apps.api.core.paths import ensure_dirs
from apps.api.routers import health, jobs, metrics, policies, runners


def get_allowed_origins() -> list[str]:
    settings = get_settings()
    raw = settings.allowed_origins
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="CoreQueue API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    settings = get_settings()
    ensure_dirs(settings.data_root)


app.include_router(health.router)
app.include_router(jobs.router)
app.include_router(runners.router)
app.include_router(metrics.router)
app.include_router(policies.router)
