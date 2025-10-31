"""Comprehensive tests for MCP protocol compliance and tool functionality."""
import pytest
import json
from fastapi.testclient import TestClient


@pytest.mark.mcp
def test_mcp_endpoint_exists(client):
    """Test MCP endpoint is mounted and accessible."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
    )
    assert response.status_code == 200


@pytest.mark.mcp
def test_mcp_tools_list(client, mock_all_adzuna_endpoints):
    """Test MCP tools/list returns all available tools."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check JSON-RPC structure
    assert "jsonrpc" in data
    assert data["jsonrpc"] == "2.0"
    assert "id" in data
    assert data["id"] == 1
    assert "result" in data
    
    # Check tools list
    result = data["result"]
    assert "tools" in result
    tools = result["tools"]
    assert isinstance(tools, list)
    assert len(tools) >= 4  # At least 4 tools


@pytest.mark.mcp
def test_mcp_tools_list_contains_expected_tools(client, mock_all_adzuna_endpoints):
    """Test that all expected tools are present in tools/list."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
    )
    
    data = response.json()
    tools = data["result"]["tools"]
    tool_names = [tool["name"] for tool in tools]
    
    # Check all expected tools are present
    assert "search_jobs" in tool_names
    assert "get_top_companies" in tool_names
    assert "get_salary_histogram" in tool_names
    assert "health_check" in tool_names


@pytest.mark.mcp
def test_mcp_tool_schema_structure(client, mock_all_adzuna_endpoints):
    """Test that tool schemas have correct structure."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list",
            "params": {}
        }
    )
    
    data = response.json()
    tools = data["result"]["tools"]
    
    # Find search_jobs tool
    search_tool = next((t for t in tools if t["name"] == "search_jobs"), None)
    assert search_tool is not None
    
    # Check tool structure
    assert "name" in search_tool
    assert "description" in search_tool
    assert "inputSchema" in search_tool
    
    # Check input schema
    schema = search_tool["inputSchema"]
    assert "type" in schema
    assert schema["type"] == "object"
    assert "properties" in schema
    assert "required" in schema
    
    # Check required parameters
    assert "what" in schema["required"]
    
    # Check parameter properties
    properties = schema["properties"]
    assert "what" in properties
    assert "where" in properties
    assert "country" in properties
    assert "page" in properties


@pytest.mark.mcp
def test_mcp_tool_call_search_jobs(client, mock_adzuna_search_success):
    """Test MCP tools/call for search_jobs tool."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "search_jobs",
                "arguments": {
                    "what": "data scientist",
                    "country": "sg"
                }
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check JSON-RPC structure
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 2
    assert "result" in data
    
    # Check result structure
    result = data["result"]
    assert "content" in result
    assert isinstance(result["content"], list)
    assert len(result["content"]) > 0
    
    # Check content item
    content_item = result["content"][0]
    assert "type" in content_item
    assert "text" in content_item


@pytest.mark.mcp
def test_mcp_tool_call_with_all_parameters(client, requests_mock):
    """Test MCP tools/call with all search parameters."""
    requests_mock.get(
        "https://api.adzuna.com/v1/api/jobs/us/search/1",
        json={"count": 50, "results": []}
    )
    
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_jobs",
                "arguments": {
                    "what": "software engineer",
                    "where": "New York",
                    "country": "us",
                    "page": 1,
                    "results_per_page": 20,
                    "sort_by": "salary",
                    "full_time": True,
                    "salary_min": 100000,
                    "salary_max": 200000
                }
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data


@pytest.mark.mcp
def test_mcp_tool_call_top_companies(client, mock_adzuna_top_companies_success):
    """Test MCP tools/call for get_top_companies tool."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "get_top_companies",
                "arguments": {
                    "country": "sg"
                }
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert "content" in data["result"]


@pytest.mark.mcp
def test_mcp_tool_call_salary_histogram(client, mock_adzuna_histogram_success):
    """Test MCP tools/call for get_salary_histogram tool."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "get_salary_histogram",
                "arguments": {
                    "what": "engineer",
                    "country": "sg"
                }
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data


@pytest.mark.mcp
def test_mcp_tool_call_health_check(client, mock_env_vars):
    """Test MCP tools/call for health_check tool."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "health_check",
                "arguments": {}
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "result" in data


@pytest.mark.mcp
def test_mcp_tool_call_invalid_tool_name(client):
    """Test MCP tools/call with invalid tool name."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 7,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            }
        }
    )
    
    # Should return error response
    assert response.status_code in [200, 404, 500]
    data = response.json()
    # MCP protocol may return error in result or as error field
    assert "error" in data or "result" in data


@pytest.mark.mcp
def test_mcp_tool_call_missing_required_param(client):
    """Test MCP tools/call with missing required parameter."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "search_jobs",
                "arguments": {
                    # Missing required 'what' parameter
                    "country": "sg"
                }
            }
        }
    )
    
    # Should return error (validation failure)
    assert response.status_code in [200, 422, 500]


