.PHONY: up down api web worker migrate fmt test

up:
	docker compose -f deploy/docker/docker-compose.dev.yml up --build

down:
	docker compose -f deploy/docker/docker-compose.dev.yml down -v

api:
	docker compose -f deploy/docker/docker-compose.dev.yml up api

web:
	docker compose -f deploy/docker/docker-compose.dev.yml up web

worker:
	docker compose -f deploy/docker/docker-compose.dev.yml up worker

