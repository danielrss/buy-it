set dotenv-load := false

REQUIRED_PYTHON := "3.13"

# Verify the active Python major.minor matches .python-version
[private]
check-python:
    @uv run python -c "import sys; v=str(sys.version_info.major)+'.'+str(sys.version_info.minor); req='{{ REQUIRED_PYTHON }}'; sys.exit(0) if v==req else (print('Python '+req+' required, got '+v) or sys.exit(1))"

# Build images and start the app in Docker
up:
    docker compose up --build

run: up

# Stop and remove containers
down:
    docker compose down

# View logs for the API container
logs:
    docker compose logs -f api

# Run all tests
test: check-python
    uv run pytest -v

# Run unit tests only
test-unit: check-python
    uv run pytest tests/unit -v

# Run integration tests only
test-int: check-python
    uv run pytest tests/integration -v

# Run linting checks
lint: check-python
    uv run ruff check src tests

# Run type checking
typecheck: check-python
    uv run pyright

# Run lint + typecheck + tests
check: lint typecheck test

# Run code formatting
fmt: check-python
    uv run ruff format src tests

# Remove venv, tool caches, and compiled Python files
cleanup-local:
    rm -rf .venv .pytest_cache .ruff_cache
    find src tests -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Remove all Docker artifacts created by this project (containers, images, volumes, networks)
cleanup-docker:
    docker compose down --rmi all --volumes --remove-orphans

# Cleanup local environment and Docker artifacts
cleanup: cleanup-local cleanup-docker