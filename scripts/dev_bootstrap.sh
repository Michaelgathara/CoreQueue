#!/usr/bin/env bash
set -euo pipefail

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env from .env.example"
fi

docker compose -f deploy/docker/docker-compose.dev.yml up --build -d
echo "Stack starting..."

