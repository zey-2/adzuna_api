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
- Adzuna API credentials (get them from [https://developer.adzuna.com/](https://developer.adzuna.com/))

## Installation

1. **Clone or navigate to this repository**

2. **Create and activate conda environment**

   ```bash
   # Create conda environment with Python 3.13
   conda create -n adzuna-mcp python=3.13 -y

   # Activate the environment
   conda activate adzuna-mcp
   ```

3. **Install dependencies**

   Using pip:

   ```bash
   pip install -r requirements.txt
   ```

   Or using uv (recommended):

   ```bash
   uv pip install -r requirements.txt
   ```

4. **Set up environment variables**

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

The server will start on `http://localhost:8000` with:

- **API Documentation**: http://localhost:8000/docs
- **MCP Endpoint**: http://localhost:8000/mcp

### Testing with MCP Inspector

You can test your MCP server using the official MCP Inspector:

1. Start your server (see above)

2. In a new terminal, run the MCP Inspector:

   ```bash
   npx @modelcontextprotocol/inspector
   ```

3. Connect to your MCP server at `http://127.0.0.1:8000/mcp`

4. Navigate to the **Tools** section and click **List Tools** to see all available endpoints

5. Test an endpoint by selecting it, filling in parameters, and clicking **Run Tool**

### Using with AI Assistants

To connect this MCP server to an AI assistant (like Claude Desktop), add the following configuration to your MCP settings:

```json
{
  "mcpServers": {
    "adzuna-jobs": {
      "url": "http://localhost:8000/mcp"
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
- `salary_min`, `salary_max` (optional): Salary range filters

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

### 2. `get_top_companies`

Get the top companies currently hiring in a specific country.

**Parameters:**

- `country` (default: "sg"): Country code

**Example:**

```python
# Get top hiring companies in Singapore
{
  "country": "sg"
}
```

### 3. `get_salary_histogram`

Get salary distribution histogram for job search results.

**Parameters:**

- `what` (required): Keywords to search for
- `country` (default: "sg"): Country code
- `where` (optional): Location to search in

**Example:**

```python
# Get salary distribution for data scientist roles
{
  "what": "data scientist",
  "country": "sg"
}
```

### 4. `health_check`

Check if the API is running and properly configured.

**Parameters:** None

## API Endpoints (Direct REST Access)

You can also use the FastAPI endpoints directly without MCP:

- `GET /jobs/search` - Search for jobs
- `GET /jobs/top-companies` - Get top hiring companies
- `GET /jobs/histogram` - Get salary histogram
- `GET /health` - Health check

Visit `http://localhost:8000/docs` for interactive API documentation.

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
