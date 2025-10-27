from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import heapq

from apps.api.models.policy import Policy
from apps.api.models.job import Job
from apps.api.models.metric import RunnerMetric
from apps.api.schemas.policy import PolicyIn


def list_policies(db: Session) -> list[Policy]:
    return db.query(Policy).order_by(Policy.created_at.desc()).all()


def upsert_policy(db: Session, data: PolicyIn, created_by: str = "system") -> Policy:
    p = Policy(name=data.name, match=data.match, rules=data.rules.model_dump(), created_by=created_by)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _parse_wall_time_to_seconds(value) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str) and value.count(":") == 2:
        h, m, s = value.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    return 0


def _job_matches(match: dict, job: Job) -> bool:
    if not match:
        return True
    if (team := match.get("team")) and team != job.team_id:
        return False
    if (owner := match.get("owner")) and owner != job.owner_id:
        return False
    if (priority := match.get("priority")) and priority != job.priority:
        return False
    if (tags := match.get("tags")):
        try:
            spec_tags = (job.spec or {}).get("tags", [])
            if not all(t in spec_tags for t in tags):
                return False
        except Exception:
            return False
    return True


def dry_run(db: Session, data: PolicyIn, days: int = 7) -> dict:
    window_start = datetime.utcnow() - timedelta(days=days)
    jobs: list[Job] = (
        db.query(Job)
        .filter(or_(Job.queued_at == None, Job.queued_at > window_start))
        .all()
    )

    matched = [j for j in jobs if _job_matches(data.match, j)]
    would_allow = 0
    would_deny = 0
    violations_by_rule: dict[str, int] = {}
    examples: list[dict] = []

    rules = data.rules.model_dump()
    max_wall = _parse_wall_time_to_seconds(rules.get("max_wall_time")) if rules.get("max_wall_time") else None
    max_conc = rules.get("max_concurrent_gpu_jobs")
    deny_thermal = rules.get("deny_if_device_thermal_state")

    for j in matched:
        violated = False
        if max_wall:
            spec_lim = 0
            try:
                spec_lim = _parse_wall_time_to_seconds((j.spec or {}).get("limits", {}).get("wall_time"))
            except Exception:
                spec_lim = 0
            if spec_lim and spec_lim > max_wall:
                violated = True
                violations_by_rule["max_wall_time"] = violations_by_rule.get("max_wall_time", 0) + 1
                examples.append({"job_id": j.id, "reason": "spec wall_time exceeds policy"})
            elif j.started_at and j.finished_at:
                run_secs = int((j.finished_at - j.started_at).total_seconds())
                if run_secs > max_wall:
                    violated = True
                    violations_by_rule["max_wall_time"] = violations_by_rule.get("max_wall_time", 0) + 1
                    examples.append({"job_id": j.id, "reason": "actual runtime exceeds policy"})

        # thermal check (kinda hard to get actual thermals from machine it seems)
        if deny_thermal and j.runner_id and j.started_at and j.finished_at and not violated:
            cnt = (
                db.query(func.count(RunnerMetric.id))
                .filter(
                    RunnerMetric.runner_id == j.runner_id,
                    RunnerMetric.recorded_at >= j.started_at,
                    RunnerMetric.recorded_at <= j.finished_at,
                    RunnerMetric.thermal_state == deny_thermal,
                )
                .scalar()
                or 0
            )
            if cnt > 0:
                violated = True
                violations_by_rule["deny_if_device_thermal_state"] = violations_by_rule.get("deny_if_device_thermal_state", 0) + 1
                examples.append({"job_id": j.id, "reason": f"thermal {deny_thermal}"})

        if violated:
            would_deny += 1
        else:
            would_allow += 1

    if max_conc and data.match.get("team"):
        team = data.match.get("team")
        active = [j for j in matched if j.team_id == team and j.started_at and j.finished_at]
        active.sort(key=lambda x: x.started_at)
        heap: list[datetime] = []
        current = 0
        for j in active:
            while heap and heap[0] <= j.started_at:
                heapq.heappop(heap)
                current -= 1
            heapq.heappush(heap, j.finished_at)
            current += 1
            if current > int(max_conc):
                violations_by_rule["max_concurrent_gpu_jobs"] = violations_by_rule.get("max_concurrent_gpu_jobs", 0) + 1
                examples.append({"job_id": j.id, "reason": "concurrency would exceed policy"})

    return {
        "evaluated": len(matched),
        "would_allow": would_allow,
        "would_deny": would_deny,
        "violations_by_rule": violations_by_rule,
        "examples": examples[:10],
    }

