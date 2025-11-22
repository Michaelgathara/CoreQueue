from io import BytesIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from apps.api.core.config import get_settings
from apps.api.core.db import get_session
from apps.api.schemas.job import JobCreate, JobListOut, JobOut
from apps.api.services.job_service import (
    cancel_job,
    create_job,
    get_job,
    parse_job_create,
)
from apps.api.storage.artifacts import list_artifacts, read_artifact, write_artifact
from apps.api.storage.logs import append_log_line, read_log

router = APIRouter()


@router.post("/jobs/{job_id}/artifacts")
async def upload_artifact(job_id: str, file: UploadFile = File(...)):
    settings = get_settings()
    data = await file.read()
    write_artifact(settings, job_id, file.filename, data)
    return {"ok": True, "filename": file.filename}


@router.get("/jobs/{job_id}/artifacts")
def list_job_artifacts(job_id: str):
    settings = get_settings()
    items = list_artifacts(settings, job_id)
    return {"artifacts": items}


@router.get("/jobs/{job_id}/artifacts/{filename}")
def download_artifact(job_id: str, filename: str):
    settings = get_settings()
    # Also returns bytes now, not a Path
    data = read_artifact(settings, job_id, filename)
    if not data:
        raise HTTPException(status_code=404, detail="artifact not found")

    return StreamingResponse(BytesIO(data), media_type="application/octet-stream")


@router.get("/jobs/{job_id}/logs")
def get_logs(job_id: str, max_bytes: int | None = None):
    settings = get_settings()
    data = read_log(settings, job_id, max_bytes)
    return StreamingResponse(iter([data]), media_type="text/plain")


@router.post("/jobs/{job_id}/logs/append")
def append_logs(job_id: str, body: dict):
    settings = get_settings()
    line = body.get("line") or body.get("chunk")
    if not isinstance(line, str):
        raise HTTPException(status_code=400, detail="line required")
    append_log_line(settings, job_id, line)
    return {"ok": True}


@router.post("/jobs/submit", response_model=JobOut)
def submit_job(body: JobCreate, db: Session = Depends(get_session)):
    try:
        spec = parse_job_create(body)
        job = create_job(db, spec)
        return JobOut.model_validate(job)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs", response_model=JobListOut)
def list_jobs(
    db: Session = Depends(get_session),
    state: str | None = None,
    team: str | None = None,
    owner: str | None = None,
    page: int = 1,
    limit: int = 20,
):
    from apps.api.models.job import Job

    query = db.query(Job)
    if state:
        query = query.filter(Job.state == state)
    if team:
        query = query.filter(Job.team_id == team)
    if owner:
        query = query.filter(Job.owner_id == owner)

    total = query.count()
    offset = (page - 1) * limit
    rows = query.order_by(Job.queued_at.desc()).offset(offset).limit(limit).all()

    return JobListOut(
        total=total,
        page=page,
        limit=limit,
        data=[JobOut.model_validate(j) for j in rows],
    )


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job_status(job_id: str, db: Session = Depends(get_session)):
    job = get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobOut.model_validate(job)


@router.post("/jobs/{job_id}/cancel", response_model=JobOut)
def cancel_job_endpoint(job_id: str, db: Session = Depends(get_session)):
    job = cancel_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return JobOut.model_validate(job)
