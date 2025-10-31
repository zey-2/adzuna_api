# Google Cloud Run Deployment Guide

This guide provides step-by-step instructions for deploying the Adzuna Job Search MCP Server to Google Cloud Run.

## Prerequisites

Before deploying, ensure you have:

- **Google Cloud Account** with billing enabled
- **gcloud CLI** installed and configured ([Installation Guide](https://cloud.google.com/sdk/docs/install))
- **Docker** installed for local testing ([Installation Guide](https://docs.docker.com/get-docker/))
- **Adzuna API credentials** from [https://developer.adzuna.com/](https://developer.adzuna.com/)
- **GCP Project** created or selected

## Initial GCP Setup

### 1. Authenticate with Google Cloud

```powershell
# Login to Google Cloud
gcloud auth login

# Set your project ID
$PROJECT_ID = "your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Set Default Region

For free tier optimization, use `us-central1`:

```powershell
gcloud config set run/region us-central1
```

**Free Tier Details:**
- **Region:** All regions eligible, but `us-central1` uses Tier 1 pricing (lowest cost)
- **Monthly Limits:** 2M requests, 180K vCPU-seconds, 360K GiB-seconds
- **Network:** 1 GB outbound data from North America per month

## Configure Adzuna API Credentials

### Using Google Secret Manager (Recommended)

```powershell
# Create secrets for Adzuna credentials
echo -n "your_adzuna_app_id" | gcloud secrets create adzuna-app-id --data-file=-
echo -n "your_adzuna_app_key" | gcloud secrets create adzuna-app-key --data-file=-

# Get your project number
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"

# Grant Cloud Run service account access to secrets
gcloud secrets add-iam-policy-binding adzuna-app-id `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding adzuna-app-key `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor"
```

## Local Docker Testing (Optional but Recommended)

Test your Docker container locally before deploying:

### Build the Docker Image

```powershell
docker build -t adzuna-mcp-server .
```

### Run Locally

```powershell
docker run -p 7000:7000 `
    -e ADZUNA_APP_ID=your_app_id `
    -e ADZUNA_APP_KEY=your_app_key `
    -e PORT=7000 `
    adzuna-mcp-server
```

### Test Endpoints

```powershell
# Test health check
curl http://localhost:7000/health

# Test API docs
Start-Process "http://localhost:7000/docs"

# Test MCP tools list
curl -X POST http://localhost:7000/mcp `
    -H "Content-Type: application/json" `
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Test MCP tool call
curl -X POST http://localhost:7000/mcp `
    -H "Content-Type: application/json" `
    -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search_jobs","arguments":{"what":"data scientist","country":"sg"}}}'
```

## Deploy to Google Cloud Run

### Method 1: Using Cloud Build (Recommended)

```powershell
# Build container image using Cloud Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/adzuna-mcp-server

# Deploy to Cloud Run
gcloud run deploy adzuna-mcp-server `
    --image gcr.io/$PROJECT_ID/adzuna-mcp-server `
    --region us-central1 `
    --platform managed `
    --allow-unauthenticated `
    --min-instances 0 `
    --max-instances 10 `
    --memory 512Mi `
    --cpu 1 `
    --timeout 300s `
    --concurrency 80 `
    --update-secrets ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest
```

### Method 2: Using Local Docker Build

```powershell
# Configure Docker for GCR
gcloud auth configure-docker

# Tag your local image
docker tag adzuna-mcp-server gcr.io/$PROJECT_ID/adzuna-mcp-server

# Push to Google Container Registry
docker push gcr.io/$PROJECT_ID/adzuna-mcp-server

# Deploy to Cloud Run
gcloud run deploy adzuna-mcp-server `
    --image gcr.io/$PROJECT_ID/adzuna-mcp-server `
    --region us-central1 `
    --platform managed `
    --allow-unauthenticated `
    --min-instances 0 `
    --update-secrets ADZUNA_APP_ID=adzuna-app-id:latest,ADZUNA_APP_KEY=adzuna-app-key:latest
```

### Deployment Configuration Explained

- `--allow-unauthenticated`: Public access (no authentication required)
- `--min-instances 0`: Scale to zero when not in use (free tier optimized)
- `--max-instances 10`: Maximum concurrent instances
- `--memory 512Mi`: Memory allocation per instance
- `--cpu 1`: CPU allocation (1 vCPU)
- `--timeout 300s`: Request timeout (5 minutes)
- `--concurrency 80`: Max concurrent requests per instance
- `--update-secrets`: Mount secrets as environment variables

## Verify Deployment

### Get Service URL

```powershell
$SERVICE_URL = gcloud run services describe adzuna-mcp-server `
    --region us-central1 `
    --format "value(status.url)"

Write-Host "Service URL: $SERVICE_URL"
```

### Test Deployed Service

```powershell
# Test health endpoint
curl $SERVICE_URL/health

# Test MCP endpoint
curl -X POST $SERVICE_URL/mcp `
    -H "Content-Type: application/json" `
    -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

# Open API documentation
Start-Process "$SERVICE_URL/docs"
```

## Connect from Claude Desktop

Add to your Claude Desktop MCP configuration:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "adzuna-jobs": {
      "url": "https://your-service-url/mcp"
    }
  }
}
```

Replace `your-service-url` with your actual Cloud Run service URL.

## Update Deployment

To update your deployed service with new code:

```powershell
# Rebuild and redeploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/adzuna-mcp-server

gcloud run deploy adzuna-mcp-server `
    --image gcr.io/$PROJECT_ID/adzuna-mcp-server `
    --region us-central1
```

## Monitoring and Logs

### View Logs

```powershell
# Stream logs in real-time
gcloud run services logs tail adzuna-mcp-server --region us-central1

# Read recent logs
gcloud run services logs read adzuna-mcp-server --region us-central1 --limit 50
```

### Monitor Metrics

View metrics in the GCP Console:

```powershell
# Open Cloud Run console
Start-Process "https://console.cloud.google.com/run"
```

Key metrics to monitor:
- **Request count** - Stay under 2M/month for free tier
- **CPU utilization** - Monitor vCPU-seconds usage
- **Memory utilization** - Monitor GiB-seconds usage
- **Response time** - Track cold start impact
- **Error rate** - Monitor 4xx/5xx responses

### View Service Details

```powershell
gcloud run services describe adzuna-mcp-server --region us-central1
```

## Cost Optimization

### Free Tier Limits

- **Requests:** 2 million requests/month
- **CPU Time:** 180,000 vCPU-seconds/month
- **Memory Time:** 360,000 GiB-seconds/month
- **Network:** 1 GB outbound from North America/month

### Optimization Tips

1. **Use min-instances: 0** - No idle costs, accepts cold starts (~1-3 seconds)
2. **Deploy in us-central1** - Tier 1 pricing region
3. **Set appropriate timeout** - Default 300s, reduce if possible
4. **Optimize container size** - Faster cold starts
5. **Monitor usage** - Set up billing alerts

### Set Up Billing Alerts

```powershell
# Create billing budget alert
gcloud billing budgets create `
    --billing-account=BILLING_ACCOUNT_ID `
    --display-name="Cloud Run Budget" `
    --budget-amount=10USD `
    --threshold-rule=percent=50 `
    --threshold-rule=percent=90 `
    --threshold-rule=percent=100
```

## Troubleshooting

### Common Issues

**1. Secret Access Denied**

If you see "failed to access secret" errors:

```powershell
# Verify service account has access
gcloud secrets get-iam-policy adzuna-app-id

# Re-grant access if needed
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
gcloud secrets add-iam-policy-binding adzuna-app-id `
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" `
    --role="roles/secretmanager.secretAccessor"
```

**2. Container Build Fails**

Check Cloud Build logs:

```powershell
gcloud builds log --region=us-central1
```

**3. Service Returns 500 Errors**

Check service logs:

```powershell
gcloud run services logs read adzuna-mcp-server --region us-central1 --limit 100
```

**4. Cold Start Timeout**

Increase timeout or use min-instances > 0:

```powershell
gcloud run services update adzuna-mcp-server `
    --region us-central1 `
    --timeout 600s
```

**5. Out of Memory**

Increase memory allocation:

```powershell
gcloud run services update adzuna-mcp-server `
    --region us-central1 `
    --memory 1Gi
```

### Health Check Debug

```powershell
# Check health endpoint
curl $SERVICE_URL/health

# Expected response:
# {"status":"healthy","credentials_configured":"True"}
```

## Cleanup

To delete the service and associated resources:

```powershell
# Delete Cloud Run service
gcloud run services delete adzuna-mcp-server --region us-central1

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/adzuna-mcp-server

# Delete secrets
gcloud secrets delete adzuna-app-id
gcloud secrets delete adzuna-app-key
```

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Adzuna API Documentation](https://developer.adzuna.com/docs)
- [FastAPI MCP Documentation](https://github.com/tadata-org/fastapi_mcp)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io/)

## Support

For issues specific to:
- **Adzuna API:** Contact Adzuna support or check their documentation
- **Google Cloud Run:** Refer to GCP documentation or support
- **MCP Protocol:** Check the MCP specification or fastapi-mcp repository

## Security Considerations

1. **Secrets Management:** Always use Secret Manager for credentials, never commit secrets to git
2. **Public Access:** Service is configured for public access - consider adding authentication for production
3. **Rate Limiting:** Consider implementing rate limiting to prevent abuse
4. **API Key Rotation:** Regularly rotate your Adzuna API credentials
5. **Monitoring:** Set up alerts for unusual activity or high usage
