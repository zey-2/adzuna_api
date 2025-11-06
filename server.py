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


def remove_class_fields(data: Any) -> Any:
    """Recursively remove __CLASS__ fields from dictionaries and lists."""
    if isinstance(data, dict):
        return {
            key: remove_class_fields(value)
            for key, value in data.items()
            if key != "__CLASS__"
        }
    elif isinstance(data, list):
        return [remove_class_fields(item) for item in data]
    else:
        return data


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
    what_and: Optional[str] = Query(
        None,
        description="Keywords to search for (all keywords must be found)"
    ),
    what_phrase: Optional[str] = Query(
        None,
        description="An entire phrase which must be found in the description or title"
    ),
    what_or: Optional[str] = Query(
        None,
        description="Keywords to search for (any keywords may be found, space separated)"
    ),
    what_exclude: Optional[str] = Query(
        None,
        description="Keywords to exclude from the search (space separated)"
    ),
    title_only: Optional[str] = Query(
        None,
        description="Keywords to find, but only in the title (space separated)"
    ),
    distance: Optional[int] = Query(
        None,
        description="Distance in kilometres from the centre of the 'where' location (defaults to 5km)"
    ),
    location0: Optional[str] = Query(
        None,
        description="Location field for structured location search (e.g., 'UK')"
    ),
    location1: Optional[str] = Query(
        None,
        description="Location field level 1 (e.g., 'South East England')"
    ),
    location2: Optional[str] = Query(
        None,
        description="Location field level 2 (e.g., 'Surrey')"
    ),
    location3: Optional[str] = Query(
        None,
        description="Location field level 3"
    ),
    location4: Optional[str] = Query(
        None,
        description="Location field level 4"
    ),
    location5: Optional[str] = Query(
        None,
        description="Location field level 5"
    ),
    location6: Optional[str] = Query(
        None,
        description="Location field level 6"
    ),
    location7: Optional[str] = Query(
        None,
        description="Location field level 7"
    ),
    max_days_old: Optional[int] = Query(
        None,
        description="The age of the oldest advertisement in days that will be returned"
    ),
    category: Optional[str] = Query(
        None,
        description="The category tag, as returned by the 'category' endpoint"
    ),
    sort_dir: Optional[str] = Query(
        None,
        description="The direction to order the search results ('up' or 'down')"
    ),
    salary_include_unknown: Optional[bool] = Query(
        None,
        description="If set to True, jobs without a known salary are returned"
    ),
    company: Optional[str] = Query(
        None,
        description="The canonical company name to filter by"
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
    if what_and:
        params["what_and"] = what_and
    if what_phrase:
        params["what_phrase"] = what_phrase
    if what_or:
        params["what_or"] = what_or
    if what_exclude:
        params["what_exclude"] = what_exclude
    if title_only:
        params["title_only"] = title_only
    if distance is not None:
        params["distance"] = distance
    if location0:
        params["location0"] = location0
    if location1:
        params["location1"] = location1
    if location2:
        params["location2"] = location2
    if location3:
        params["location3"] = location3
    if location4:
        params["location4"] = location4
    if location5:
        params["location5"] = location5
    if location6:
        params["location6"] = location6
    if location7:
        params["location7"] = location7
    if max_days_old is not None:
        params["max_days_old"] = max_days_old
    if category:
        params["category"] = category
    if sort_dir:
        params["sort_dir"] = sort_dir
    if salary_include_unknown is not None:
        params["salary_include_unknown"] = 1 if salary_include_unknown else 0
    if company:
        params["company"] = company
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Clean the response data
        cleaned_data = remove_class_fields(data)
        
        results = cleaned_data.get("results", [])
        for job in results:
            job.pop('salary_min', None)
            job.pop('salary_max', None)
        
        return JobSearchResponse(
            count=cleaned_data.get("count", 0),
            results=results
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Adzuna API: {str(e)}"
        )


@app.get(
    "/jobs/categories",
    response_model=dict,
    operation_id="get_categories",
    tags=["jobs"],
    summary="List available job categories",
    description="Get a list of available job categories for a specific country"
)
async def get_categories(
    country: str = Query(
        "sg",
        description="Country code (e.g., 'sg' for Singapore, 'us' for USA, 'gb' for UK)"
    ),
) -> dict[str, Any]:
    """Get available job categories from Adzuna API."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise HTTPException(
            status_code=500,
            detail="Adzuna API credentials not configured."
        )
    
    endpoint = f"https://api.adzuna.com/v1/api/jobs/{country}/categories"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return remove_class_fields(data)
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
    what: Optional[str] = Query(
        None,
        description="Keywords to search for (space separated)"
    ),
    location0: Optional[str] = Query(
        None,
        description="Location field for structured location search"
    ),
    location1: Optional[str] = Query(
        None,
        description="Location field level 1"
    ),
    location2: Optional[str] = Query(
        None,
        description="Location field level 2"
    ),
    location3: Optional[str] = Query(
        None,
        description="Location field level 3"
    ),
    location4: Optional[str] = Query(
        None,
        description="Location field level 4"
    ),
    location5: Optional[str] = Query(
        None,
        description="Location field level 5"
    ),
    location6: Optional[str] = Query(
        None,
        description="Location field level 6"
    ),
    location7: Optional[str] = Query(
        None,
        description="Location field level 7"
    ),
    category: Optional[str] = Query(
        None,
        description="The category tag, as returned by the 'category' endpoint"
    ),
) -> dict[str, Any]:
    """Get top hiring companies from Adzuna API."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise HTTPException(
            status_code=500,
            detail="Adzuna API credentials not configured."
        )
    
    endpoint = f"https://api.adzuna.com/v1/api/jobs/{country}/top_companies"
    params: dict[str, Any] = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
    }
    
    # Add optional parameters
    if what:
        params["what"] = what
    if location0:
        params["location0"] = location0
    if location1:
        params["location1"] = location1
    if location2:
        params["location2"] = location2
    if location3:
        params["location3"] = location3
    if location4:
        params["location4"] = location4
    if location5:
        params["location5"] = location5
    if location6:
        params["location6"] = location6
    if location7:
        params["location7"] = location7
    if category:
        params["category"] = category
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return remove_class_fields(data)
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
    country: str = Query(
        "sg",
        description="Country code (e.g., 'sg' for Singapore)"
    ),
    what: Optional[str] = Query(
        None,
        description="Keywords to search for (space separated)"
    ),
    location0: Optional[str] = Query(
        None,
        description="Location field for structured location search"
    ),
    location1: Optional[str] = Query(
        None,
        description="Location field level 1"
    ),
    location2: Optional[str] = Query(
        None,
        description="Location field level 2"
    ),
    location3: Optional[str] = Query(
        None,
        description="Location field level 3"
    ),
    location4: Optional[str] = Query(
        None,
        description="Location field level 4"
    ),
    location5: Optional[str] = Query(
        None,
        description="Location field level 5"
    ),
    location6: Optional[str] = Query(
        None,
        description="Location field level 6"
    ),
    location7: Optional[str] = Query(
        None,
        description="Location field level 7"
    ),
    category: Optional[str] = Query(
        None,
        description="The category tag, as returned by the 'category' endpoint"
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
    }
    
    # Add optional parameters
    if what:
        params["what"] = what
    if location0:
        params["location0"] = location0
    if location1:
        params["location1"] = location1
    if location2:
        params["location2"] = location2
    if location3:
        params["location3"] = location3
    if location4:
        params["location4"] = location4
    if location5:
        params["location5"] = location5
    if location6:
        params["location6"] = location6
    if location7:
        params["location7"] = location7
    if category:
        params["category"] = category
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return remove_class_fields(data)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Adzuna API: {str(e)}"
        )


