## CoreQueue (Work In Progress)

End-to-end job orchestration platform with a FastAPI backend, Swift runner, and a typed web UI powered by Next.js, tRPC, React Query, and Zod.

### Features
- **API (FastAPI)**: Jobs, Runners, Metrics, Policies, Artifacts, Logs, Health.
- **Database (PostgreSQL + SQLAlchemy + Alembic)**: Versioned schema with core models (`Job`, `Runner`, `RunnerMetric`, `Policy`, `Team`, `User`).
- **Queueing (Redis)**: Jobs are queued and claimed by runners.
- **Runner (Swift)**: Registers, heartbeats/telemetry, claims jobs, executes commands, streams logs, uploads artifacts.
- **Web (Next.js)**: Dashboard, Jobs (table + detail), Submit, Runners, Policies. Strong typing via tRPC and Zod.
- **DX & Tooling**: Dark theme, reusable UI components, pre-commit hooks, Docker ignores, modular routers, centralized settings.

### Monorepo Structure
- `apps/api` — FastAPI application, models, routers, services, storage utilities, Alembic.
- `apps/web` — Next.js app with tRPC client, pages, components, and styling.
- `apps/runner` — Swift runner package and executable.
- `deploy/docker` — Dockerfiles and compose files for local/dev builds.
- `packages/common` — Shared frontend packages (if present in your setup).

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node and `pnpm`
- Swift (for the Runner)
- PostgreSQL and Redis 
- Optional: `uv` (for fast Python dependency management) and `pre-commit`

### Services (Postgres & Redis)
If you use Docker, bring up infra with the provided compose file:

```bash
docker compose -f deploy/docker/docker-compose.dev.yml up -d
```

### Environment
Create a `.env` in the repo root (or export env vars) with at least:

```bash
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/corequeue
REDIS_URL=redis://localhost:6379/0
DATA_DIR=.data
```

### Backend (API)

```bash
# From repo root
# Option A: using uv (recommended)
uv sync -p 3.11

# Option B: using pip (fallback)
python -m venv .venv && . .venv/bin/activate
pip install -e apps/api

# Apply migrations
alembic -c apps/api/alembic.ini upgrade head

# Run API (Hot reload)
uvicorn apps.api.main:app --reload
```

API base defaults to `http://127.0.0.1:8000`. Quick health check:

```bash
curl http://127.0.0.1:8000/alive
```

### Frontend (Web)

```bash
cd apps/web
pnpm install
pnpm dev
```

Then open `http://localhost:3000`.

### Runner (Swift) (WIP)

```bash
cd apps/runner
swift build
swift run corequeue-runner
```

The runner registers with the API, sends telemetry, claims jobs, executes their commands, and streams logs/artifacts.

---

## Usage

### Key Pages
- `/` — Landing page with quick navigation
- `/dashboard` — Metrics overview and recent violations
- `/jobs` — Paginated job table with filters
- `/jobs/[id]` — Job detail with live logs, artifacts, and cancellation
- `/submit` — Submit a job via form, JSON, or YAML
- `/runners` — Runner list with status and last seen
- `/policies` — List/apply policies, with dry run support

### Submit a Job (UI)
- Navigate to `/submit`
- Choose input mode: Form, JSON, or YAML
- Provide required fields (e.g., name, owner, team, priority, entrypoint)
- Submit and follow the link to the created job

### Submit a Job (API)

```bash
curl -X POST http://127.0.0.1:8000/jobs/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example",
    "owner": "michael",
    "team": "core",
    "priority": "normal",
    "spec": {
      "entrypoint": "echo Hello && sleep 2 && echo Done",
      "artifacts": ["output.log"],
      "env": {"EXAMPLE": "1"}
    },
    "tags": ["demo"],
    "wall_time": "00:10:00"
  }'
```

Equivalent YAML (via UI YAML mode):

```yaml
name: example
owner: michael
team: core
priority: normal
spec:
  entrypoint: echo Hello && sleep 2 && echo Done
  artifacts:
    - output.log
  env:
    EXAMPLE: "1"
tags:
  - demo
wall_time: 00:10:00
```

### Policies

List policies:

```bash
curl http://127.0.0.1:8000/policies
```

Apply (or dry run) a policy:

```bash
curl -X POST http://127.0.0.1:8000/policies/apply \
  -H "Content-Type: application/json" \
  -d '{
    "name": "default-wall-time",
    "match": {"team": "core"},
    "rules": {"max_wall_time": "01:00:00"},
    "dry_run_only": true
  }'
```

### Metrics Overview

```bash
curl "http://127.0.0.1:8000/metrics/overview?hours=24"
```

### Runners

```bash
curl http://127.0.0.1:8000/runners
```

---

## Architecture Highlights
- **Settings**: Centralized via `pydantic-settings` with `get_settings()` and `.env` support.
- **Routers**: Modular (`health`, `jobs`, `runners`, `metrics`, `policies`).
- **Services**: `job_service` (submit, parse wall time, queue, cancel) and `policy_service` (list, apply, dry run).
- **Storage**: Utilities for job artifacts and logs with safe paths.
- **Schemas**: Pydantic for API; Zod for frontend validation.
- **tRPC**: Typed procedures for jobs, runners, metrics, policies.

---

## Development

### Pre-commit Hooks

```bash
pipx install pre-commit || pip install pre-commit
pre-commit install
```

Hooks include Black, isort, pyupgrade, Prettier, and whitespace/EOF fixers.

### Migrations

```bash
# Create a new migration (example)
alembic -c apps/api/alembic.ini revision -m "your message"

# Apply latest
alembic -c apps/api/alembic.ini upgrade head
```

### Common Issues
- Ensure `DATABASE_URL` and `REDIS_URL` are reachable before starting API/Runner.
- If migrations fail, verify that Alembic points to app metadata in `env.py` and that your virtualenv contains `apps/api`.
- When running the web app from the repo root workspace, prefer `cd apps/web && pnpm dev` to avoid workspace filter mismatches.

---

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).
