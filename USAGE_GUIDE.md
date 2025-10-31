# How to Use the Adzuna MCP Service

Your Adzuna Job Search MCP Server is deployed and ready to use!

**Service URL:** https://adzuna-mcp-server-236255620233.us-central1.run.app

---

## 🤖 Method 1: Use with Claude Desktop (Easiest)

### Step 1: Open Claude Desktop Configuration

**Windows:**
```powershell
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

**macOS/Linux:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Step 2: Add This Configuration

```json
{
  "mcpServers": {
    "adzuna-jobs": {
      "url": "https://adzuna-mcp-server-236255620233.us-central1.run.app/mcp"
    }
  }
}
```

### Step 3: Restart Claude Desktop

### Step 4: Try These Prompts

- "Search for data scientist jobs in Singapore"
- "What are the top hiring companies in the UK?"
- "Show me salary ranges for software engineers in New York"
- "Find part-time jobs in London"
- "What companies are hiring the most in Singapore?"

---

## 🌐 Method 2: Direct API Access

### Interactive API Documentation

Visit: https://adzuna-mcp-server-236255620233.us-central1.run.app/docs

This provides a Swagger UI where you can test all endpoints directly in your browser.

### Available Endpoints

#### 1. Search Jobs
```
GET /jobs/search
```

**Parameters:**
- `what` (required): Job keywords (e.g., "data scientist")
- `where` (optional): Location (e.g., "Singapore")
- `country`: Country code (default: "sg")
- `page`: Page number (default: 1)
- `results_per_page`: Results per page (default: 10, max: 50)
- `sort_by`: "date", "salary", or "relevance"
- `full_time`, `part_time`, `contract`, `permanent`: Boolean filters
- `salary_min`, `salary_max`: Salary filters

**Example:**
```
https://adzuna-mcp-server-236255620233.us-central1.run.app/jobs/search?what=python+developer&country=sg&results_per_page=5
```

#### 2. Get Top Companies
```
GET /jobs/top-companies
```

**Parameters:**
- `country`: Country code (default: "sg")

**Example:**
```
https://adzuna-mcp-server-236255620233.us-central1.run.app/jobs/top-companies?country=us
```

#### 3. Get Salary Histogram
```
GET /jobs/histogram
```

**Parameters:**
- `what` (required): Job keywords
- `country`: Country code (default: "sg")
- `where` (optional): Location

**Example:**
```
https://adzuna-mcp-server-236255620233.us-central1.run.app/jobs/histogram?what=software+engineer&country=sg
```

#### 4. Health Check
```
GET /health
```

**Example:**
```
https://adzuna-mcp-server-236255620233.us-central1.run.app/health
```

---

## 💻 Method 3: Programmatic Access

### Python Example

```python
import requests

BASE_URL = "https://adzuna-mcp-server-236255620233.us-central1.run.app"

# Search for jobs
response = requests.get(
    f"{BASE_URL}/jobs/search",
    params={
        "what": "data scientist",
        "where": "Singapore",
        "country": "sg",
        "results_per_page": 10,
        "sort_by": "salary"
    }
)
jobs = response.json()
print(f"Found {jobs['count']} jobs")

for job in jobs['results'][:5]:
    print(f"- {job['title']} at {job['company']['display_name']}")
    print(f"  {job['location']['display_name']}")
    if job.get('salary_min'):
        print(f"  Salary: ${job['salary_min']:,.0f} - ${job['salary_max']:,.0f}")
    print()

# Get top companies
response = requests.get(
    f"{BASE_URL}/jobs/top-companies",
    params={"country": "sg"}
)
companies = response.json()
print(f"\nTop {len(companies['leaderboard'])} companies:")
for i, company in enumerate(companies['leaderboard'][:10], 1):
    print(f"{i}. {company['canonical_name']}")
```

### JavaScript Example

```javascript
const BASE_URL = 'https://adzuna-mcp-server-236255620233.us-central1.run.app';

