FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY apps/worker/requirements.txt ./apps/worker/requirements.txt
RUN pip install -r apps/worker/requirements.txt

COPY apps/worker ./apps/worker
COPY packages/common ./packages/common

ENV PYTHONPATH=/app

CMD ["python", "-m", "apps.worker.main"]

