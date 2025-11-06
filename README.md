# Adzuna Job Search MCP Server

A Model Context Protocol (MCP) server that exposes the [Adzuna Job Search API](https://developer.adzuna.com/) as MCP tools, allowing AI assistants to search and retrieve job listings programmatically.

This project uses [fastapi_mcp](https://github.com/tadata-org/fastapi_mcp) to automatically convert FastAPI endpoints into MCP tools.

## Features

- 🔍 **Job Search**: Search for jobs with filters like location, salary, job type
- 🏢 **Top Companies**: Get top hiring companies by country
- 📊 **Salary Histogram**: View salary distributions for job searches
- 🤖 **AI-Ready**: Exposes all functionality as MCP tools for AI assistants
- 📝 **Auto-Generated Documentation**: FastAPI provides interactive API docs
- 🔒 **Environment-Based Configuration**: Secure credential management

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io/) is an emerging standard that defines how AI agents communicate with applications. By exposing your API through MCP, you enable AI assistants (like Claude, ChatGPT, and others) to interact with your services directly.

## Prerequisites

- Python 3.13+
- Conda (Anaconda or Miniconda)
- Adzuna API credentials (get them from [https://developer.adzuna.com/](https://developer.adzuna.com/))

## Installation

1. **Clone or navigate to this repository**

2. **Create and activate conda environment**

   **Option A: Using environment.yml (Recommended)**

   ```bash
   # Create conda environment from environment.yml
   conda env create -f environment.yml

   # Activate the environment
   conda activate adzuna-mcp
   ```

   **Option B: Manual setup**

   ```bash
   # Create conda environment with Python 3.13
   conda create -n adzuna-mcp python=3.13 -y

   # Activate the environment
   conda activate adzuna-mcp

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your Adzuna credentials:

   ```bash
   ADZUNA_APP_ID=your_actual_app_id
   ADZUNA_APP_KEY=your_actual_app_key
   ```

## Usage

### Running the Server

Start the MCP server:

```bash
python server.py
```

The server will start on `http://localhost:7000` with:

- **API Documentation**: http://localhost:7000/docs
- **MCP Endpoint**: http://localhost:7000/mcp

### Testing with MCP Inspector

You can test your MCP server using the official MCP Inspector:

1. Start your server (see above)

2. In a new terminal, run the MCP Inspector:

   ```bash
   npx @modelcontextprotocol/inspector
   ```

3. Connect to your MCP server at `http://127.0.0.1:7000/mcp`

4. Navigate to the **Tools** section and click **List Tools** to see all available endpoints

5. Test an endpoint by selecting it, filling in parameters, and clicking **Run Tool**

### Using with AI Assistants

To connect this MCP server to an AI assistant (like Claude Desktop), add the following configuration to your MCP settings:

```json
{
  "mcpServers": {
    "adzuna-jobs": {
      "url": "http://localhost:7000/mcp"
    }
  }
}
```

## Available MCP Tools

The server exposes the following tools that AI assistants can use:

### 1. `search_jobs`

Search for job listings with various filters.

**Parameters:**

- `what` (required): Keywords to search for (e.g., "data scientist", "software engineer")
- `where` (optional): Location to search in (e.g., "Singapore", "New York")
- `country` (default: "sg"): Country code (sg, us, gb, etc.)
- `page` (default: 1): Page number for pagination
- `results_per_page` (default: 10, max: 50): Number of results per page
- `sort_by` (optional): Sort order - "date", "salary", or "relevance"
- `full_time`, `part_time`, `contract`, `permanent` (optional): Job type filters
- `what_and` (optional): Keywords that must all be found
- `what_phrase` (optional): An entire phrase that must be found
- `what_or` (optional): Keywords where any may be found
- `what_exclude` (optional): Keywords to exclude
- `title_only` (optional): Keywords to find only in the title
- `distance` (optional): Distance in km from the 'where' location
- `max_days_old` (optional): Maximum age of the advertisement in days
- `category` (optional): Category tag to filter by
- `sort_dir` (optional): Sort direction ('up' or 'down')
- `salary_include_unknown` (optional): Include jobs with unknown salaries
- `company` (optional): Filter by a specific company name

**Example:**

```python
# Search for data scientist jobs in Singapore
{
  "what": "data scientist",
  "where": "Singapore",
  "country": "sg",
  "results_per_page": 20
}
```

### 2. `get_categories`

Get a list of available job categories for a specific country.

**Parameters:**

- `country` (default: "sg"): Country code

**Example:**

```python
# Get all available job categories in Singapore
{
  "country": "sg"
}
```

### 3. `get_top_companies`

Get the top companies currently hiring in a specific country.

**Parameters:**

- `country` (default: "sg"): Country code
- `what` (optional): Keywords to search for
- `category` (optional): Category tag to filter by

**Example:**

```python
# Get top hiring companies in Singapore
{
  "country": "sg"
}
```

### 4. `get_salary_histogram`

Get salary distribution histogram for job search results.

**Parameters:**

- `country` (default: "sg"): Country code
- `what` (optional): Keywords to search for
- `where` (optional): Location to search in
- `category` (optional): Category tag to filter by

**Example:**

```python
# Get salary distribution for data scientist roles
{
  "what": "data scientist",
  "country": "sg"
}
```

### 5. `health_check`

Check if the API is running and properly configured.

**Parameters:** None

## API Endpoints (Direct REST Access)

You can also use the FastAPI endpoints directly without MCP:

- `GET /jobs/search` - Search for jobs
- `GET /jobs/categories` - List available job categories
- `GET /jobs/top-companies` - Get top hiring companies
- `GET /jobs/histogram` - Get salary histogram
- `GET /health` - Health check

Visit `http://localhost:7000/docs` for interactive API documentation.

## Project Structure

```
adzuna_api/
├── server.py           # Main MCP server implementation
├── adzuna_example.py   # Original example script
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variable template
├── .env               # Your actual credentials (gitignored)
└── README.md          # This file
```

## How It Works

1. **FastAPI Application**: The `server.py` file defines a FastAPI application with endpoints for the Adzuna API
2. **MCP Integration**: Using `fastapi_mcp`, the FastAPI app is wrapped to create an MCP server
3. **Automatic Tool Generation**: Each FastAPI endpoint is automatically exposed as an MCP tool with proper schemas
4. **AI Assistant Integration**: AI assistants can discover and call these tools through the MCP protocol

## Development

### Adding New Endpoints

To add new Adzuna API endpoints:

1. Define a new FastAPI endpoint in `server.py`:

   ```python
   @app.get(
       "/jobs/new-endpoint",
       operation_id="new_tool_name",
       tags=["jobs"]
   )
   async def new_endpoint(param: str):
       # Your implementation
       pass
   ```

2. The endpoint will automatically be exposed as an MCP tool named `new_tool_name`

3. Restart the server to see the new tool

### Customizing MCP Configuration

You can customize the MCP server behavior:

```python
mcp = FastApiMCP(
    app,
    name="Custom MCP Name",
    description="Custom description",
    describe_all_responses=True,  # Include all response schemas
    describe_full_response_schema=True,  # Full JSON schema in descriptions
)
```

## Country Codes

Common Adzuna country codes:

- `sg` - Singapore
- `us` - United States
- `gb` - United Kingdom
- `au` - Australia
- `ca` - Canada
- `de` - Germany
- `fr` - France
- `nl` - Netherlands
- `nz` - New Zealand
- `pl` - Poland
- `za` - South Africa

[See full list](https://developer.adzuna.com/docs/api)

## Testing

### Running Tests

This project includes comprehensive tests with 95%+ code coverage.

Install development dependencies:

```bash
pip install pytest pytest-cov pytest-asyncio requests-mock httpx pytest-mock
```

Or use the Makefile:

Run all tests:

```bash
pytest tests/ -v
```

Run with coverage report (95% threshold):

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
# Open htmlcov/index.html in your browser after running test-cov
```

### Test Structure

- `tests/conftest.py` - Shared fixtures and test configuration
- `tests/test_endpoints.py` - FastAPI endpoint tests (40+ tests)
- `tests/test_mcp_tools.py` - MCP protocol compliance tests (30+ tests)
- `tests/test_integration.py` - End-to-end integration tests (15+ tests)

## Deployment

### Google Cloud Run Deployment

This MCP server can be deployed to Google Cloud Run with free tier support (2M requests/month, 180K vCPU-seconds, 360K GiB-seconds).

**See [DEPLOYMENT.md](DEPLOYMENT.md) for complete step-by-step deployment instructions.**

#### Quick Deploy

```powershell
# Set your GCP project ID
$env:PROJECT_ID = "your-gcp-project-id"

# Build and deploy
gcloud builds submit --tag gcr.io/$env:PROJECT_ID/adzuna-mcp-server
gcloud run deploy adzuna-mcp-server `
    --image gcr.io/$env:PROJECT_ID/adzuna-mcp-server `
    --region us-central1 `
    --platform managed `
    --allow-unauthenticated `
    --min-instances 0 `
    --update-secrets ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest
```

Or use the Makefile:

#### Deployment Features

- ✅ Free tier optimized (us-central1 region)
- ✅ Min instances: 0 (no idle cost, accepts cold starts ~1-3s)
- ✅ Public access (no authentication required)
- ✅ Secret Manager integration for credentials
- ✅ Auto-scaling (0-10 instances)
- ✅ 512MB memory, 1 vCPU
- ✅ 300s timeout

### Local Docker Testing

Build and test locally before deploying:

```bash
# Build image
docker build -t adzuna-mcp-server .

# Run locally
docker run -p 7000:7000 `
    -e ADZUNA_APP_ID=your_id `
    -e ADZUNA_APP_KEY=your_key `
    -e PORT=7000 `
    adzuna-mcp-server

# Test
curl http://localhost:7000/health
```

### Connecting to Deployed Service

Add to your Claude Desktop MCP configuration:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "adzuna-jobs": {
      "url": "https://your-service-url.run.app/mcp"
    }
  }
}
```

Replace `your-service-url.run.app` with your actual Cloud Run service URL.

## Troubleshooting

### API Credentials Not Working

- Verify your credentials at https://developer.adzuna.com/
- Ensure `.env` file is in the same directory as `server.py`
- Check that there are no extra spaces in your `.env` file

### MCP Connection Issues

- Ensure the server is running (`python server.py`)
- Verify the MCP endpoint is accessible at `http://localhost:8000/mcp`
- Check firewall settings if connecting remotely

### No Results Returned

- Try broader search terms
- Check if the country code is correct
- Verify the API credentials are valid

### Tests Failing

- Ensure all dev dependencies are installed (see "Running Tests" install step)
- Check that environment variables are mocked properly
- Run individual test files to isolate issues: `pytest tests/test_endpoints.py -v`

### Docker Build Issues

- Ensure Docker is running
- Check that Dockerfile and .dockerignore are present
- Verify Python dependencies are correct in requirements.txt

### Cloud Run Deployment Issues

- Ensure gcloud CLI is installed and authenticated
- Verify GCP project is set: `gcloud config get-value project`
- Check that required APIs are enabled (Run, Build, Secret Manager)
- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting

## Resources

- [Adzuna API Documentation](https://developer.adzuna.com/docs/api)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [FastAPI-MCP Documentation](https://github.com/tadata-org/fastapi_mcp)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Acknowledgments

- Built with [FastAPI-MCP](https://github.com/tadata-org/fastapi_mcp) by Tadata
- Powered by [Adzuna Job Search API](https://developer.adzuna.com/)
- Uses the [Model Context Protocol](https://modelcontextprotocol.io/)
