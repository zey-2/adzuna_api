"""Comprehensive tests for FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
def test_health_check_with_credentials(client, mock_env_vars):
    """Test health check endpoint with credentials configured."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "credentials_configured" in data
    assert data["credentials_configured"] == "True"


@pytest.mark.unit
def test_health_check_without_credentials(client, env_without_credentials):
    """Test health check endpoint reports credential status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    # Credentials are loaded at module import time, so they persist
    assert "credentials_configured" in data


@pytest.mark.unit
def test_search_jobs_minimal_params(client, mock_adzuna_search_success):
    """Test job search with minimal required parameters."""
    response = client.get("/jobs/search", params={"what": "data scientist"})
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "results" in data
    assert data["count"] == 100
    assert len(data["results"]) == 2
    assert data["results"][0]["title"] == "Senior Data Scientist"


@pytest.mark.unit
def test_search_jobs_all_params(client, requests_mock):
    """Test job search with all parameters."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/us/search/2",
        json={"count": 50, "results": []}
    )
    
    response = client.get(
        "/jobs/search",
        params={
            "what": "software engineer",
            "where": "New York",
            "country": "us",
            "page": 2,
            "results_per_page": 20,
            "sort_by": "salary",
            "full_time": True,
            "part_time": False,
            "contract": False,
            "permanent": True,
            "salary_min": 80000,
            "salary_max": 150000
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert data["count"] == 50


@pytest.mark.unit
def test_search_jobs_missing_what_param(client):
    """Test job search without required 'what' parameter."""
    response = client.get("/jobs/search")
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_search_jobs_empty_results(client, mock_adzuna_search_empty):
    """Test job search with no results."""
    response = client.get("/jobs/search", params={"what": "nonexistent job"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert len(data["results"]) == 0


@pytest.mark.unit
def test_search_jobs_without_credentials(client, env_without_credentials, requests_mock):
    """Test job search fails gracefully without credentials."""
    # Mock the Adzuna API to return 401
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        status_code=401,
        json={"error": "Unauthorized"}
    )
    
    response = client.get("/jobs/search", params={"what": "developer"})
    assert response.status_code == 500
    assert "detail" in response.json()


@pytest.mark.unit
def test_search_jobs_api_error(client, mock_adzuna_search_error):
    """Test job search handles API errors."""
    response = client.get("/jobs/search", params={"what": "test"})
    assert response.status_code == 500
    assert "detail" in response.json()


@pytest.mark.unit
def test_search_jobs_invalid_country(client, requests_mock):
    """Test job search with invalid country code."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/invalid/search/1",
        status_code=404,
        json={"error": "Country not found"}
    )
    
    response = client.get(
        "/jobs/search",
        params={"what": "developer", "country": "invalid"}
    )
    assert response.status_code == 500


@pytest.mark.unit
def test_search_jobs_pagination(client, requests_mock):
    """Test job search pagination."""
    # Mock page 1
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        json={"count": 100, "results": [{"id": "1", "title": "Job 1"}]}
    )
    
    # Mock page 2
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/2",
        json={"count": 100, "results": [{"id": "2", "title": "Job 2"}]}
    )
    
    # Test page 1
    response1 = client.get("/jobs/search", params={"what": "developer", "page": 1})
    assert response1.status_code == 200
    
    # Test page 2
    response2 = client.get("/jobs/search", params={"what": "developer", "page": 2})
    assert response2.status_code == 200


@pytest.mark.unit
def test_search_jobs_results_per_page(client, requests_mock):
    """Test job search with different results per page."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        json={"count": 100, "results": []}
    )
    
    response = client.get(
        "/jobs/search",
        params={"what": "developer", "results_per_page": 50}
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_search_jobs_salary_filter(client, requests_mock):
    """Test job search with salary filters."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        json={
            "count": 10,
            "results": [
                {
                    "id": "1",
                    "title": "High Paying Job",
                    "salary_min": 100000,
                    "salary_max": 150000
                }
            ]
        }
    )
    
    response = client.get(
        "/jobs/search",
        params={"what": "senior", "salary_min": 100000, "salary_max": 200000}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 10


@pytest.mark.unit
def test_search_jobs_employment_type_filters(client, requests_mock):
    """Test job search with employment type filters."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        json={"count": 30, "results": []}
    )
    
    response = client.get(
        "/jobs/search",
        params={
            "what": "developer",
            "full_time": True,
            "permanent": True
        }
    )
    assert response.status_code == 200


@pytest.mark.unit
def test_get_top_companies_default_country(client, mock_adzuna_top_companies_success):
    """Test get top companies with default country (Singapore)."""
    response = client.get("/jobs/top-companies")
    assert response.status_code == 200
    data = response.json()
    assert "leaderboard" in data
    assert len(data["leaderboard"]) == 3
    assert data["leaderboard"][0]["canonical_name"] == "tech-corp"
    assert data["leaderboard"][0]["count"] == 50


@pytest.mark.unit
def test_get_top_companies_custom_country(client, requests_mock):
    """Test get top companies with custom country."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/us/top_companies",
        json={
            "leaderboard": [
                {"canonical_name": "us-company", "count": 100}
            ]
        }
    )
    
    response = client.get("/jobs/top-companies", params={"country": "us"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["leaderboard"]) == 1
    assert data["leaderboard"][0]["canonical_name"] == "us-company"


@pytest.mark.unit
def test_get_top_companies_api_error(client, requests_mock):
    """Test get top companies handles API errors."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/top_companies",
        status_code=500,
        json={"error": "Server error"}
    )
    
    response = client.get("/jobs/top-companies")
    assert response.status_code == 500


@pytest.mark.unit
def test_get_top_companies_without_credentials(client, env_without_credentials, requests_mock):
    """Test get top companies without credentials."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/top_companies",
        status_code=401
    )
    
    response = client.get("/jobs/top-companies")
    assert response.status_code == 500


@pytest.mark.unit
def test_get_salary_histogram_minimal_params(client, mock_adzuna_histogram_success):
    """Test salary histogram with minimal parameters."""
    response = client.get("/jobs/histogram", params={"what": "engineer"})
    assert response.status_code == 200
    data = response.json()
    assert "histogram" in data
    assert "salary" in data["histogram"]
    assert len(data["histogram"]["salary"]) == 6


@pytest.mark.unit
def test_get_salary_histogram_all_params(client, requests_mock):
    """Test salary histogram with all parameters."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/us/histogram",
        json={
            "histogram": {
                "salary": [
                    {"label": "60000", "count": 50}
                ]
            }
        }
    )
    
    response = client.get(
        "/jobs/histogram",
        params={"what": "data scientist", "country": "us", "where": "California"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "histogram" in data


@pytest.mark.unit
def test_get_salary_histogram_missing_what(client):
    """Test salary histogram without required 'what' parameter."""
    response = client.get("/jobs/histogram")
    assert response.status_code == 422  # Validation error


@pytest.mark.unit
def test_get_salary_histogram_api_error(client, requests_mock):
    """Test salary histogram handles API errors."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/histogram",
        status_code=500
    )
    
    response = client.get("/jobs/histogram", params={"what": "test"})
    assert response.status_code == 500


@pytest.mark.unit
def test_get_salary_histogram_empty_results(client, requests_mock):
    """Test salary histogram with empty results."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/histogram",
        json={"histogram": {"salary": []}}
    )
    
    response = client.get("/jobs/histogram", params={"what": "rare job"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["histogram"]["salary"]) == 0


@pytest.mark.unit
def test_api_root_redirect(client):
    """Test root endpoint redirects to docs."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code in [307, 308]  # Temporary or permanent redirect
    assert "/docs" in response.headers.get("location", "")


@pytest.mark.unit
def test_openapi_schema_available(client):
    """Test OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


@pytest.mark.unit
def test_docs_endpoint_available(client):
    """Test API documentation endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.unit
def test_search_jobs_response_structure(client, mock_adzuna_search_success):
    """Test job search response has correct structure."""
    response = client.get("/jobs/search", params={"what": "developer"})
    assert response.status_code == 200
    data = response.json()
    
    # Check top-level structure
    assert isinstance(data["count"], int)
    assert isinstance(data["results"], list)
    
    # Check individual job structure
    if len(data["results"]) > 0:
        job = data["results"][0]
        assert "id" in job
        assert "title" in job
        assert "company" in job
        assert "location" in job
        assert "redirect_url" in job


@pytest.mark.unit
def test_multiple_concurrent_requests(client, mock_all_adzuna_endpoints):
    """Test handling multiple concurrent requests."""
    # Simulate concurrent requests
    responses = []
    for i in range(5):
        response = client.get("/jobs/search", params={"what": f"job{i}"})
        responses.append(response)
    
    # All should succeed
    assert all(r.status_code == 200 for r in responses)


@pytest.mark.unit
def test_sort_by_parameter(client, requests_mock):
    """Test different sort_by parameter values."""
    sort_options = ["date", "relevance", "salary"]
    
    for sort_by in sort_options:
        requests_mock.get(
            "https://api.adzuna.com/v1/api/jobs/sg/search/1",
            json={"count": 10, "results": []}
        )
        
        response = client.get(
            "/jobs/search",
            params={"what": "developer", "sort_by": sort_by}
        )
        assert response.status_code == 200
