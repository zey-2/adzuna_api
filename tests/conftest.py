"""Pytest configuration and shared fixtures."""
import os
import pytest
from fastapi.testclient import TestClient
from server import app


@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Automatically mock environment variables for all tests."""
    monkeypatch.setenv("ADZUNA_APP_ID", "test_app_id")
    monkeypatch.setenv("ADZUNA_APP_KEY", "test_app_key")


@pytest.fixture
def env_without_credentials(monkeypatch):
    """Remove credentials from environment."""
    monkeypatch.delenv("ADZUNA_APP_ID", raising=False)
    monkeypatch.delenv("ADZUNA_APP_KEY", raising=False)


@pytest.fixture
def client():
    """Create a test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_adzuna_search_success(requests_mock):
    """Mock successful Adzuna job search response."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        json={
            "count": 100,
            "results": [
                {
                    "id": "123456",
                    "title": "Senior Data Scientist",
                    "company": {"display_name": "Tech Corp"},
                    "location": {"display_name": "Singapore"},
                    "description": "Looking for experienced data scientist",
                    "redirect_url": "https://example.com/job/123456",
                    "salary_min": 80000,
                    "salary_max": 120000,
                    "contract_time": "full_time",
                    "category": {"label": "IT Jobs"}
                },
                {
                    "id": "789012",
                    "title": "Data Analyst",
                    "company": {"display_name": "Finance Co"},
                    "location": {"display_name": "Singapore CBD"},
                    "description": "Data analysis role",
                    "redirect_url": "https://example.com/job/789012",
                    "salary_min": 50000,
                    "salary_max": 70000,
                    "contract_time": "full_time",
                    "category": {"label": "IT Jobs"}
                }
            ]
        }
    )
    return requests_mock


@pytest.fixture
def mock_adzuna_search_empty(requests_mock):
    """Mock Adzuna search with no results."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        json={"count": 0, "results": []}
    )
    return requests_mock


@pytest.fixture
def mock_adzuna_search_error(requests_mock):
    """Mock Adzuna API error response."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        status_code=500,
        json={"error": "Internal server error"}
    )
    return requests_mock


@pytest.fixture
def mock_adzuna_top_companies_success(requests_mock):
    """Mock successful top companies response."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/top_companies",
        json={
            "leaderboard": [
                {"canonical_name": "tech-corp", "count": 50},
                {"canonical_name": "finance-co", "count": 35},
                {"canonical_name": "retail-inc", "count": 28}
            ]
        }
    )
    return requests_mock


@pytest.fixture
def mock_adzuna_histogram_success(requests_mock):
    """Mock successful salary histogram response."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/histogram",
        json={
            "histogram": {
                "salary": [
                    {"label": "30000", "count": 25},
                    {"label": "40000", "count": 45},
                    {"label": "50000", "count": 80},
                    {"label": "60000", "count": 120},
                    {"label": "70000", "count": 95},
                    {"label": "80000", "count": 70}
                ]
            }
        }
    )
    return requests_mock


@pytest.fixture
def mock_all_adzuna_endpoints(requests_mock):
    """Mock all Adzuna API endpoints with success responses."""
    # Search endpoint
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        json={
            "count": 100,
            "results": [
                {
                    "id": "123456",
                    "title": "Test Job",
                    "company": {"display_name": "Test Company"},
                    "location": {"display_name": "Test Location"},
                    "redirect_url": "https://example.com/job/123"
                }
            ]
        }
    )
    
    # Top companies endpoint
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/top_companies",
        json={
            "leaderboard": [
                {"canonical_name": "test-company", "count": 50}
            ]
        }
    )
    
    # Histogram endpoint
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/histogram",
        json={
            "histogram": {
                "salary": [
                    {"label": "50000", "count": 100}
                ]
            }
        }
    )
    
    return requests_mock
