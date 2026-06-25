set dotenv-load := false

REQUIRED_PYTHON := "3.13"

# Verify the active Python major.minor matches .python-version
[private]
check-python:
    @uv run python -c "import sys; v=str(sys.version_info.major)+'.'+str(sys.version_info.minor); req='{{ REQUIRED_PYTHON }}'; sys.exit(0) if v==req else (print('Python '+req+' required, got '+v) or sys.exit(1))"

# Build images, apply DB migrations and start the app in Docker
up:
    docker compose up --build -d --wait db
    just migrate
    docker compose up --build

run: up

# Stop and remove containers
down:
    docker compose down

# View logs for the API container
logs:
    docker compose logs -f api

# Run unit + integration tests (spins up an ephemeral test DB)
test: test-unit test-int

# Run unit tests only (no DB, no api)
test-unit: check-python
    uv run pytest tests/unit -v

# Run integration tests only (spins up an ephemeral test DB, always tears it down)
test-int: check-python
    #!/usr/bin/env bash
    set -euo pipefail
    docker compose --profile test up -d --wait db-test
    trap 'docker compose --profile test rm -fsv db-test >/dev/null 2>&1 || true' EXIT
    export POSTGRES_HOST=localhost POSTGRES_PORT=5433 POSTGRES_DB=buyit_test
    uv run alembic upgrade head
    uv run pytest tests/integration -v

# Run linting checks
lint: check-python
    uv run ruff check app tests

# Run type checking
typecheck: check-python
    uv run pyright

# Run lint + typecheck + tests
check: lint typecheck test

# Run code formatting
fmt: check-python
    uv run ruff format app tests

# Remove venv, tool caches, and compiled Python files
cleanup-local:
    rm -rf .venv .pytest_cache .ruff_cache
    find app tests -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove project containers, built images, volumes, and networks
cleanup-docker:
    docker compose down --rmi local --volumes --remove-orphans

# Cleanup local environment and Docker artifacts (including DB)
cleanup: cleanup-local cleanup-docker

# Apply all pending migrations (runs against localhost:5432 - db container must be up)
migrate: check-python
    POSTGRES_HOST=localhost uv run alembic upgrade head

# Generate a new autogenerate migration (usage: just migration name=add_products)
migration name: check-python
    POSTGRES_HOST=localhost uv run alembic revision --autogenerate -m "{{name}}"

# Roll back the most recent migration
migrate-down: check-python
    POSTGRES_HOST=localhost uv run alembic downgrade -1
