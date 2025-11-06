from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from apps.api.core.db import get_session
from apps.api.models.job import Job
from apps.api.models.metric import RunnerMetric
from apps.api.models.policy import Policy

router = APIRouter()


@router.get("/metrics/overview")
def metrics_overview(hours: int = 1, db: Session = Depends(get_session)):
    since = datetime.utcnow() - timedelta(hours=hours)
    cpu_avg = (
        db.query(func.avg(RunnerMetric.cpu_usage))
        .filter(RunnerMetric.recorded_at > since)
        .scalar()
        or 0.0
    )
    gpu_avg = (
        db.query(func.avg(RunnerMetric.gpu_usage))
        .filter(RunnerMetric.recorded_at > since)
        .scalar()
        or 0.0
    )
    queue_time_avg = (
        db.query(func.avg(func.extract("epoch", Job.started_at - Job.queued_at)))
        .filter(Job.started_at.isnot(None))
        .scalar()
        or 0.0
    )
    run_time_avg = (
        db.query(func.avg(func.extract("epoch", Job.finished_at - Job.started_at)))
        .filter(Job.finished_at.isnot(None))
        .scalar()
        or 0.0
    )
    violations = {
        "max_wall_time": 0,
        "deny_if_device_thermal_state": 0,
        "max_concurrent_gpu_jobs": 0,
    }
    recent_jobs = db.query(Job).filter(Job.finished_at > since).all()
    for j in recent_jobs:
        if j.started_at and j.finished_at:
            if (j.finished_at - j.started_at).total_seconds() > 7200:  # default max
                violations["max_wall_time"] += 1
        if j.runner_id and j.started_at and j.finished_at:
            cnt = (
                db.query(func.count(RunnerMetric.id))
                .filter(
                    RunnerMetric.runner_id == j.runner_id,
                    RunnerMetric.recorded_at >= j.started_at,
                    RunnerMetric.recorded_at <= j.finished_at,
                    RunnerMetric.thermal_state == "critical",
                )
                .scalar()
                or 0
            )
            if cnt > 0:
                violations["deny_if_device_thermal_state"] += 1

    return {
        "cpu_avg": cpu_avg,
        "gpu_avg": gpu_avg,
        "queue_time_avg_sec": queue_time_avg,
        "run_time_avg_sec": run_time_avg,
        "violations": violations,
    }
