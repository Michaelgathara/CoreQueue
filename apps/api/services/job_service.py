from datetime import datetime
import yaml
from sqlalchemy.orm import Session

from apps.api.models.job import Job
from apps.api.schemas.job import JobCreate, JobSpec


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
    return job


def get_job(db: Session, job_id: str) -> Job | None:
    return db.get(Job, job_id)

