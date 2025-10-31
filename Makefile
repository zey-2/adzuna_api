.PHONY: test test-cov test-unit test-integration test-mcp install install-dev setup-env dev docker-build docker-run docker-test gcp-deploy clean help

help:
	@echo "Available commands:"
	@echo "  make setup-env        - Create conda environment from environment.yml"
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install development and test dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make test-cov         - Run tests with coverage report (95%% threshold)"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-mcp         - Run MCP protocol tests only"
	@echo "  make dev              - Start development server with auto-reload"
	@echo "  make docker-build     - Build Docker image"
	@echo "  make docker-run       - Run Docker container locally"
	@echo "  make docker-test      - Run Docker container with test credentials"
	@echo "  make gcp-deploy       - Deploy to Google Cloud Run"
	@echo "  make clean            - Remove test artifacts and cache files"

setup-env:
	conda env create -f environment.yml
	@echo "Environment created. Activate with: conda activate adzuna-mcp"

install:
	pip install fastapi>=0.115.0 fastapi-mcp>=0.4.0 uvicorn>=0.32.0 requests>=2.32.0 pydantic>=2.0.0

install-dev:
	pip install fastapi>=0.115.0 fastapi-mcp>=0.4.0 uvicorn>=0.32.0 requests>=2.32.0 pydantic>=2.0.0
	pip install pytest>=8.0.0 pytest-cov>=4.1.0 pytest-asyncio>=0.23.0 requests-mock>=1.11.0 httpx>=0.25.0 pytest-mock>=3.12.0

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=server --cov-report=html --cov-report=term-missing --cov-branch --cov-fail-under=95

test-unit:
	pytest tests/ -v -m "unit"

test-integration:
	pytest tests/ -v -m "integration"

test-mcp:
	pytest tests/ -v -m "mcp"

dev:
	uvicorn server:app --reload --host 0.0.0.0 --port 7000

docker-build:
	docker build -t adzuna-mcp-server .

docker-run:
	docker run -p 7000:7000 -e ADZUNA_APP_ID=$(ADZUNA_APP_ID) -e ADZUNA_APP_KEY=$(ADZUNA_APP_KEY) -e PORT=7000 adzuna-mcp-server

docker-test:
	docker run -p 7000:7000 -e ADZUNA_APP_ID=test_id -e ADZUNA_APP_KEY=test_key -e PORT=7000 adzuna-mcp-server

gcp-deploy:
	@echo "Deploying to Google Cloud Run..."
	@if not defined PROJECT_ID (echo ERROR: PROJECT_ID environment variable not set && exit /b 1)
	gcloud builds submit --tag gcr.io/$(PROJECT_ID)/adzuna-mcp-server
	gcloud run deploy adzuna-mcp-server --image gcr.io/$(PROJECT_ID)/adzuna-mcp-server --region us-central1 --platform managed --allow-unauthenticated --min-instances 0

clean:
	@if exist __pycache__ rmdir /s /q __pycache__
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist .coverage del .coverage
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist tests\__pycache__ rmdir /s /q tests\__pycache__
	@echo Cleaned test artifacts and cache files