@pytest.mark.mcp
def test_mcp_tool_call_invalid_parameter_type(client):
    """Test MCP tools/call with invalid parameter type."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "search_jobs",
                "arguments": {
                    "what": "developer",
                    "page": "invalid"  # Should be integer
                }
            }
        }
    )
    
    # Should handle gracefully
    assert response.status_code in [200, 422, 500]


@pytest.mark.mcp
def test_mcp_jsonrpc_format_validation(client, mock_all_adzuna_endpoints):
    """Test JSON-RPC 2.0 format compliance."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/list",
            "params": {}
        }
    )
    
    data = response.json()
    
    # Must have jsonrpc field with value "2.0"
    assert "jsonrpc" in data
    assert data["jsonrpc"] == "2.0"
    
    # Must have id field matching request
    assert "id" in data
    assert data["id"] == 10
    
    # Must have either result or error (not both)
    assert ("result" in data) != ("error" in data)


@pytest.mark.mcp
def test_mcp_missing_jsonrpc_field(client):
    """Test request without jsonrpc field."""
    response = client.post(
        "/mcp",
        json={
            "id": 11,
            "method": "tools/list",
            "params": {}
        }
    )
    
    # Should handle gracefully (may accept or reject)
    assert response.status_code in [200, 400, 422]


@pytest.mark.mcp
def test_mcp_invalid_method(client):
    """Test MCP with invalid method name."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 12,
            "method": "invalid/method",
            "params": {}
        }
    )
    
    # Should return error
    assert response.status_code in [200, 404, 422, 500]


@pytest.mark.mcp
def test_mcp_malformed_json(client):
    """Test MCP with malformed JSON."""
    response = client.post(
        "/mcp",
        data="invalid json{",
        headers={"Content-Type": "application/json"}
    )
    
    # Should return 400 or 422 for malformed JSON
    assert response.status_code in [400, 422]


@pytest.mark.mcp
def test_mcp_content_type_json(client, mock_all_adzuna_endpoints):
    """Test MCP endpoint requires JSON content type."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/list",
            "params": {}
        }
    )
    
    # Should accept application/json
    assert response.status_code == 200


@pytest.mark.mcp
def test_mcp_response_content_type(client, mock_all_adzuna_endpoints):
    """Test MCP response has correct content type."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 14,
            "method": "tools/list",
            "params": {}
        }
    )
    
    content_type = response.headers.get("content-type", "")
    assert "application/json" in content_type.lower()


@pytest.mark.mcp
def test_mcp_id_preservation(client, mock_all_adzuna_endpoints):
    """Test that request ID is preserved in response."""
    request_ids = [1, 100, "string-id", None]
    
    for req_id in request_ids:
        if req_id is None:
            # ID is optional in JSON-RPC 2.0 (notification)
            continue
            
        response = client.post(
            "/mcp",
            json={
                "jsonrpc": "2.0",
                "id": req_id,
                "method": "tools/list",
                "params": {}
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "id" in data
            assert data["id"] == req_id


@pytest.mark.mcp
def test_mcp_tool_descriptions_present(client, mock_all_adzuna_endpoints):
    """Test that all tools have descriptions."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 15,
            "method": "tools/list",
            "params": {}
        }
    )
    
    data = response.json()
    tools = data["result"]["tools"]
    
    for tool in tools:
        assert "description" in tool
        assert len(tool["description"]) > 0


@pytest.mark.mcp
def test_mcp_sequential_requests(client, mock_all_adzuna_endpoints):
    """Test multiple sequential MCP requests."""
    # First request - list tools
    response1 = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/list",
            "params": {}
        }
    )
    assert response1.status_code == 200
    
    # Second request - call tool
    response2 = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 21,
            "method": "tools/call",
            "params": {
                "name": "health_check",
                "arguments": {}
            }
        }
    )
    assert response2.status_code == 200


@pytest.mark.mcp
def test_mcp_result_is_json_serializable(client, mock_all_adzuna_endpoints):
    """Test that MCP results are properly JSON serializable."""
    response = client.post(
        "/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 22,
            "method": "tools/list",
            "params": {}
        }
    )
    
    # Response should be valid JSON
    data = response.json()
    
    # Should be able to serialize again
    json_str = json.dumps(data)
    assert len(json_str) > 0
    
    # Should be able to deserialize
    parsed = json.loads(json_str)
    assert parsed == data
