.PHONY: help install install-dev test test-cov format lint pre-commit clean run run-docker deploy deploy-prod remove logs setup-env

# Default target
help:
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Install dependencies
install:
	pip install -r requirements.txt

# Install development dependencies
install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

# Run tests
test:
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=app --cov-report=html --cov-report=term-missing

format: ## Format code with black and isort
	black .
	isort .

lint: ## Run linting checks
	flake8 .
	mypy .

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf .mypy_cache

run: ## Run the application locally
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-docker: ## Run the application with Docker
	docker-compose up --build

deploy: ## Deploy to AWS Lambda (dev)
	serverless deploy

deploy-prod: ## Deploy to AWS Lambda (production)
	./scripts/deploy-with-env.sh

remove: ## Remove AWS Lambda deployment
	serverless remove

logs: ## View AWS Lambda logs
	serverless logs -f api

setup: install-dev ## Setup development environment
	@echo "Development environment setup complete!"

setup-env: ## Setup environment variables with API keys
	@./scripts/setup-env.sh

check-env: ## Check environment variables configuration
	@./scripts/check-env.sh

setup-aws: ## Setup AWS credentials
	@./scripts/setup-aws.sh

cleanup-vpc: ## Clean up VPC resources (no longer needed for external DB)
	@./scripts/cleanup-vpc.sh

deploy-check: check-env ## Check environment before deployment
	@echo "Environment check completed. Run 'make deploy-prod' to deploy."

ci: format lint test ## Run CI checks
	@echo "CI checks completed successfully!"
