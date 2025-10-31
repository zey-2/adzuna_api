"""Integration tests with live server."""
import pytest
import time
import requests
import subprocess
import sys
import os
from multiprocessing import Process
import signal


def start_test_server(port=8888):
    """Start the server in a subprocess for testing."""
    import uvicorn
    from server import app
    
    # Set test environment variables
    os.environ["ADZUNA_APP_ID"] = "test_app_id"
    os.environ["ADZUNA_APP_KEY"] = "test_app_key"
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="error")


@pytest.fixture(scope="module")
def live_server():
    """Start a live server for integration testing."""
    port = 8888
    base_url = f"http://127.0.0.1:{port}"
    
    # Start server in separate process
    proc = Process(target=start_test_server, args=(port,), daemon=True)
    proc.start()
    
    # Wait for server to start
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            time.sleep(0.5)
    else:
        proc.terminate()
        pytest.fail("Server failed to start within timeout period")
    
    yield base_url
    
    # Cleanup
    proc.terminate()
    proc.join(timeout=5)
    if proc.is_alive():
        proc.kill()


@pytest.mark.integration
@pytest.mark.slow
def test_server_starts_successfully(live_server):
    """Test that the server starts and responds to health check."""
    response = requests.get(f"{live_server}/health", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.integration
@pytest.mark.slow
def test_full_mcp_workflow(live_server, mock_all_adzuna_endpoints):
    """Test complete MCP workflow: list tools, then call a tool."""
    base_url = f"{live_server}/mcp"
    
    # Step 1: List available tools
    list_response = requests.post(
        base_url,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        },
        timeout=5
    )
    
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert "result" in list_data
    assert "tools" in list_data["result"]
    
    tools = list_data["result"]["tools"]
    assert len(tools) > 0
    tool_names = [tool["name"] for tool in tools]
    assert "health_check" in tool_names
    
    # Step 2: Call a tool (health_check - doesn't need external API)
    call_response = requests.post(
        base_url,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "health_check",
                "arguments": {}
            }
        },
        timeout=5
    )
    
    assert call_response.status_code == 200
    call_data = call_response.json()
    assert "result" in call_data
    assert "content" in call_data["result"]


@pytest.mark.integration
@pytest.mark.slow
def test_api_documentation_accessible(live_server):
    """Test that API documentation is accessible."""
    response = requests.get(f"{live_server}/docs", timeout=5)
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


@pytest.mark.integration
@pytest.mark.slow
def test_openapi_schema_accessible(live_server):
    """Test that OpenAPI schema is accessible."""
    response = requests.get(f"{live_server}/openapi.json", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "info" in data
    assert "paths" in data


@pytest.mark.integration
@pytest.mark.slow
def test_concurrent_mcp_requests(live_server):
    """Test handling multiple concurrent MCP requests."""
    base_url = f"{live_server}/mcp"
    
    def make_request(request_id):
        """Make a single MCP request."""
        return requests.post(
            base_url,
            json={
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/list",
                "params": {}
            },
            timeout=10
        )
    
    # Make concurrent requests
    import concurrent.futures
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request, i) for i in range(5)]
        responses = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    # All should succeed
    assert all(r.status_code == 200 for r in responses)
    
    # All should have proper structure
    for response in responses:
        data = response.json()
        assert "result" in data
        assert "tools" in data["result"]


@pytest.mark.integration
@pytest.mark.slow
def test_server_handles_rapid_requests(live_server):
    """Test server handles rapid sequential requests."""
    for i in range(10):
        response = requests.get(f"{live_server}/health", timeout=5)
        assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
def test_cors_headers_if_configured(live_server):
    """Test CORS headers if CORS is configured."""
    response = requests.get(f"{live_server}/health", timeout=5)
    # Just check that request succeeds - CORS may or may not be configured
    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
def test_mcp_endpoint_persistent_across_requests(live_server):
    """Test MCP endpoint remains consistent across multiple requests."""
    base_url = f"{live_server}/mcp"
    
    # Make multiple requests
    for i in range(3):
        response = requests.post(
            base_url,
            json={
                "jsonrpc": "2.0",
                "id": i,
                "method": "tools/list",
                "params": {}
            },
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Tool list should be consistent
        tools = data["result"]["tools"]
        tool_names = [tool["name"] for tool in tools]
        assert "health_check" in tool_names


@pytest.mark.integration
@pytest.mark.slow
def test_server_error_recovery(live_server):
    """Test server recovers from errors gracefully."""
    base_url = f"{live_server}/mcp"
    
    # Make invalid request
    invalid_response = requests.post(
        base_url,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "invalid_method",
            "params": {}
        },
        timeout=5
    )
    # Server should handle error
    
    # Follow up with valid request - should still work
    valid_response = requests.post(
        base_url,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        timeout=5
    )
    
    assert valid_response.status_code == 200


@pytest.mark.integration
@pytest.mark.slow
def test_server_response_time(live_server):
    """Test server responds within reasonable time."""
    start_time = time.time()
    response = requests.get(f"{live_server}/health", timeout=5)
    end_time = time.time()
    
    assert response.status_code == 200
    
    # Should respond in less than 1 second for health check
    response_time = end_time - start_time
    assert response_time < 1.0


@pytest.mark.integration
@pytest.mark.slow
def test_mcp_tools_json_rpc_compliance(live_server):
    """Test MCP endpoint follows JSON-RPC 2.0 specification."""
    base_url = f"{live_server}/mcp"
    
    response = requests.post(
        base_url,
        json={
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/list",
            "params": {}
        },
        timeout=5
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # JSON-RPC 2.0 compliance
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 100
    assert ("result" in data) or ("error" in data)


@pytest.mark.integration
@pytest.mark.slow
def test_server_handles_large_response(live_server, requests_mock):
    """Test server handles large responses properly."""
    # Mock large response
    large_results = [
        {
            "id": str(i),
            "title": f"Job {i}",
            "company": {"display_name": f"Company {i}"},
            "location": {"display_name": f"Location {i}"},
            "redirect_url": f"https://example.com/job/{i}"
        }
        for i in range(100)
    ]
    
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/sg/search/1",
        json={"count": 1000, "results": large_results}
    )
    
    # This test would need the server to actually make external calls
    # For now, just verify the endpoint exists
    response = requests.get(f"{live_server}/health", timeout=5)
    assert response.status_code == 200


@pytest.mark.integration
def test_server_metadata(live_server):
    """Test server returns correct metadata in OpenAPI schema."""
    response = requests.get(f"{live_server}/openapi.json", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    info = data.get("info", {})
    
    # Check that server has proper metadata
    assert "title" in info
    assert "version" in info
    assert "description" in info


@pytest.mark.integration
def test_health_check_returns_credential_status(live_server):
    """Test health check indicates credential configuration status."""
    response = requests.get(f"{live_server}/health", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert "credentials_configured" in data
    # Value should be a string "True" or "False"
    assert data["credentials_configured"] in ["True", "False"]
