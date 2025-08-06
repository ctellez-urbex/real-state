# Real State Search API - Makefile for Serverless Deployment

.PHONY: help install test deploy dev prod setup-ssm clean logs

# Default target
help:
	@echo "Real State Search API - Serverless Deployment"
	@echo ""
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  test         - Run tests"
	@echo "  setup-ssm    - Setup SSM parameters"
	@echo "  db-url       - Generate DATABASE_URL"
	@echo "  deploy-local - Deploy locally with temporary values"
	@echo "  deploy-dev   - Deploy to development stage"
	@echo "  deploy-prod  - Deploy to production stage"
	@echo "  logs         - View CloudWatch logs"
	@echo "  clean        - Remove serverless artifacts"
	@echo "  help         - Show this help"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Installing serverless framework..."
	npm install -g serverless
	@echo "✅ Dependencies installed successfully!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Configure AWS credentials: aws configure"
	@echo "2. Generate DATABASE_URL: make db-url"
	@echo "3. Deploy locally: make deploy-local"
	@echo "4. Configure GitHub secrets and push to developer branch"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ --cov=app --cov-report=term-missing

# Setup SSM parameters
setup-ssm:
	@echo "Setting up SSM parameters..."
	@echo "Enter stage (dev/prod):"
	@read stage; \
	./scripts/setup-ssm-params.sh $$stage

# Generate DATABASE_URL
db-url:
	@echo "Generating DATABASE_URL..."
	./scripts/generate-database-url.sh

# Deploy locally with temporary values
deploy-local:
	@echo "Deploying locally with temporary configuration..."
	./scripts/deploy-local.sh

# Deploy to development
deploy-dev:
	@echo "Deploying to development stage..."
	serverless deploy --stage dev --verbose

# Deploy to production
deploy-prod:
	@echo "Deploying to production stage..."
	serverless deploy --stage prod --verbose

# View logs
logs:
	@echo "Viewing CloudWatch logs..."
	@echo "Enter stage (dev/prod):"
	@read stage; \
	serverless logs --stage $$stage --tail

# Clean serverless artifacts
clean:
	@echo "Cleaning serverless artifacts..."
	rm -rf .serverless
	rm -rf node_modules
	rm -rf .requirements
	rm -rf .python_packages

# Get deployment info
info:
	@echo "Getting deployment information..."
	@echo "Enter stage (dev/prod):"
	@read stage; \
	serverless info --stage $$stage

# Remove deployment
remove:
	@echo "Removing deployment..."
	@echo "Enter stage (dev/prod):"
	@read stage; \
	serverless remove --stage $$stage

# Test API locally
local:
	@echo "Starting local development server..."
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Package for deployment
package:
	@echo "Packaging for deployment..."
	@echo "Enter stage (dev/prod):"
	@read stage; \
	serverless package --stage $$stage

# Invoke function locally
invoke:
	@echo "Invoking function locally..."
	@echo "Enter stage (dev/prod):"
	@read stage; \
	serverless invoke local --stage $$stage --function api --path events/test-event.json 