@app.get(
    "/jobs/geodata",
    response_model=dict,
    operation_id="get_geodata",
    tags=["jobs"],
    summary="Get salary data for locations",
    description="Provides salary data for locations inside an area"
)
async def get_geodata(
    country: str = Query(
        "sg",
        description="Country code (e.g., 'sg' for Singapore, 'us' for USA, 'gb' for UK)"
    ),
    location0: Optional[str] = Query(
        None,
        description="Location field for structured location search (e.g., 'UK')"
    ),
    location1: Optional[str] = Query(
        None,
        description="Location field level 1 (e.g., 'South East England')"
    ),
    location2: Optional[str] = Query(
        None,
        description="Location field level 2 (e.g., 'Surrey')"
    ),
    location3: Optional[str] = Query(
        None,
        description="Location field level 3"
    ),
    location4: Optional[str] = Query(
        None,
        description="Location field level 4"
    ),
    location5: Optional[str] = Query(
        None,
        description="Location field level 5"
    ),
    location6: Optional[str] = Query(
        None,
        description="Location field level 6"
    ),
    location7: Optional[str] = Query(
        None,
        description="Location field level 7"
    ),
    category: Optional[str] = Query(
        None,
        description="The category tag, as returned by the 'category' endpoint"
    ),
) -> dict[str, Any]:
    """Get salary data for locations inside an area from Adzuna API."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise HTTPException(
            status_code=500,
            detail="Adzuna API credentials not configured."
        )
    
    endpoint = f"https://api.adzuna.com/v1/api/jobs/{country}/geodata"
    params: dict[str, Any] = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
    }
    
    # Add optional parameters
    if location0:
        params["location0"] = location0
    if location1:
        params["location1"] = location1
    if location2:
        params["location2"] = location2
    if location3:
        params["location3"] = location3
    if location4:
        params["location4"] = location4
    if location5:
        params["location5"] = location5
    if location6:
        params["location6"] = location6
    if location7:
        params["location7"] = location7
    if category:
        params["category"] = category
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return remove_class_fields(data)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Adzuna API: {str(e)}"
        )


@app.get(
    "/jobs/history",
    response_model=dict,
    operation_id="get_salary_history",
    tags=["jobs"],
    summary="Get historical salary data",
    description="Provides historical average salary data over time"
)
async def get_salary_history(
    country: str = Query(
        "sg",
        description="Country code (e.g., 'sg' for Singapore, 'us' for USA, 'gb' for UK)"
    ),
    location0: Optional[str] = Query(
        None,
        description="Location field for structured location search"
    ),
    location1: Optional[str] = Query(
        None,
        description="Location field level 1"
    ),
    location2: Optional[str] = Query(
        None,
        description="Location field level 2"
    ),
    location3: Optional[str] = Query(
        None,
        description="Location field level 3"
    ),
    location4: Optional[str] = Query(
        None,
        description="Location field level 4"
    ),
    location5: Optional[str] = Query(
        None,
        description="Location field level 5"
    ),
    location6: Optional[str] = Query(
        None,
        description="Location field level 6"
    ),
    location7: Optional[str] = Query(
        None,
        description="Location field level 7"
    ),
    category: Optional[str] = Query(
        None,
        description="The category tag, as returned by the 'category' endpoint"
    ),
    months: Optional[int] = Query(
        None,
        description="The number of months back for which to retrieve data"
    ),
) -> dict[str, Any]:
    """Get historical average salary data from Adzuna API."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise HTTPException(
            status_code=500,
            detail="Adzuna API credentials not configured."
        )
    
    endpoint = f"https://api.adzuna.com/v1/api/jobs/{country}/history"
    params: dict[str, Any] = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
    }
    
    # Add optional parameters
    if location0:
        params["location0"] = location0
    if location1:
        params["location1"] = location1
    if location2:
        params["location2"] = location2
    if location3:
        params["location3"] = location3
    if location4:
        params["location4"] = location4
    if location5:
        params["location5"] = location5
    if location6:
        params["location6"] = location6
    if location7:
        params["location7"] = location7
    if category:
        params["category"] = category
    if months is not None:
        params["months"] = months
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return remove_class_fields(data)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Adzuna API: {str(e)}"
        )


