# Cartify

A modern ⚡ FastAPI-powered backend for Cartify — a lightweight 🛒 e-commerce API with PostgreSQL 🐘, Docker 🐳, and a scalable architecture 🚀.

## What this repo contains

- A small FastAPI app serving a couple of endpoints (see `app/main.py`).
- A startup DB connectivity check: when the app boots it runs a trivial `SELECT 1` against your database and stores the result in `app.state.db_connected`.
- A simple health endpoint at `/health` and a welcome endpoint at `/`.

## Features

- FastAPI for fast, async-capable HTTP APIs
- SQLAlchemy for DB models and schema creation
- Docker-friendly (there's a `docker-compose.yml` at project root)

## Requirements

- Python 3.10+ (3.11 recommended)
- PostgreSQL (local or remote) or a running PostgreSQL service via Docker
- Docker & Docker Compose (if you prefer containerized setup)

Recommended Python packages (example):

- fastapi
- uvicorn[standard]
- sqlalchemy
- psycopg2-binary

You can install them locally with:

```zsh
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary
```

## Environment

The app reads its DB URL from the typical `DATABASE_URL` environment variable. Example values (replace with real credentials):

```bash
DATABASE_URL=postgresql://cartify_user:secretpassword@localhost:5432/cartify_db
```

If you run with Docker Compose, you can place environment variables into a `.env` file and Docker Compose will pick it up.

## Quickstart — Docker (recommended)

This project includes `docker-compose.yml`. The simplest way to bring up the app and a Postgres DB is:

```zsh
# build and start containers
docker compose up --build -d

# watch logs (optional)
docker compose logs -f
```

The API will be reachable at `http://localhost:8000` by default (if the compose file maps that port).

The service will attempt a DB connection on startup and log whether it succeeded. You can verify via the health endpoint:

```zsh
curl -s http://localhost:8000/health | jq
```

Expected JSON shape:

```json
{
  "status": "ok",
  "db_connected": true
}
```

If `db_connected` is `false`, check database credentials and that Postgres is reachable from the app container or host.

## Quickstart — Local (no Docker)

1. Create and activate a virtual environment (see earlier).
1. Export your `DATABASE_URL` value in the shell:

```zsh
export DATABASE_URL="postgresql://cartify_user:secretpassword@localhost:5432/cartify_db"
```

1. Start the app with Uvicorn:

```zsh
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://127.0.0.1:8000/` for the welcome endpoint and `http://127.0.0.1:8000/health` for the health check.

## Quickstart — Local (Makefile)

If you prefer using the included Makefile to simplify local setup and running, follow these steps:

```bash
make help        # see commands
make venv        # create .venv
source .venv/bin/activate
make install     # install deps
make db-up       # start Postgres + Mailhog
make run         # run FastAPI
```

This runs the sequence: create a virtualenv, activate it, install dependencies, start local services via docker-compose (Postgres + Mailhog), and run the FastAPI app with Uvicorn.

## Endpoints

- `GET /` — welcome endpoint. Returns a friendly message and the DB connection status.
- `GET /health` — returns `{ "status": "ok", "db_connected": <true|false> }`.

## Troubleshooting

- If the app logs show `Database connection failed during startup`, double-check `DATABASE_URL`, network connectivity, and that Postgres is accepting connections from the app (check host/port and firewall rules).
- When using Docker, ensure the DB container is fully ready. You can inspect DB logs with `docker compose logs db` (container name may vary).

## Next steps / Enhancements

- Add a `requirements.txt` or `pyproject.toml` for dependency management.
- Add Alembic for migrations and document how to run them.
- Add tests and a CI pipeline to validate the health and DB connectivity on push.

## License

This project does not include a license file. Add one (for example, an MIT license) if you intend to publish.
```<!-- filepath: /home/kabelo-moobi/Workspace/github/cartify/README.md -->
# Cartify

A modern ⚡ FastAPI-powered backend for Cartify — a lightweight 🛒 e-commerce API with PostgreSQL 🐘, Docker 🐳, and a scalable architecture 🚀.

## What this repo contains

- A small FastAPI app serving a couple of endpoints (see `app/main.py`).
- A startup DB connectivity check: when the app boots it runs a trivial `SELECT 1` against your database and stores the result in `app.state.db_connected`.
- A simple health endpoint at `/health` and a welcome endpoint at `/`.

## Features

- FastAPI for fast, async-capable HTTP APIs
- SQLAlchemy for DB models and schema creation
- Docker-friendly (there's a `docker-compose.yml` at project root)

## Requirements

- Python 3.10+ (3.11 recommended)
- PostgreSQL (local or remote) or a running PostgreSQL service via Docker
- Docker & Docker Compose (if you prefer containerized setup)

Recommended Python packages (example):

- fastapi
- uvicorn[standard]
- sqlalchemy
- psycopg2-binary

You can install them locally with:

```zsh
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary
```

## Environment

The app reads its DB URL from the typical `DATABASE_URL` environment variable. Example values (replace with real credentials):

```bash
DATABASE_URL=postgresql://cartify_user:secretpassword@localhost:5432/cartify_db
```

If you run with Docker Compose, you can place environment variables into a `.env` file and Docker Compose will pick it up.

## Quickstart — Docker (recommended)

This project includes `docker-compose.yml`. The simplest way to bring up the app and a Postgres DB is:

```zsh
# build and start containers
docker compose up --build -d

# watch logs (optional)
docker compose logs -f
```

The API will be reachable at `http://localhost:8000` by default (if the compose file maps that port).

The service will attempt a DB connection on startup and log whether it succeeded. You can verify via the health endpoint:

```zsh
curl -s http://localhost:8000/health | jq
```

Expected JSON shape:

```json
{
  "status": "ok",
  "db_connected": true
}
```

If `db_connected` is `false`, check database credentials and that Postgres is reachable from the app container or host.

## Quickstart — Local (no Docker)

1. Create and activate a virtual environment (see earlier).
1. Export your `DATABASE_URL` value in the shell:

```zsh
export DATABASE_URL="postgresql://cartify_user:secretpassword@localhost:5432/cartify_db"
```

1. Start the app with Uvicorn:

```zsh
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit `http://127.0.0.1:8000/` for the welcome endpoint and `http://127.0.0.1:8000/health` for the health check.

## Quickstart — Local (Makefile)

If you prefer using the included Makefile to simplify local setup and running, follow these steps:

```bash
make help        # see commands
make venv        # create .venv
source .venv/bin/activate
make install     # install deps
make db-up       # start Postgres + Mailhog
make run         # run FastAPI
```

This runs the sequence: create a virtualenv, activate it, install dependencies, start local services via docker-compose (Postgres + Mailhog), and run the FastAPI app with Uvicorn.

## Endpoints

- `GET /` — welcome endpoint. Returns a friendly message and the DB connection status.
- `GET /health` — returns `{ "status": "ok", "db_connected": <true|false> }`.

## Troubleshooting

- If the app logs show `Database connection failed during startup`, double-check `DATABASE_URL`, network connectivity, and that Postgres is accepting connections from the app (check host/port and firewall rules).
- When using Docker, ensure the DB container is fully ready. You can inspect DB logs with `docker compose logs db` (container name may vary).

## Next steps / Enhancements

- Add a `requirements.txt` or `pyproject.toml` for dependency management.
- Add Alembic for migrations and document how to run them.
- Add tests and a CI pipeline to validate the health and DB connectivity on push.

## License

This project does not include a license file. Add one (for example, an MIT license) if you intend to publish.