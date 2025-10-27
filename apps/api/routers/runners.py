from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from apps.api.clients.redis_client import get_redis
from apps.api.core.db import get_session
from apps.api.models.job import Job
from apps.api.models.metric import RunnerMetric
from apps.api.models.runner import Runner

router = APIRouter()


@router.post("/runners/register")
def register_runner(body: dict, db: Session = Depends(get_session)):
    name = body.get("name")
    host = body.get("host")
    arch = body.get("arch", "arm64")
    gpu_class = body.get("gpu_class", "apple-silicon")
    if not name or not host:
        raise HTTPException(status_code=400, detail="name and host required")
    existing = (
        db.query(Runner).filter(Runner.name == name).filter(Runner.host == host).first()
    )
    if existing:
        return {"id": existing.id}
    runner = Runner(name=name, host=host, arch=arch, gpu_class=gpu_class, status="idle")
    db.add(runner)
    db.commit()
    db.refresh(runner)
    return {"id": runner.id}


@router.get("/runners")
def list_runners(db: Session = Depends(get_session)):
    rows = db.query(Runner).all()
    return {
        "runners": [
            {"id": r.id, "name": r.name, "status": r.status, "last_seen": r.last_seen}
            for r in rows
        ]
    }


@router.post("/runners/telemetry")
def ingest_telemetry(body: dict, db: Session = Depends(get_session)):
    runner_id = body.get("runner_id")
    cpu = float(body.get("cpu_usage", 0.0))
    gpu = float(body.get("gpu_usage", 0.0))
    mem = float(body.get("mem_gb", 0.0))
    thermal = body.get("thermal_state", "unknown")
    if not runner_id:
        raise HTTPException(status_code=400, detail="runner_id required")
    r = db.get(Runner, runner_id)
    if not r:
        raise HTTPException(status_code=404, detail="runner not found")
    r.last_seen = datetime.utcnow()
    db.add(r)
    m = RunnerMetric(
        runner_id=runner_id,
        cpu_usage=cpu,
        gpu_usage=gpu,
        mem_gb=mem,
        thermal_state=thermal,
        recorded_at=datetime.utcnow(),
    )
    db.add(m)
    db.commit()
    return {"ok": True}


@router.post("/runners/claim")
def claim_job(body: dict, db: Session = Depends(get_session)):
    runner_id = body.get("runner_id")
    if not runner_id:
        raise HTTPException(status_code=400, detail="runner_id required")
    r = get_redis()
    item = r.brpop(f"runner:{runner_id}:assignments", timeout=1)
    if not item:
        return {"job": None}
    _, raw = item
    import json

    data = json.loads(raw)
    job_id = data.get("job_id")
    job = db.get(Job, job_id)
    if not job:
        return {"job": None}
    if job.state != "QUEUED":
        return {"job": None}
    job.state = "CLAIMED"
    job.runner_id = runner_id
    db.add(job)
    db.commit()
    return {"job_id": job.id, "spec": job.spec}


@router.post("/runners/started")
def runner_started(body: dict, db: Session = Depends(get_session)):
    job_id = body.get("job_id")
    runner_id = body.get("runner_id")
    if not job_id or not runner_id:
        raise HTTPException(status_code=400, detail="job_id and runner_id required")
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    job.state = "RUNNING"
    job.started_at = datetime.utcnow()
    job.runner_id = runner_id
    db.add(job)
    db.commit()
    return {"ok": True}


@router.post("/runners/finished")
def runner_finished(body: dict, db: Session = Depends(get_session)):
    job_id = body.get("job_id")
    runner_id = body.get("runner_id")
    exit_code = body.get("exit_code", 0)
    error = body.get("error")
    if not job_id or not runner_id:
        raise HTTPException(status_code=400, detail="job_id and runner_id required")
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    job.state = "SUCCEEDED" if int(exit_code) == 0 else "FAILED"
    job.finished_at = datetime.utcnow()
    job.runner_id = runner_id
    job.exit_code = int(exit_code)
    job.error = error
    db.add(job)
    db.commit()
    return {"ok": True}
