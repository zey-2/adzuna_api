"""Adzuna Job Search MCP Server using FastAPI-MCP.

This server exposes Adzuna Job Search API endpoints as MCP tools
that can be used by AI assistants.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP


def load_env(path: str = ".env") -> None:
    """Populate environment variables from a simple KEY=VALUE .env file."""
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


# Load environment variables
load_env()

# Get Adzuna API credentials from environment
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
    print(
        "Warning: ADZUNA_APP_ID and ADZUNA_APP_KEY not set. "
        "Please set them in your .env file or environment variables."
    )


# Pydantic models for request/response
class JobSearchResponse(BaseModel):
    """Response model for job search."""
    count: int = Field(..., description="Total number of matching jobs")
    results: list[dict[str, Any]] = Field(..., description="List of job listings")


class JobDetails(BaseModel):
    """Detailed job information."""
    id: str = Field(..., description="Job ID")
    title: str = Field(..., description="Job title")
    company: dict[str, Any] = Field(..., description="Company information")
    location: dict[str, Any] = Field(..., description="Location information")
    description: str = Field(..., description="Job description")
    redirect_url: str = Field(..., description="URL to apply for the job")
    salary_min: Optional[float] = Field(None, description="Minimum salary")
    salary_max: Optional[float] = Field(None, description="Maximum salary")


# Initialize FastAPI app
app = FastAPI(
    title="Adzuna Job Search API",
    description="MCP server for searching and retrieving job listings from Adzuna",
    version="1.0.0",
)


@app.get(
    "/jobs/search",
    response_model=JobSearchResponse,
    operation_id="search_jobs",
    tags=["jobs"],
    summary="Search for jobs",
    description="Search for job listings on Adzuna with various filters"
)
async def search_jobs(
    what: str = Query(
        ...,
        description="Keywords to search for (e.g., 'data scientist', 'software engineer')"
    ),
    where: Optional[str] = Query(
        None,
        description="Location to search in (e.g., 'Singapore', 'New York')"
    ),
    country: str = Query(
        "sg",
        description="Country code (e.g., 'sg' for Singapore, 'us' for USA, 'gb' for UK)"
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number for pagination (starts at 1)"
    ),
    results_per_page: int = Query(
        10,
        ge=1,
        le=50,
        description="Number of results per page (1-50)"
    ),
    sort_by: Optional[str] = Query(
        None,
        description="Sort order: 'date' (newest first), 'salary' (highest first), or 'relevance'"
    ),
    full_time: Optional[bool] = Query(
        None,
        description="Filter for full-time positions only"
    ),
    part_time: Optional[bool] = Query(
        None,
        description="Filter for part-time positions only"
    ),
    contract: Optional[bool] = Query(
        None,
        description="Filter for contract positions only"
    ),
    permanent: Optional[bool] = Query(
        None,
        description="Filter for permanent positions only"
    ),
    salary_min: Optional[int] = Query(
        None,
        description="Minimum salary filter"
    ),
    salary_max: Optional[int] = Query(
        None,
        description="Maximum salary filter"
    ),
) -> JobSearchResponse:
    """Search for jobs using the Adzuna API."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise HTTPException(
            status_code=500,
            detail="Adzuna API credentials not configured. Please set ADZUNA_APP_ID and ADZUNA_APP_KEY."
        )
    
    # Build the API endpoint URL
    endpoint = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
    
    # Build query parameters
    params: dict[str, Any] = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what": what,
        "content-type": "application/json",
    }
    
    # Add optional parameters
    if where:
        params["where"] = where
    if sort_by:
        params["sort_by"] = sort_by
    if full_time is not None:
        params["full_time"] = 1 if full_time else 0
    if part_time is not None:
        params["part_time"] = 1 if part_time else 0
    if contract is not None:
        params["contract"] = 1 if contract else 0
    if permanent is not None:
        params["permanent"] = 1 if permanent else 0
    if salary_min is not None:
        params["salary_min"] = salary_min
    if salary_max is not None:
        params["salary_max"] = salary_max
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return JobSearchResponse(
            count=data.get("count", 0),
            results=data.get("results", [])
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Adzuna API: {str(e)}"
        )


@app.get(
    "/jobs/top-companies",
    response_model=dict,
    operation_id="get_top_companies",
    tags=["jobs"],
    summary="Get top hiring companies",
    description="Get the top companies currently hiring in a specific country"
)
async def get_top_companies(
    country: str = Query(
        "sg",
        description="Country code (e.g., 'sg' for Singapore, 'us' for USA)"
    ),
) -> dict[str, Any]:
    """Get top hiring companies from Adzuna API."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise HTTPException(
            status_code=500,
            detail="Adzuna API credentials not configured."
        )
    
    endpoint = f"https://api.adzuna.com/v1/api/jobs/{country}/top_companies"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Adzuna API: {str(e)}"
        )


@app.get(
    "/jobs/histogram",
    response_model=dict,
    operation_id="get_salary_histogram",
    tags=["jobs"],
    summary="Get salary histogram",
    description="Get salary distribution histogram for job search results"
)
async def get_salary_histogram(
    what: str = Query(
        ...,
        description="Keywords to search for (e.g., 'data scientist')"
    ),
    country: str = Query(
        "sg",
        description="Country code (e.g., 'sg' for Singapore)"
    ),
    where: Optional[str] = Query(
        None,
        description="Location to search in"
    ),
) -> dict[str, Any]:
    """Get salary histogram for job search results."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise HTTPException(
            status_code=500,
            detail="Adzuna API credentials not configured."
        )
    
    endpoint = f"https://api.adzuna.com/v1/api/jobs/{country}/histogram"
    params: dict[str, Any] = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": what,
    }
    
    if where:
        params["where"] = where
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Adzuna API: {str(e)}"
        )


@app.get(
    "/health",
    operation_id="health_check",
    tags=["system"],
    summary="Health check",
    description="Check if the API is running and configured"
)
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    credentials_set = bool(ADZUNA_APP_ID and ADZUNA_APP_KEY)
    return {
        "status": "healthy",
        "credentials_configured": str(credentials_set),
    }


# Create MCP server from FastAPI app
mcp = FastApiMCP(
    app,
    name="Adzuna Job Search MCP",
    description="MCP server for searching and retrieving job listings from Adzuna API",
)

# Mount the MCP server
mcp.mount_http()


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Adzuna Job Search MCP Server...")
    print(f"   API docs: http://localhost:8000/docs")
    print(f"   MCP endpoint: http://localhost:8000/mcp")
    print()
    
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("⚠️  Warning: Adzuna credentials not configured!")
        print("   Please set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file")
        print()
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
