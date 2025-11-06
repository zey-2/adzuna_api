# Deployment script for Adzuna MCP Server to Google Cloud Run
# This script automates the deployment process

$ErrorActionPreference = "Continue"

Write-Host "🚀 Deploying Adzuna MCP Server to Google Cloud Run..." -ForegroundColor Cyan
Write-Host ""

# Get project ID
$PROJECT_ID = gcloud config get-value project
if ([string]::IsNullOrEmpty($PROJECT_ID)) {
    Write-Host "❌ No GCP project configured. Run: gcloud config set project YOUR_PROJECT_ID" -ForegroundColor Red
    exit 1
}

Write-Host "📋 Project ID: $PROJECT_ID" -ForegroundColor Green
Write-Host ""

# Set region
$REGION = "us-central1"
gcloud config set run/region $REGION
Write-Host "📍 Region: $REGION" -ForegroundColor Green
Write-Host ""

# Enable required services
Write-Host "🔧 Enabling required GCP services..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com --quiet
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet
Write-Host "✅ Services enabled" -ForegroundColor Green
Write-Host ""

# Check if secrets exist, if not create them
Write-Host "🔐 Checking Adzuna API credentials..." -ForegroundColor Yellow

$secretsExist = $true
try {
    gcloud secrets describe adzuna-app-id --quiet 2>$null
    Write-Host "  ✓ Secret 'adzuna-app-id' exists" -ForegroundColor Gray
} catch {
    $secretsExist = $false
    Write-Host "  ⚠ Secret 'adzuna-app-id' not found" -ForegroundColor Yellow
}

try {
    gcloud secrets describe adzuna-app-key --quiet 2>$null
    Write-Host "  ✓ Secret 'adzuna-app-key' exists" -ForegroundColor Gray
} catch {
    $secretsExist = $false
    Write-Host "  ⚠ Secret 'adzuna-app-key' not found" -ForegroundColor Yellow
}

if (-not $secretsExist) {
    Write-Host ""
    Write-Host "❌ Adzuna API credentials not configured!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please create secrets manually:" -ForegroundColor Yellow
    Write-Host '  echo -n "your_app_id" | gcloud secrets create adzuna-app-id --data-file=-' -ForegroundColor Cyan
    Write-Host '  echo -n "your_app_key" | gcloud secrets create adzuna-app-key --data-file=-' -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Or set them from .env file if you have one." -ForegroundColor Yellow
    
    # Check if .env file exists
    if (Test-Path ".env") {
        Write-Host ""
        $response = Read-Host "Found .env file. Create secrets from .env? (y/n)"
        if ($response -eq "y") {
            $envContent = Get-Content ".env"
            $appId = ($envContent | Select-String "ADZUNA_APP_ID=(.+)").Matches.Groups[1].Value
            $appKey = ($envContent | Select-String "ADZUNA_APP_KEY=(.+)").Matches.Groups[1].Value
            
            if ($appId -and $appKey) {
                Write-Host "Creating secrets from .env file..." -ForegroundColor Cyan
                echo $appId | gcloud secrets create adzuna-app-id --data-file=-
                echo $appKey | gcloud secrets create adzuna-app-key --data-file=-
                Write-Host "✅ Secrets created successfully" -ForegroundColor Green
            } else {
                Write-Host "❌ Could not find credentials in .env file" -ForegroundColor Red
                exit 1
            }
        } else {
            exit 1
        }
    } else {
        exit 1
    }
}

Write-Host ""

# Grant service account access to secrets
Write-Host "🔑 Granting service account access to secrets..." -ForegroundColor Yellow
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

gcloud secrets add-iam-policy-binding adzuna-app-id `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --quiet

gcloud secrets add-iam-policy-binding adzuna-app-key `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor" `
    --quiet

Write-Host "✅ Permissions configured" -ForegroundColor Green
Write-Host ""

# Build container using Cloud Build
Write-Host "🏗️  Building container image with Cloud Build..." -ForegroundColor Yellow
Write-Host "   This may take 2-3 minutes..." -ForegroundColor Gray
gcloud builds submit --tag gcr.io/$PROJECT_ID/adzuna-mcp-server --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Container built successfully" -ForegroundColor Green
Write-Host ""

# Deploy to Cloud Run
Write-Host "🚢 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy adzuna-mcp-server `
    --image gcr.io/$PROJECT_ID/adzuna-mcp-server `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --min-instances 0 `
    --max-instances 10 `
    --memory 512Mi `
    --cpu 1 `
    --timeout 300s `
    --concurrency 80 `
    --update-secrets "ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest" `
    --quiet

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Deployment successful!" -ForegroundColor Green
Write-Host ""

# Get service URL
$SERVICE_URL = gcloud run services describe adzuna-mcp-server `
    --region $REGION `
    --format "value(status.url)"

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Cyan
Write-Host ""
Write-Host "📚 API Documentation: $SERVICE_URL/docs" -ForegroundColor Yellow
Write-Host "🔌 MCP Endpoint: $SERVICE_URL/mcp" -ForegroundColor Yellow
Write-Host "💚 Health Check: $SERVICE_URL/health" -ForegroundColor Yellow
Write-Host ""
Write-Host "Testing health endpoint..." -ForegroundColor Gray
try {
    $health = Invoke-RestMethod -Uri "$SERVICE_URL/health" -Method Get
    Write-Host "✅ Health check passed: $($health.status)" -ForegroundColor Green
    Write-Host "   Credentials configured: $($health.credentials_configured)" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Could not reach health endpoint (this is normal if it's still starting)" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Available MCP Tools:" -ForegroundColor Cyan
Write-Host "  • search_jobs - Search for job listings" -ForegroundColor Gray
Write-Host "  • get_categories - List available job categories" -ForegroundColor Gray
Write-Host "  • get_top_companies - Get top hiring companies" -ForegroundColor Gray
Write-Host "  • get_salary_histogram - Get salary distribution" -ForegroundColor Gray
Write-Host "  • get_geodata - Get salary data for locations" -ForegroundColor Gray
Write-Host "  • get_salary_history - Get historical salary data" -ForegroundColor Gray
Write-Host "  • get_api_version - Get Adzuna API version" -ForegroundColor Gray
Write-Host "  • health_check - Check server health" -ForegroundColor Gray
Write-Host ""
