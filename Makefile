# ============================================
# CV Algorithm Hub - Management Scripts
# ============================================
# Usage:
#   Development: make dev-up
#   Production:  make prod-up
#   Blue-Green:  make bg-deploy
# ============================================

.PHONY: help dev-up dev-down dev-logs prod-up prod-down prod-logs bg-deploy bg-rollback

# Help
help:
	@echo ""
	@echo "CV Algorithm Hub - Management Commands"
	@echo ""
	@echo "Development:"
	@echo "  dev-up        - Start development environment"
	@echo "  dev-down      - Stop development environment"
	@echo "  dev-logs      - View development logs"
	@echo ""
	@echo "Production:"
	@echo "  prod-up       - Start production environment"
	@echo "  prod-down     - Stop production environment"
	@echo "  prod-logs     - View production logs"
	@echo ""
	@echo "Blue-Green Deployment:"
	@echo "  bg-deploy     - Deploy to inactive color"
	@echo "  bg-switch     - Switch traffic to new version"
	@echo "  bg-rollback   - Rollback to previous version"
	@echo ""
	@echo "Other:"
	@echo "  install       - Install Python dependencies"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linters"
	@echo "  clean         - Clean build artifacts"
	@echo ""

# ============================================
# Development Commands
# ============================================

dev-up:  ## Start development environment
	@echo "Starting development environment..."
	CVHUB_ENVIRONMENT=development docker-compose --profile dev up -d

dev-down:  ## Stop development environment
	@echo "Stopping development environment..."
	CVHUB_ENVIRONMENT=development docker-compose --profile dev down

dev-logs:  ## View development logs
	CVHUB_ENVIRONMENT=development docker-compose --profile dev logs -f

dev-build:  ## Rebuild development images
	CVHUB_ENVIRONMENT=development docker-compose --profile dev build --no-cache

dev-restart:  ## Restart development services
	@if [ -z "$(SERVICE)" ]; then \
		echo "Usage: make dev-restart SERVICE=api-gateway"; \
	else \
		CVHUB_ENVIRONMENT=development docker-compose --profile dev restart $(SERVICE); \
	fi

# ============================================
# Production Commands
# ============================================

prod-up:  ## Start production environment
	@echo "Starting production environment..."
	CVHUB_ENVIRONMENT=production docker-compose --profile prod up -d

prod-down:  ## Stop production environment
	@echo "Stopping production environment..."
	CVHUB_ENVIRONMENT=production docker-compose --profile prod down

prod-logs:  ## View production logs
	CVHUB_ENVIRONMENT=production docker-compose --profile prod logs -f

prod-build:  ## Rebuild production images
	CVHUB_ENVIRONMENT=production docker-compose --profile prod build --no-cache

prod-pull:  ## Pull latest production images
	CVHUB_ENVIRONMENT=production docker-compose --profile prod pull

# ============================================
# Blue-Green Deployment
# ============================================

bg-deploy:  ## Deploy to inactive color (blue or green)
	@echo "Deploying to inactive color..."
	@./scripts/blue-green-deploy.sh

bg-switch:  ## Switch traffic to newly deployed version
	@echo "Switching traffic..."
	@./scripts/blue-green-switch.sh

bg-rollback:  ## Rollback to previous version
	@echo "Rolling back..."
	@./scripts/blue-green-rollback.sh

bg-status:  ## Check blue-green deployment status
	@./scripts/blue-green-status.sh

# ============================================
# GPU Commands
# ============================================

gpu-status:  ## Check GPU availability
	@nvidia-smi || echo "NVIDIA driver not found"

gpu-dev-up:  ## Start development with GPU support
	@echo "Starting development with GPU support..."
	CVHUB_ENVIRONMENT=development CVHUB_GPU_ENABLED=true GPU_COUNT=1 docker-compose --profile dev up -d algorithm-engine

# ============================================
# Monitoring Commands
# ============================================

monitor-dev:  ## Start monitoring dashboard for development
	@echo "Starting Grafana at http://localhost:3001"
	CVHUB_ENVIRONMENT=development docker-compose --profile dev up -d prometheus grafana

monitor-stop:  ## Stop monitoring services
	CVHUB_ENVIRONMENT=development docker-compose stop prometheus grafana

# ============================================
# Local Development
# ============================================

install:  ## Install Python dependencies
	pip install -r requirements.txt

dev-local:  ## Run API Gateway locally (not in Docker)
	uvicorn src.api_gateway.app.main:app --reload --port 8080

web-install:  ## Install frontend dependencies
	cd src/web-ui && npm ci

web-dev:  ## Run frontend dev server
	cd src/web-ui && npm run dev

web-build:  ## Build frontend
	cd src/web-ui && npm run build

# ============================================
# Testing & Linting
# ============================================

test:  ## Run tests
	pytest tests/ -v --cov=src --cov-report=term

test-coverage:  ## Run tests with coverage report
	pytest tests/ -v --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:  ## Run linters
	black --check .
	isort --check-only .
	ruff check .
	mypy src/ --ignore-missing-imports

lint-fix:  ## Fix linting issues
	black .
	isort .
	ruff check --fix .

format:  ## Format code
	black .
	isort .

# ============================================
# Maintenance
# ============================================

clean:  ## Clean build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".pytest_cache" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ dist/

logs-tail:  ## Tail all logs
	tail -f ./logs/**/*.log 2>/dev/null || echo "No logs found"

db-backup:  ## Backup database
	@docker exec cvhub-postgres pg_dump -U postgres cv_algorithm_hub > backup_$$(date +%Y%m%d_%H%M%S).sql

db-restore:  ## Restore database
	@if [ -z "$(FILE)" ]; then echo "Usage: make db-restore FILE=backup.sql"; exit 1; fi
	cat $(FILE) | docker exec -i cvhub-postgres psql -U postgres -d cv_algorithm_hub
