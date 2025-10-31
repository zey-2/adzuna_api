# Test script for deployed Adzuna MCP Server
$BASE_URL = "https://adzuna-mcp-server-236255620233.us-central1.run.app"

Write-Host "`n=== Testing Adzuna MCP Server ===" -ForegroundColor Cyan
Write-Host "Service URL: $BASE_URL`n" -ForegroundColor Yellow

# Test 1: Health Check
Write-Host "1. Testing Health Check..." -ForegroundColor Green
$health = Invoke-RestMethod -Uri "$BASE_URL/health"
Write-Host "   Status: $($health.status)" -ForegroundColor White
Write-Host "   Credentials: $($health.credentials_configured)`n" -ForegroundColor White

# Test 2: Search Jobs
Write-Host "2. Testing Job Search (data scientist in Singapore)..." -ForegroundColor Green
$jobs = Invoke-RestMethod -Uri "$BASE_URL/jobs/search" -Method GET -Body @{
    what = "data scientist"
    where = "Singapore"
    country = "sg"
    results_per_page = 5
}
Write-Host "   Found: $($jobs.count) jobs" -ForegroundColor White
Write-Host "   Sample: $($jobs.results[0].title) at $($jobs.results[0].company.display_name)`n" -ForegroundColor White

# Test 3: Top Companies
Write-Host "3. Testing Top Companies (Singapore)..." -ForegroundColor Green
$companies = Invoke-RestMethod -Uri "$BASE_URL/jobs/top-companies" -Method GET -Body @{
    country = "sg"
}
Write-Host "   Top company: $($companies.leaderboard[0].canonical_name)`n" -ForegroundColor White

# Test 4: Salary Histogram
Write-Host "4. Testing Salary Histogram (software engineer)..." -ForegroundColor Green
$histogram = Invoke-RestMethod -Uri "$BASE_URL/jobs/histogram" -Method GET -Body @{
    what = "software engineer"
    country = "sg"
}
Write-Host "   Salary ranges found: $($histogram.histogram.salary.Count)`n" -ForegroundColor White

# Test 5: API Documentation
Write-Host "5. Opening API Documentation..." -ForegroundColor Green
Start-Process "$BASE_URL/docs"
Write-Host "   API docs opened in browser`n" -ForegroundColor White

Write-Host "=== All Tests Complete! ===" -ForegroundColor Cyan
Write-Host "`nYou can now use this service with Claude Desktop or any MCP-compatible client." -ForegroundColor Yellow
Write-Host "MCP Endpoint: $BASE_URL/mcp`n" -ForegroundColor Yellow
