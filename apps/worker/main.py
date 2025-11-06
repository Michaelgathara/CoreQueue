import json
import os
import time

import psycopg
import redis


def team_running_count(conn: psycopg.Connection, team_id: str) -> int:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT count(1) FROM jobs WHERE team_id=%s AND state='RUNNING'", (team_id,)
        )
        row = cur.fetchone()
        return int(row[0]) if row else 0


def get_team_id(conn: psycopg.Connection, job_id: str) -> str:
    with conn.cursor() as cur:
        cur.execute("SELECT team_id FROM jobs WHERE id=%s", (job_id,))
        row = cur.fetchone()
        return row[0] if row else ""


def get_job_spec(conn: psycopg.Connection, job_id: str):
    with conn.cursor() as cur:
        cur.execute("SELECT spec FROM jobs WHERE id=%s", (job_id,))
        row = cur.fetchone()
        if not row:
            return {}
        spec = row[0]
        if isinstance(spec, str):
            try:
                return json.loads(spec)
            except Exception:
                return {}
        return spec


def select_runner(conn: psycopg.Connection) -> str | None:
    sql = """
    WITH latest AS (
      SELECT DISTINCT ON (runner_id)
        runner_id, cpu_usage, gpu_usage, thermal_state, recorded_at
      FROM runner_metrics
      ORDER BY runner_id, recorded_at DESC
    )
    SELECT r.id
    FROM runners r
    LEFT JOIN latest m ON m.runner_id = r.id
    WHERE r.status = 'idle'
    ORDER BY
      CASE m.thermal_state
        WHEN 'nominal' THEN 0
        WHEN 'fair' THEN 1
        WHEN 'serious' THEN 2
        WHEN 'critical' THEN 3
        ELSE 4
      END,
      COALESCE(m.cpu_usage, 1.0) + COALESCE(m.gpu_usage, 1.0) ASC,
      r.last_seen DESC NULLS LAST
    LIMIT 1
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        row = cur.fetchone()
        return row[0] if row else None


def select_runner_with_policy(
    conn: psycopg.Connection, deny_thermal: str | None
) -> str | None:
    base = """
    WITH latest AS (
      SELECT DISTINCT ON (runner_id)
        runner_id, cpu_usage, gpu_usage, thermal_state, recorded_at
      FROM runner_metrics
      ORDER BY runner_id, recorded_at DESC
    )
    SELECT r.id
    FROM runners r
    LEFT JOIN latest m ON m.runner_id = r.id
    WHERE r.status = 'idle'
    {thermal_clause}
    ORDER BY
      CASE m.thermal_state
        WHEN 'nominal' THEN 0
        WHEN 'fair' THEN 1
        WHEN 'serious' THEN 2
        WHEN 'critical' THEN 3
        ELSE 4
      END,
      COALESCE(m.cpu_usage, 1.0) + COALESCE(m.gpu_usage, 1.0) ASC,
      r.last_seen DESC NULLS LAST
    LIMIT 1
    """
    thermal_clause = ""
    params: tuple = ()
    if deny_thermal:
        thermal_clause = "AND (m.thermal_state IS NULL OR m.thermal_state <> %s)"
        params = (deny_thermal,)
    sql = base.format(thermal_clause=thermal_clause)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        return row[0] if row else None


def load_policies(conn: psycopg.Connection) -> list[dict]:
    with conn.cursor() as cur:
        cur.execute("SELECT name, match, rules FROM policies")
        rows = cur.fetchall()
    result = []
    for name, match, rules in rows:
        result.append({"name": name, "match": match or {}, "rules": rules or {}})
    return result


def effective_policy_for_team(conn: psycopg.Connection, team_id: str) -> dict:
    chosen: dict = {}
    for p in load_policies(conn):
        match = p.get("match") or {}
        if match.get("team") == team_id or match == {}:
            chosen = p
            if match.get("team") == team_id:
                break
    return chosen.get("rules", {})


def process_job(
    conn: psycopg.Connection, job_id: str, max_running_per_team: int
) -> None:
    team_id = get_team_id(conn, job_id)
    if not team_id:
        return
    rules = effective_policy_for_team(conn, team_id)
    policy_max = rules.get("max_concurrent_gpu_jobs")
    if policy_max is not None:
        try:
            max_running_per_team = int(policy_max)
        except Exception:
            pass
    if team_running_count(conn, team_id) >= max_running_per_team:
        # defer: push back to tail
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.rpush("queue:jobs:default", job_id)
        return
    deny_thermal = rules.get("deny_if_device_thermal_state")
    runner_id = select_runner_with_policy(conn, deny_thermal)
    if not runner_id:
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.rpush("queue:jobs:default", job_id)
        return
    # push assignment to per-runner queue; runner will claim and transition states
    r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    payload = {
        "job_id": job_id,
        "spec": get_job_spec(conn, job_id),
    }
    r.lpush(f"runner:{runner_id}:assignments", json.dumps(payload))


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://", 1)
    r = redis.from_url(redis_url)
    with psycopg.connect(db_url) as conn:
        while True:
            item = r.brpop("queue:jobs:default", timeout=2)
            if not item:
                time.sleep(0.5)
                continue
            _, job_id = item
            try:
                max_running = int(os.getenv("MAX_CONCURRENT_RUNNING_PER_TEAM", "2"))
                process_job(conn, job_id.decode("utf-8"), max_running)
            except Exception:
                conn.rollback()


if __name__ == "__main__":
    main()