// Search for jobs
async function searchJobs() {
  const response = await fetch(
    `${BASE_URL}/jobs/search?what=software+engineer&country=us&results_per_page=5`
  );
  const data = await response.json();
  console.log(`Found ${data.count} jobs`);
  data.results.forEach(job => {
    console.log(`- ${job.title} at ${job.company.display_name}`);
  });
}

// Get top companies
async function getTopCompanies() {
  const response = await fetch(`${BASE_URL}/jobs/top-companies?country=sg`);
  const data = await response.json();
  console.log('Top companies:', data.leaderboard.slice(0, 5));
}

searchJobs();
getTopCompanies();
```

### PowerShell Example

```powershell
$BASE_URL = "https://adzuna-mcp-server-236255620233.us-central1.run.app"

# Search for jobs
$jobs = Invoke-RestMethod -Uri "$BASE_URL/jobs/search" -Body @{
    what = "data analyst"
    country = "sg"
    results_per_page = 5
}

Write-Host "Found $($jobs.count) jobs:"
$jobs.results | ForEach-Object {
    Write-Host "- $($_.title) at $($_.company.display_name)"
}

# Get top companies
$companies = Invoke-RestMethod -Uri "$BASE_URL/jobs/top-companies?country=sg"
Write-Host "`nTop companies:"
$companies.leaderboard[0..4] | ForEach-Object {
    Write-Host "- $($_.canonical_name)"
}
```

---

## 🧪 Testing the Service

Run the test script:

```powershell
.\test_deployment.ps1
```

This will test all endpoints and open the API documentation in your browser.

---

## 📊 Supported Countries

Use these country codes in your requests:

| Country | Code |
|---------|------|
| Singapore | `sg` |
| United States | `us` |
| United Kingdom | `gb` |
| Australia | `au` |
| Canada | `ca` |
| Germany | `de` |
| France | `fr` |
| Netherlands | `nl` |
| India | `in` |
| South Africa | `za` |
| New Zealand | `nz` |
| Poland | `pl` |
| Brazil | `br` |
| Austria | `at` |
| Belgium | `be` |
| Switzerland | `ch` |
| Italy | `it` |
| Mexico | `mx` |

---

## 🔒 Security & Cost

- **Authentication:** None required (public access)
- **Rate Limiting:** Subject to Adzuna API limits
- **Cost:** Free tier optimized
  - Scales to zero when not in use
  - First 2M requests/month free
  - Region: us-central1 (lowest cost)

---

## 📈 Monitoring

View service metrics and logs:
https://console.cloud.google.com/run?project=job-rec-repo

---

## 🛠️ Troubleshooting

### Service Not Responding
- Check service status: `https://adzuna-mcp-server-236255620233.us-central1.run.app/health`
- View logs in GCP Console

### API Errors
- Verify your Adzuna API credentials are valid
- Check if you've exceeded API rate limits
- Ensure country code is supported

### MCP Not Working in Claude
- Verify Claude Desktop is restarted after config changes
- Check config file syntax is valid JSON
- Ensure MCP endpoint URL is correct

---

## 🔄 Updating the Service

To redeploy with changes:

```powershell
# Build new image
gcloud builds submit --tag gcr.io/job-rec-repo/adzuna-mcp-server

# Deploy
gcloud run deploy adzuna-mcp-server `
  --image gcr.io/job-rec-repo/adzuna-mcp-server `
  --region us-central1
```

---

## 📞 Quick Reference

- **API Docs:** https://adzuna-mcp-server-236255620233.us-central1.run.app/docs
- **Health Check:** https://adzuna-mcp-server-236255620233.us-central1.run.app/health
- **MCP Endpoint:** https://adzuna-mcp-server-236255620233.us-central1.run.app/mcp
- **GCP Console:** https://console.cloud.google.com/run?project=job-rec-repo

Enjoy using your MCP-enabled job search service! 🚀
