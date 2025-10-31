@echo off
echo Starting Adzuna MCP Server on port 7000...
echo.
echo Checking if port 7000 is already in use...
netstat -ano | findstr :7000 > nul
if %ERRORLEVEL% EQU 0 (
    echo ERROR: Port 7000 is already in use!
    echo Please stop the existing server first or use the running instance at http://localhost:7000/docs
    pause
    exit /b 1
)
echo Port 7000 is available. Starting server...
echo.
C:\Users\bitrunner1\.conda\envs\adzuna-mcp\python.exe server.py