@app.get(
    "/version",
    response_model=dict,
    operation_id="get_api_version",
    tags=["system"],
    summary="Get API version",
    description="Returns the current version of the Adzuna API"
)
async def get_api_version() -> dict[str, Any]:
    """Get the current version of the Adzuna API."""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise HTTPException(
            status_code=500,
            detail="Adzuna API credentials not configured."
        )
    
    endpoint = "https://api.adzuna.com/v1/api/version"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
    }
    
    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        return remove_class_fields(data)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Adzuna API: {str(e)}"
        )


@app.get(
    "/",
    include_in_schema=False,
)
async def root():
    """Redirect root to API documentation."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


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
    describe_full_response_schema=True,
)

# Mount the MCP server
mcp.mount_http()


if __name__ == "__main__":
    import uvicorn
    
    # Cloud Run provides PORT environment variable
    port = int(os.getenv("PORT", 7000))
    
    print("🚀 Starting Adzuna Job Search MCP Server...")
    print(f"   API docs: http://localhost:{port}/docs")
    print(f"   MCP endpoint: http://localhost:{port}/mcp")
    print()
    
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("⚠️  Warning: Adzuna credentials not configured!")
        print("   Please set ADZUNA_APP_ID and ADZUNA_APP_KEY in your environment")
        print()
    
    uvicorn.run(app, host="0.0.0.0", port=port)
