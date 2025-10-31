---
name: Adzuna MCP Server Enhancement Plan
description: Comprehensive plan to add exhaustive testing (95%+ coverage) and Google Cloud Run deployment with manual workflow, optimized for GCP free tier with public access
---

# Adzuna MCP Server Enhancement Plan

## Overview

Add exhaustive testing strategy (95%+ coverage) and Google Cloud Run deployment with manual workflow, optimized for GCP free tier with public access.

## Implementation Steps

### 1. Create Comprehensive Test Suite

**Directory:** `tests/`

#### 1.1 `conftest.py` - Test Fixtures
- Fixtures for mocking all Adzuna API endpoints
- Environment variable fixtures (with/without credentials)
- Error scenario fixtures (API failures, timeouts, invalid responses)
- Test client fixture for FastAPI
- MCP client fixture for protocol testing

#### 1.2 `test_endpoints.py` - FastAPI Endpoint Tests
- **Health Check Tests:**
  - Test with credentials configured
  - Test without credentials configured
  - Test response format
- **Job Search Tests:**
  - Test successful search with minimal parameters
  - Test with all parameters (pagination, filters, sorting)
  - Test missing credentials error
  - Test invalid country code
  - Test API timeout handling
  - Test malformed API response
  - Test parameter validation (422 errors)
- **Top Companies Tests:**
  - Test successful retrieval
  - Test with different countries
  - Test API error handling
- **Salary Histogram Tests:**
  - Test successful retrieval
  - Test with different parameters
  - Test API error handling

#### 1.3 `test_mcp_tools.py` - MCP Protocol Tests
- **Tool Discovery Tests:**
  - Test `tools/list` endpoint
  - Verify all expected tools present (search_jobs, get_top_companies, get_salary_histogram, health_check)
  - Verify tool schemas match FastAPI OpenAPI
  - Verify operation IDs are correct
  - Verify input schema properties and required fields
- **Tool Invocation Tests:**
  - Test `tools/call` with valid parameters
  - Test `tools/call` with invalid tool name
  - Test `tools/call` with missing required parameters
  - Test `tools/call` with invalid parameter types
  - Test JSON-RPC protocol compliance
  - Test error response format
- **MCP Protocol Tests:**
  - Test JSON-RPC 2.0 format
  - Test id field handling
  - Test error codes and messages

#### 1.4 `test_integration.py` - End-to-End Tests
- Start live server in subprocess
- Test complete MCP workflow (list → call → verify)
- Test multiple concurrent requests
- Test server startup with/without credentials
- Test graceful error handling in live environment

#### 1.5 `pytest.ini` - Test Configuration
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
    --cov=server
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    --cov-branch
    --cov-fail-under=95
markers =
    unit: Unit tests for individual functions
    integration: Integration tests with live server
    mcp: MCP protocol-specific tests
    slow: Slow running tests
```

### 2. Update Dependencies

**File:** `requirements.txt`

Add test dependencies section:
```txt
# Existing production dependencies
fastapi>=0.115.0
fastapi-mcp>=0.4.0
uvicorn>=0.32.0
requests>=2.32.0
pydantic>=2.0.0

# Development and Testing Dependencies
pytest>=8.0.0
pytest-cov>=4.1.0
pytest-asyncio>=0.23.0
requests-mock>=1.11.0
httpx>=0.25.0
pytest-mock>=3.12.0
```

### 3. Create Docker Deployment Files

#### 3.1 `Dockerfile`
```dockerfile
# Use official Python runtime as base image
FROM python:3.13-slim

# Set working directory
WORKDIR /code

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for Docker layer caching
COPY requirements.txt /code/requirements.txt

# Install Python dependencies (production only)
RUN pip install --no-cache-dir --upgrade \
    fastapi>=0.115.0 \
    fastapi-mcp>=0.4.0 \
    uvicorn>=0.32.0 \
    requests>=2.32.0 \
    pydantic>=2.0.0

# Copy application code
COPY server.py /code/server.py
COPY adzuna_example.py /code/adzuna_example.py
COPY README.md /code/README.md

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /code
USER appuser

# Cloud Run sets PORT environment variable
# Use exec form for proper signal handling
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

#### 3.2 `.dockerignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
*.cover
tests/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Git
.git/
.gitignore

# Environment
.env
.env.local

# Documentation
docs/

# Test files
test*.py

# CI/CD
.github/
.gitlab-ci.yml

