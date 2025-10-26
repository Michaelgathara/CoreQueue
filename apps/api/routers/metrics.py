from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from apps.api.core.db import get_session
from apps.api.models.metric import RunnerMetric
from apps.api.models.job import Job


router = APIRouter()


@router.get("/metrics/overview")
def metrics_overview(hours: int = 1, db: Session = Depends(get_session)):
    since = datetime.utcnow() - timedelta(hours=hours)
    cpu_avg = db.query(func.avg(RunnerMetric.cpu_usage)).filter(RunnerMetric.recorded_at > since).scalar() or 0.0
    gpu_avg = db.query(func.avg(RunnerMetric.gpu_usage)).filter(RunnerMetric.recorded_at > since).scalar() or 0.0
    queue_time_avg = db.query(func.avg(func.extract('epoch', Job.started_at - Job.queued_at))).filter(Job.started_at.isnot(None)).scalar() or 0.0
    run_time_avg = db.query(func.avg(func.extract('epoch', Job.finished_at - Job.started_at))).filter(Job.finished_at.isnot(None)).scalar() or 0.0
    return {
        "cpu_avg": cpu_avg,
        "gpu_avg": gpu_avg,
        "queue_time_avg_sec": queue_time_avg,
        "run_time_avg_sec": run_time_avg,
    }

