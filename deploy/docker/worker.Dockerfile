FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY apps/worker ./apps/worker
COPY packages/common ./packages/common

ENV PYTHONPATH=/app

RUN python -m pip install --upgrade pip && pip install requests redis orjson tenacity psycopg[binary]

CMD ["python", "-m", "apps.worker.main"]

