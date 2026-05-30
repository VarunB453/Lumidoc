.PHONY: help bootstrap dev dev-client dev-server build test lint clean docker-up docker-down

help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

bootstrap: ## First-time project setup
	bash scripts/bootstrap.sh

dev-client: ## Start client development server
	cd apps/client && npm run dev

dev-server: ## Start server development server
	cd apps/server && uvicorn app.main:app --reload --port 8000

build-client: ## Build client for production
	cd apps/client && npm run build

build-server: ## Build server Docker image
	docker build -f infrastructure/docker/server.Dockerfile -t lumidoc-server .

test-client: ## Run client tests
	cd apps/client && npm run test

test-server: ## Run server tests
	cd apps/server && pytest -v

lint-client: ## Lint client code
	cd apps/client && npm run lint

lint-server: ## Lint server code
	cd apps/server && ruff check . && ruff format --check .

docker-up: ## Start all services with Docker Compose
	docker compose -f infrastructure/docker/compose/docker-compose.yml -f infrastructure/docker/compose/docker-compose.dev.yml up -d

docker-down: ## Stop all Docker services
	docker compose -f infrastructure/docker/compose/docker-compose.yml down

docker-build: ## Build all Docker images
	docker compose -f infrastructure/docker/compose/docker-compose.yml build

clean: ## Clean build artifacts
	rm -rf apps/client/dist
	rm -rf apps/server/__pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

seed: ## Seed the database
	bash scripts/seed_db.sh

backup: ## Backup the database
	bash scripts/backup_db.sh

healthcheck: ## Check health of all services
	bash scripts/healthcheck.sh

generate-keys: ## Generate RSA keys for JWT
	bash scripts/generate_keys.sh
