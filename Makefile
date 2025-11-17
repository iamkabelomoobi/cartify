# ----- CONFIG -----
PYTHON := python
PIP := pip
UVICORN_APP := app.main:app
VENV := .venv

# ----- HELP -----
.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make venv        - Create virtual environment (.venv)"
	@echo "  make activate    - Show command to activate venv"
	@echo "  make install     - Install dependencies from requirements.txt"
	@echo "  make freeze      - Export dependencies to requirements.txt"
	@echo "  make run         - Run FastAPI app with Uvicorn (reload)"
	@echo "  make db-up       - Start Postgres + Mailhog via docker-compose"
	@echo "  make db-down     - Stop docker-compose services"
	@echo "  make db-logs     - Tail docker-compose logs"
	@echo "  make fmt         - (Optional) Format code with black, isort if installed"

# ----- VENV & DEPENDENCIES -----
.PHONY: venv
venv:
	$(PYTHON) -m venv $(VENV)

.PHONY: activate
activate:
	@echo "Run: source $(VENV)/bin/activate"

.PHONY: install
install:
	$(PIP) install -r requirements.txt

.PHONY: freeze
freeze:
	$(PIP) freeze > requirements.txt

# ----- RUN APP -----
.PHONY: run
run:
	uvicorn $(UVICORN_APP) --reload

# ----- DOCKER: DB & MAILHOG -----
.PHONY: db-up
db-up:
	docker-compose up -d

.PHONY: db-down
db-down:
	docker-compose down

.PHONY: db-logs
db-logs:
	docker-compose logs -f

# ----- OPTIONAL: FORMAT -----
.PHONY: fmt
fmt:
	@echo "Running formatters (if installed)..."
	- black app
	- isort app
