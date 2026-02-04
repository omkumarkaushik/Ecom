.PHONY: help install lint test build run clean deploy rollback

# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
DOCKER := docker
DOCKER_COMPOSE := docker-compose
IMAGE_NAME := ecom-app
VERSION := $(shell git describe --tags --always --dirty)

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

lint: ## Run all linting checks
	@echo "Running Black..."
	black --check .
	@echo "Running isort..."
	isort --check-only .
	@echo "Running flake8..."
	flake8 .
	@echo "Running pylint..."
	pylint **/*.py || true

format: ## Format code with black and isort
	black .
	isort .

security: ## Run security checks
	@echo "Running Bandit..."
	bandit -r . -f json -o bandit-report.json || true
	bandit -r . -ll
	@echo "Running Safety..."
	safety check

test: ## Run unit tests with coverage
	pytest tests/ --cov=. --cov-report=html --cov-report=term

test-verbose: ## Run tests with verbose output
	pytest tests/ -v --cov=. --cov-report=html --cov-report=term

build: ## Build Docker image
	$(DOCKER) build \
		--build-arg BUILD_DATE=$(shell date -u +'%Y-%m-%dT%H:%M:%SZ') \
		--build-arg VCS_REF=$(shell git rev-parse --short HEAD) \
		--build-arg VERSION=$(VERSION) \
		-t $(IMAGE_NAME):$(VERSION) \
		-t $(IMAGE_NAME):latest \
		.

build-no-cache: ## Build Docker image without cache
	$(DOCKER) build --no-cache \
		--build-arg BUILD_DATE=$(shell date -u +'%Y-%m-%dT%H:%M:%SZ') \
		--build-arg VCS_REF=$(shell git rev-parse --short HEAD) \
		--build-arg VERSION=$(VERSION) \
		-t $(IMAGE_NAME):$(VERSION) \
		-t $(IMAGE_NAME):latest \
		.

run: ## Run the application with Docker Compose
	$(DOCKER_COMPOSE) up -d

stop: ## Stop the application
	$(DOCKER_COMPOSE) down

logs: ## View application logs
	$(DOCKER_COMPOSE) logs -f

status: ## Check application status
	$(DOCKER_COMPOSE) ps

clean: ## Clean up build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -f bandit-report.json safety-report.json trivy-report.json

clean-docker: ## Clean Docker images and containers
	$(DOCKER_COMPOSE) down -v
	$(DOCKER) system prune -f

deploy-staging: ## Deploy to staging environment
	./deploy.sh staging deploy

deploy-production: ## Deploy to production environment
	./deploy.sh production deploy

rollback-staging: ## Rollback staging deployment
	./deploy.sh staging rollback

rollback-production: ## Rollback production deployment
	./deploy.sh production rollback

scan: ## Run container security scan
	$(DOCKER) run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		aquasec/trivy image $(IMAGE_NAME):latest

ci: lint security test build ## Run full CI pipeline locally

all: install lint test build ## Install, lint, test, and build

.DEFAULT_GOAL := help