# Misc
*.log
.DS_Store
Makefile
DEPLOYMENT.md
```

#### 3.3 Update `server.py` - PORT Environment Variable

Update the main block to use Cloud Run's PORT environment variable:
```python
if __name__ == "__main__":
    import uvicorn
    
    # Cloud Run provides PORT environment variable
    port = int(os.getenv("PORT", 8000))
    
    print("🚀 Starting Adzuna Job Search MCP Server...")
    print(f"   API docs: http://localhost:{port}/docs")
    print(f"   MCP endpoint: http://localhost:{port}/mcp")
    print()
    
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("⚠️  Warning: Adzuna credentials not configured!")
        print("   Please set ADZUNA_APP_ID and ADZUNA_APP_KEY in your environment")
        print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 4. Create Deployment Documentation

**File:** `DEPLOYMENT.md`

#### Contents:
- **Prerequisites:**
  - Google Cloud account with billing enabled
  - gcloud CLI installed and authenticated
  - Docker installed (for local testing)
  - Adzuna API credentials

- **GCP Setup:**
  - Enable required APIs (Cloud Run, Cloud Build, Secret Manager)
  - Create GCP project or select existing
  - Set default region to `us-central1` (free tier optimized)

- **Secret Manager Setup:**
  ```bash
  # Create secrets
  echo -n "your_app_id" | gcloud secrets create adzuna-app-id --data-file=-
  echo -n "your_app_key" | gcloud secrets create adzuna-app-key --data-file=-
  
  # Grant Cloud Run service account access
  gcloud secrets add-iam-policy-binding adzuna-app-id \
      --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
      --role="roles/secretmanager.secretAccessor"
  
  gcloud secrets add-iam-policy-binding adzuna-app-key \
      --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
      --role="roles/secretmanager.secretAccessor"
  ```

- **Local Docker Testing:**
  ```bash
  # Build image
  docker build -t adzuna-mcp-server .
  
  # Run locally
  docker run -p 8000:8000 \
      -e ADZUNA_APP_ID=your_id \
      -e ADZUNA_APP_KEY=your_key \
      -e PORT=8000 \
      adzuna-mcp-server
  
  # Test endpoints
  curl http://localhost:8000/health
  ```

- **Manual Cloud Run Deployment:**
  ```bash
  # Set variables
  export PROJECT_ID=your-gcp-project-id
  export REGION=us-central1
  
  # Build container image with Cloud Build
  gcloud builds submit --tag gcr.io/$PROJECT_ID/adzuna-mcp-server
  
  # Deploy to Cloud Run
  gcloud run deploy adzuna-mcp-server \
      --image gcr.io/$PROJECT_ID/adzuna-mcp-server \
      --region $REGION \
      --platform managed \
      --allow-unauthenticated \
      --min-instances 0 \
      --max-instances 10 \
      --memory 512Mi \
      --cpu 1 \
      --timeout 300s \
      --concurrency 80 \
      --update-secrets ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest
  
  # Get service URL
  gcloud run services describe adzuna-mcp-server \
      --region $REGION \
      --format 'value(status.url)'
  ```

- **Free Tier Optimization:**
  - Monthly limits: 2M requests, 180K vCPU-seconds, 360K GiB-seconds
  - Min instances set to 0 (cold starts ~1-3s, no idle cost)
  - Region `us-central1` uses Tier 1 pricing
  - Monitor usage in GCP Console → Billing

- **Testing Deployed Service:**
  ```bash
  # Test health endpoint
  curl https://YOUR_SERVICE_URL/health
  
  # Test MCP tools list
  curl -X POST https://YOUR_SERVICE_URL/mcp \
      -H "Content-Type: application/json" \
      -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
  ```

- **Connecting from Claude Desktop:**
  Add to Claude config:
  ```json
  {
    "mcpServers": {
      "adzuna-jobs": {
        "url": "https://YOUR_SERVICE_URL/mcp"
      }
    }
  }
  ```

- **Updating Deployment:**
  ```bash
  # Rebuild and redeploy
  gcloud builds submit --tag gcr.io/$PROJECT_ID/adzuna-mcp-server
  gcloud run deploy adzuna-mcp-server \
      --image gcr.io/$PROJECT_ID/adzuna-mcp-server \
      --region $REGION
  ```

- **Monitoring & Troubleshooting:**
  - View logs: `gcloud run services logs read adzuna-mcp-server --region $REGION`
  - Monitor metrics: GCP Console → Cloud Run → adzuna-mcp-server
  - Check cold start times, error rates, request counts

### 5. Add Development Tools

