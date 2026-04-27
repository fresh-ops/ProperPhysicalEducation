.PHONY: help lint fmt fmt-check typecheck test check fix ci run

help:
	@echo "Available targets:"
	@echo "  make lint       - Run Ruff linter"
	@echo "  make fmt        - Format code with Ruff"
	@echo "  make fmt-check  - Check formatting without changing files"
	@echo "  make typecheck  - Run mypy"
	@echo "  make test       - Run pytest"
	@echo "  make check      - Run all checks (lint + fmt-check + typecheck + test)"
	@echo "  make fix        - Auto-fix lint issues and format"
	@echo "  make ci         - Alias for make check"
	@echo "  make run        - Run the application"
	@echo "  make docker-up   - Build and start Docker containers"
	@echo "  make docker-down - Stop and remove Docker containers"
	@echo "  make docker-logs - Follow logs of Docker containers"

lint:
	uv run ruff check .

fmt:
	uv run ruff format .

fmt-check:
	uv run ruff format --check .

typecheck:
	uv run mypy .

test:
	@uv run pytest -q; \
	code=$$?; \
	if [ $$code -eq 5 ]; then \
		echo "No tests collected (treated as success)"; \
		exit 0; \
	fi; \
	exit $$code

check: lint fmt-check typecheck test

fix:
	uv run ruff check --fix .
	uv run ruff format .

ci: check

run:
	uv run uvicorn composition.main:app --host 0.0.0.0 --port 8000

docker-up:
	docker compose up --build

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f 