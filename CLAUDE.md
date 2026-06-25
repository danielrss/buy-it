# buy-it - Claude Code notes

## Project

FastAPI backend for the buy-it e-commerce platform. Python 3.13, `src/` layout, managed with `uv`.

## Libraries

| Package | Min version | Locked | Role |
|---|---|---|---|
| `fastapi` | >=0.115 | 0.138.0 | Web framework |
| `uvicorn[standard]` | >=0.32 | 0.49.0 | ASGI server (Docker only) |
| `pydantic-settings` | >=2.6 | 2.14.2 | Settings / config |
| `pytest` | >=8.3 | 9.1.1 | Test runner |
| `pytest-asyncio` | >=0.24 | 1.4.0 | Async test support |
| `httpx` | >=0.28 | 0.28.1 | HTTP client for integration tests |
| `ruff` | >=0.8 | 0.15.19 | Linter + formatter |
| `pyright` | >=1.1 | 1.1.410 | Type checker (convert to `ty` when it has an official release) |

### The app runs ONLY in Docker
There is no local uvicorn recipe. Virtual environment is used only for tests/lint/typecheck/autocomplete.

```bash
just up      # docker compose up --build
just down    # docker compose down
just logs    # docker compose logs -f api
```

### No pre-commit hooks
Skipped by choice. Run quality checks manually before committing:
```bash
just check   # lint + typecheck + test
```

### Run `just fmt` after every file edit

### Tests are split unit / integration
```bash
just test-unit   # tests/unit/   - fast, no app/HTTP
just test-int    # tests/integration/ - through the ASGI app via httpx
just test        # both
```

## Project structure

```
buy-it/
├── src/app/
│   ├── config.py           # pydantic-settings Settings + cached get_settings()
│   ├── main.py             # create_app() factory; module-level app = create_app() for uvicorn
│   └── api/
│       ├── deps.py         # FastAPI DI wiring point - add Depends() providers here
│       └── routes/
│           └── health.py   # GET /health → {"status": "ok"}
├── tests/
│   ├── conftest.py             # shared fixtures (settings, etc.)
│   ├── unit/
│   │   └── test_config.py      # Settings defaults + env override
│   └── integration/
│       ├── conftest.py         # AsyncClient fixture (ASGITransport from create_app())
│       └── test_health.py
├── Dockerfile                  # multi-stage, uv, non-root user "app"
├── docker-compose.yml
├── justfile                    # task shortcuts
├── pyproject.toml              # deps + ruff + pyright + pytest config
├── .python-version             # 3.13
└── ARCHITECTURE.md             # target layering + product-search example
```

### App factory pattern
`create_app()` in `main.py` builds and returns the `FastAPI` instance. This keeps the app testable (each test gets a fresh instance) and the DI wiring clean. The module-level `app = create_app()` is only for uvicorn's entry point.

### DI wiring point
`api/deps.py` is intentionally sparse now. It is the single place to add FastAPI `Depends()` providers as features land - services, DB sessions, repositories, etc.

### Configuration
`core/config.py` exports `get_settings()` (LRU-cached). Settings read from env or `.env`. Available variables: `ENVIRONMENT`.
## Adding a new feature

See `ARCHITECTURE.md` for the full pattern with a product-search example. The short version:

1. Add `src/app/domain/` - pure dataclasses/Protocols, zero framework imports.
2. Add `src/app/services/` - business logic, depends on domain Protocols.
3. Add `src/app/infrastructure/` - concrete repository implementations (SQL, etc.).
4. Wire the service into `api/deps.py` via `Depends()`.
5. Add an `APIRouter` under `api/routes/` and register it in `create_app()`.
6. Unit-test the service with a fake in-memory repository; integration-test the route.

**Rule:** add layers with the first real feature - don't pre-build empty folders.

## Common commands

| Command | What it does |
|---|---|
| `just up` | Build image and start the app in Docker |
| `just down` | Stop containers |
| `just logs` | Tail api logs |
| `just test` | Run all tests |
| `just test-unit` | Unit tests only |
| `just test-int` | Integration tests only |
| `just lint` | `ruff check src tests` |
| `just fmt` | `ruff format src tests` |
| `just typecheck` | `pyright` |
| `just check` | lint + typecheck + test |
| `just cleanup-local` | Remove `.venv`, tool caches, `__pycache__` |
| `just cleanup-docker` | Remove project containers, images, volumes, networks |
| `just cleanup` | `cleanup-local` + `cleanup-docker` |
| `uv sync` | Install / refresh deps into `.venv` |
| `uv add <pkg>` | Add a runtime dep |
| `uv add --dev <pkg>` | Add a dev dep |
