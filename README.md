# buy-it

A FastAPI backend for the buy-it e-commerce platform.

## Requirements

- [uv](https://docs.astral.sh/uv/) - package and project management
- [Docker](https://docs.docker.com/get-docker/) - the intended way to run the app
- [just](https://github.com/casey/just) *(optional)* - task runner shortcuts (```uv tool install rust-just```)

## Setup

```bash
uv sync          # install deps into .venv (for tests/lint/typecheck/autocomplete/running migrations)
```

## Running the app

The app is intended to run in Docker to ensure consistency on different environments:

```bash
just up          # build images and start the app in Docker
just down        # stop and remove containers
```

Or without just:

```bash
docker compose up --build
docker compose down
```

The API is available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

## Cleanup

```bash
just cleanup         # cleanup local environment and Docker artifacts - will delete your local DB!
just cleanup-local   # remove .venv, tool caches, and compiled Python files
just cleanup-docker  # remove project containers, images, volumes, and networks
```

## Testing

```bash
just test        # all tests
just test-unit   # unit tests only (fast, no app)
just test-int    # integration tests only (through the ASGI app)
```

## Code quality

```bash
just lint        # ruff check
just fmt         # ruff format
just typecheck   # pyright
just check       # lint + typecheck + unit tests
```

## Configuration

Settings are read from environment variables (or `.env`). Available variables:

| Variable            | Default   | Description                        |
|---------------------|-----------|------------------------------------|
| `ENVIRONMENT`       | `local`   | Runtime environment                |
| `POSTGRES_USER`     | `buyit`   | Postgres username                  |
| `POSTGRES_PASSWORD` | `buyit`   | Postgres password                  |
| `POSTGRES_DB`       | `buyit`   | Postgres database name             |
| `POSTGRES_HOST`     | `db`      | Postgres host                      |
| `POSTGRES_PORT`     | `5432`    | Postgres port                      |
| `MEDIA_ROOT`        | `media`   | Filesystem dir where uploads are stored |
| `MEDIA_URL_PREFIX`  | `/media`  | URL path prefix the media files are served under |
| `MEDIA_BASE_URL`    | `http://localhost:8000` | Origin prepended to make `image_url` an absolute URL |
| `MAX_IMAGE_BYTES`   | `1048576` | Max accepted image upload size in bytes (1 MiB) |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the target layered design and a worked example.
