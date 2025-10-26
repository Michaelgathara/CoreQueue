from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from apps.api.core.db import get_session
from apps.api.models.runner import Runner
from apps.api.models.metric import RunnerMetric


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
        db.query(Runner)
        .filter(Runner.name == name)
        .filter(Runner.host == host)
        .first()
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
    return {"runners": [{"id": r.id, "name": r.name, "status": r.status, "last_seen": r.last_seen} for r in rows]}


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
    m = RunnerMetric(runner_id=runner_id, cpu_usage=cpu, gpu_usage=gpu, mem_gb=mem, thermal_state=thermal, recorded_at=datetime.utcnow())
    db.add(m)
    db.commit()
    return {"ok": True}


@router.post("/runners/claim")
def claim_job(body: dict):
    # Placeholder: scheduler will assign jobs; return none for now
    return None

