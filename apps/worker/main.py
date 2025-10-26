import os
import time
import psycopg
import redis


def team_running_count(conn: psycopg.Connection, team_id: str) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT count(1) FROM jobs WHERE team_id=%s AND state='RUNNING'", (team_id,))
        row = cur.fetchone()
        return int(row[0]) if row else 0


def get_team_id(conn: psycopg.Connection, job_id: str) -> str:
    with conn.cursor() as cur:
        cur.execute("SELECT team_id FROM jobs WHERE id=%s", (job_id,))
        row = cur.fetchone()
        return row[0] if row else ""


def process_job(conn: psycopg.Connection, job_id: str, max_running_per_team: int) -> None:
    team_id = get_team_id(conn, job_id)
    if not team_id:
        return
    if team_running_count(conn, team_id) >= max_running_per_team:
        # defer: push back to tail
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.rpush("queue:jobs:default", job_id)
        return
    with conn.cursor() as cur:
        cur.execute("UPDATE jobs SET state='RUNNING', started_at=now() WHERE id=%s AND state='QUEUED'", (job_id,))
        cur.execute("UPDATE jobs SET state='SUCCEEDED', finished_at=now() WHERE id=%s AND state='RUNNING'", (job_id,))
        conn.commit()


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

