import os
import time
import psycopg
import redis


def process_job(conn: psycopg.Connection, job_id: str) -> None:
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
                process_job(conn, job_id.decode("utf-8"))
            except Exception:
                conn.rollback()


if __name__ == "__main__":
    main()