#### 5.1 `Makefile` (PowerShell-compatible)
```makefile
.PHONY: test test-cov test-unit test-integration install install-dev dev docker-build docker-run docker-test gcp-deploy clean

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

dev:
	uvicorn server:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t adzuna-mcp-server .

docker-run:
	docker run -p 8000:8000 -e ADZUNA_APP_ID=${ADZUNA_APP_ID} -e ADZUNA_APP_KEY=${ADZUNA_APP_KEY} -e PORT=8000 adzuna-mcp-server

docker-test:
	docker run -p 8000:8000 -e ADZUNA_APP_ID=test_id -e ADZUNA_APP_KEY=test_key -e PORT=8000 adzuna-mcp-server

gcp-deploy:
	gcloud builds submit --tag gcr.io/${PROJECT_ID}/adzuna-mcp-server
	gcloud run deploy adzuna-mcp-server --image gcr.io/${PROJECT_ID}/adzuna-mcp-server --region us-central1 --platform managed --allow-unauthenticated --min-instances 0

clean:
	if exist __pycache__ rmdir /s /q __pycache__
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .coverage del .coverage
	if exist htmlcov rmdir /s /q htmlcov
	if exist tests\__pycache__ rmdir /s /q tests\__pycache__
```

#### 5.2 Update `.env.example`
Add PORT variable for Cloud Run:
```bash
# Adzuna API Credentials
# Get your credentials from https://developer.adzuna.com/
ADZUNA_APP_ID=your_app_id_here
ADZUNA_APP_KEY=your_app_key_here

# Optional: Server Configuration (for Cloud Run compatibility)
PORT=8000
```

#### 5.3 Update `README.md`

Add new sections:

**Testing Section:**
```markdown
## Testing

### Running Tests

Install development dependencies:
```bash
pip install pytest pytest-cov pytest-asyncio requests-mock httpx pytest-mock
```

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage (target: 95%+):
```bash
pytest tests/ -v --cov=server --cov-report=html --cov-report=term-missing --cov-branch --cov-fail-under=95
```

Run specific test categories:
```bash
# Unit tests only
pytest tests/ -v -m "unit"

# Integration tests only
pytest tests/ -v -m "integration"

# MCP protocol tests only
pytest tests/ -v -m "mcp"
```

View coverage report:
```bash
# Open htmlcov/index.html in your browser
```

### Test Structure

- `tests/conftest.py` - Shared fixtures and test configuration
- `tests/test_endpoints.py` - FastAPI endpoint tests
- `tests/test_mcp_tools.py` - MCP protocol compliance tests
- `tests/test_integration.py` - End-to-end integration tests
```

**Deployment Section:**
```markdown
## Deployment

### Google Cloud Run Deployment

This MCP server can be deployed to Google Cloud Run with free tier support.

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step deployment instructions.

**Quick Deploy:**
```bash
# Set your GCP project ID
export PROJECT_ID=your-gcp-project-id

# Build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/adzuna-mcp-server
gcloud run deploy adzuna-mcp-server \
    --image gcr.io/$PROJECT_ID/adzuna-mcp-server \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --min-instances 0 \
    --update-secrets ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest
```

**Features:**
- ✅ Free tier optimized (us-central1 region)
- ✅ Min instances: 0 (no idle cost)
- ✅ Public access (no authentication required)
- ✅ Secret Manager integration for credentials
- ✅ Auto-scaling (0-10 instances)

### Local Docker Testing

Build and test locally before deploying:
```bash
# Build image
docker build -t adzuna-mcp-server .

# Run locally
docker run -p 8000:8000 \
    -e ADZUNA_APP_ID=your_id \
    -e ADZUNA_APP_KEY=your_key \
    -e PORT=8000 \
    adzuna-mcp-server

# Test
curl http://localhost:8000/health
```
```

## Expected Outcomes

### Test Coverage
- 95%+ code coverage achieved
- All endpoints tested with success/error cases
- MCP protocol compliance verified
- Integration tests validate end-to-end workflows

### Deployment
- Service deployed to Cloud Run in `us-central1`
- Min instances: 0 (cold starts ~1-3s)
- Public access enabled (no authentication)
- Secrets managed via Secret Manager
- Free tier optimized (2M req/month, 180K vCPU-sec, 360K GiB-sec)

### Documentation
- Complete deployment guide in DEPLOYMENT.md
- Testing instructions in README.md
- Makefile for common development tasks
- Docker configuration for containerization

## Files to Create/Modify

### New Files
- `tests/__init__.py`
- `tests/conftest.py`
- `tests/test_endpoints.py`
- `tests/test_mcp_tools.py`
- `tests/test_integration.py`
- `pytest.ini`
- `Dockerfile`
- `.dockerignore`
- `DEPLOYMENT.md`
- `Makefile`

### Modified Files
- `requirements.txt` (add test dependencies)
- `server.py` (add PORT environment variable support)
- `.env.example` (add PORT variable)
- `README.md` (add testing and deployment sections)

## Success Criteria

1. ✅ All tests pass with 95%+ coverage
2. ✅ Docker image builds successfully
3. ✅ Local Docker container runs without errors
4. ✅ Deployment to Cloud Run succeeds
5. ✅ Health check endpoint responds correctly
6. ✅ MCP endpoints accessible from Claude Desktop
7. ✅ Complete documentation for testing and deployment
8. ✅ Free tier optimized configuration
