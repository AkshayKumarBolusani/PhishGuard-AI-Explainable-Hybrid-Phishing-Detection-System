.PHONY: help dev backend frontend install lint test docker clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---- Development ----

dev: ## Run backend and frontend concurrently
	@echo "Starting backend..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
	@echo "Starting frontend..."
	cd frontend && npm run dev &
	@wait

backend: ## Run backend only
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Run frontend only
	cd frontend && npm run dev

# ---- Setup ----

install: ## Install all dependencies
	cd backend && pip install -e ".[dev]"
	cd frontend && npm install

install-backend: ## Install backend dependencies
	cd backend && pip install -e ".[dev]"

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

# ---- Quality ----

lint: ## Run all linters
	cd backend && ruff check app/ tests/
	cd backend && black --check app/ tests/
	cd backend && isort --check app/ tests/

format: ## Auto-format code
	cd backend && black app/ tests/
	cd backend && isort app/ tests/
	cd backend && ruff check --fix app/ tests/

# ---- Testing ----

test: ## Run all tests
	cd backend && pytest --cov=app --cov-report=term-missing -v

test-ai: ## Run AI pipeline tests
	cd backend && pytest tests/test_ai/ -v

test-api: ## Run API tests
	cd backend && pytest tests/test_api/ -v

coverage: ## Generate HTML coverage report
	cd backend && pytest --cov=app --cov-report=html
	@echo "Open backend/htmlcov/index.html"

# ---- Docker ----

docker: ## Build and run with Docker Compose
	docker compose up --build

docker-down: ## Stop Docker Compose
	docker compose down

docker-clean: ## Remove Docker volumes and images
	docker compose down -v --rmi all

# ---- Training ----

train: ## Train ML models
	cd backend && python -m app.ai.models.train

# ---- Cleanup ----

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf backend/.pytest_cache backend/htmlcov backend/.coverage
	rm -rf frontend/dist frontend/node_modules/.cache
