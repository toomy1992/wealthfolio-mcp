.PHONY: help install dev test lint run docker-build docker-run clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	pip install -r requirements.txt

dev: ## Run development server
	uvicorn src.mcp_server:app --reload

test: ## Run tests
	pytest tests/ -v

lint: ## Run linting
	flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

run: ## Run production server
	uvicorn src.mcp_server:app --host 0.0.0.0 --port 8000

docker-build: ## Build Docker image
	docker build -t wealthfolio-mcp .

docker-run: ## Run Docker container
	docker run -p 8000:8000 --env-file .env wealthfolio-mcp

docker-compose-up: ## Run with docker-compose
	docker-compose up -d

docker-compose-down: ## Stop docker-compose
	docker-compose down

clean: ## Clean up cache files
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

format: ## Format code with black
	black src/ tests/

check-format: ## Check code formatting
	black --check src/ tests/