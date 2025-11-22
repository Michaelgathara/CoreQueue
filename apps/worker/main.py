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


def reap_zombies(conn: psycopg.Connection) -> None:
    """
    Find jobs stuck in RUNNING state where the runner hasn't checked in recently.
    Mark them as FAILED.
    """
    # If a runner hasn't sent a heartbeat in 60 seconds, assume it's dead.
    # Note: Runners typically heartbeat every 5s.
    threshold_seconds = 60

    sql = """
    SELECT j.id, j.runner_id
    FROM jobs j
    JOIN runners r ON j.runner_id = r.id
    WHERE j.state = 'RUNNING'
      AND (r.last_seen IS NULL OR r.last_seen < NOW() - INTERVAL '%s seconds')
    """

    with conn.cursor() as cur:
        cur.execute(sql, (threshold_seconds,))
        zombies = cur.fetchall()

        for job_id, runner_id in zombies:
            print(f"Reaping zombie job {job_id} (runner {runner_id} lost)")
            cur.execute(
                """
                UPDATE jobs
                SET state='FAILED',
                    finished_at=NOW(),
                    error='Runner lost connection (zombie detected)'
                WHERE id=%s
                """,
                (job_id,),
            )

    conn.commit()


def _parse_wall_time(val: str | int | None) -> int:
    """
    Parse HH:MM:SS or seconds int into total seconds.
    Defaults to 1 hour (3600) if invalid/missing.
    """
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.count(":") == 2:
        try:
            h, m, s = val.split(":")
            return int(h) * 3600 + int(m) * 60 + int(s)
        except ValueError:
            pass
    return 3600  # default fallback


def enforce_timeouts(conn: psycopg.Connection) -> None:
    """
    Find jobs that have been running longer than their wall_time limit.
    Mark them as FAILED.
    """
    sql = "SELECT id, spec, started_at FROM jobs WHERE state = 'RUNNING'"

    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()

        now = time.time()

        for job_id, spec, started_at in rows:
            if not started_at:
                continue

            job_spec = {}
            if isinstance(spec, str):
                try:
                    job_spec = json.loads(spec)
                except Exception:
                    pass
            elif isinstance(spec, dict):
                job_spec = spec

            limits = job_spec.get("limits", {})
            wall_time_input = limits.get("wall_time")

            if not wall_time_input:
                wall_time_input = job_spec.get("wall_time")

            limit_seconds = _parse_wall_time(wall_time_input)
            duration = now - started_at.timestamp()

            if duration > limit_seconds:
                print(
                    f"Job {job_id} timed out (ran for {duration:.0f}s, limit {limit_seconds}s)"
                )
                cur.execute(
                    """
                    UPDATE jobs
                    SET state='FAILED',
                        finished_at=NOW(),
                        error='Wall time exceeded'
                    WHERE id=%s
                    """,
                    (job_id,),
                )

    conn.commit()


def prune_metrics(conn: psycopg.Connection) -> None:
    """
    Delete metrics older than retention period (default 7 days).
    """
    retention_days = int(os.getenv("METRIC_RETENTION_DAYS", "7"))
    sql = "DELETE FROM runner_metrics WHERE recorded_at < NOW() - INTERVAL '%s days'"

    with conn.cursor() as cur:
        cur.execute(sql, (retention_days,))
        if cur.rowcount > 0:
            print(f"Pruned {cur.rowcount} old metrics")

    conn.commit()


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url.startswith("postgresql+psycopg://"):
        db_url = db_url.replace("postgresql+psycopg://", "postgresql://", 1)
    r = redis.from_url(redis_url)

    last_maintenance_time = 0
    maintenance_interval = 30  # Run maintenance every 30 seconds

    with psycopg.connect(db_url) as conn:
        while True:
            now = time.time()
            if now - last_maintenance_time > maintenance_interval:
                try:
                    reap_zombies(conn)
                    enforce_timeouts(conn)
                    prune_metrics(conn)
                    last_maintenance_time = now
                except Exception as e:
                    print(f"Error in maintenance tasks: {e}")
                    conn.rollback()

            item = r.brpop("queue:jobs:default", timeout=2)
            if not item:
                continue

            _, job_id = item
            try:
                max_running = int(os.getenv("MAX_CONCURRENT_RUNNING_PER_TEAM", "2"))
                process_job(conn, job_id.decode("utf-8"), max_running)
            except Exception as e:
                print(f"Error processing job {job_id}: {e}")
                conn.rollback()


if __name__ == "__main__":
    main()
