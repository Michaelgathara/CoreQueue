from datetime import datetime
import yaml
from sqlalchemy.orm import Session

from apps.api.models.job import Job
from apps.api.schemas.job import JobCreate, JobSpec
from apps.api.clients.redis_client import get_redis


def parse_job_create(body: JobCreate) -> JobSpec:
    if body.spec is not None:
        return body.spec
    if body.yaml is not None:
        data = yaml.safe_load(body.yaml)
        return JobSpec(**data)
    raise ValueError("spec or yaml required")


def create_job(db: Session, spec: JobSpec) -> Job:
    job = Job(
        name=spec.name,
        owner_id=spec.owner,
        team_id=spec.team,
        priority=spec.priority,
        spec=spec.model_dump(),
        state="QUEUED",
        queued_at=datetime.utcnow(),
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    r = get_redis()
    r.lpush("queue:jobs:default", job.id)
    return job


def get_job(db: Session, job_id: str) -> Job | None:
    return db.get(Job, job_id)


def cancel_job(db: Session, job_id: str) -> Job | None:
    job = db.get(Job, job_id)
    if not job:
        return None
    if job.state in ("SUCCEEDED", "FAILED", "CANCELLED"):
        return job
    job.state = "CANCELLED"
    job.finished_at = datetime.utcnow()
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

