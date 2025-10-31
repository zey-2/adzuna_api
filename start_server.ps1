# PowerShell script to start Adzuna MCP Server
Write-Host "Starting Adzuna MCP Server on port 7000..." -ForegroundColor Cyan
Write-Host ""

# Check if port 7000 is already in use
$portInUse = Get-NetTCPConnection -LocalPort 7000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "ERROR: Port 7000 is already in use!" -ForegroundColor Red
    Write-Host "The server may already be running at http://localhost:7000/docs" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To stop the existing server, run: Get-Process -Id $($portInUse.OwningProcess) | Stop-Process -Force" -ForegroundColor Yellow
    exit 1
}

Write-Host "Port 7000 is available. Starting server..." -ForegroundColor Green
Write-Host ""

# Start the server using the conda environment Python
& "C:\Users\bitrunner1\.conda\envs\adzuna-mcp\python.exe" server.py
