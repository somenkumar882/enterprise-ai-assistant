# Elasticsearch Connection Troubleshooting Guide

## Error: "Failed to connect to Elasticsearch: Failed to ping Elasticsearch"

This error means the FastAPI application cannot connect to the Elasticsearch server. Here are the solutions:

## Quick Fixes

### Option 1: Start Elasticsearch with Docker Compose (Recommended)

This is the easiest way to get Elasticsearch running locally:

```bash
# Make sure you're in the project directory
cd c:\Users\LENOVO\Documents\enterprise-ai-assistant

# Start all services including Elasticsearch
docker-compose up --build
```

This will:
- Start Elasticsearch on `http://localhost:9200`
- Start Redis on `http://localhost:6379`
- Start your FastAPI app on `http://localhost:8000`

Wait 30-60 seconds for Elasticsearch to fully initialize before making requests.

### Option 2: Manual Elasticsearch Setup

If you have Elasticsearch already installed or prefer to run it separately:

```bash
# Make sure Elasticsearch is running on localhost:9200
# Then run the troubleshooting script
python troubleshoot_elasticsearch.py
```

### Option 3: Use Environment Variables to Connect to Remote Elasticsearch

If you have Elasticsearch running on a different machine:

Create/update your `.env` file:
```env
ELASTICSEARCH_HOST=your-elasticsearch-host
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=your-password
ELASTICSEARCH_INDEX=documents
```

## Troubleshooting Steps

### Step 1: Run the Diagnostic Script

```bash
python troubleshoot_elasticsearch.py
```

This will check:
- Port connectivity
- HTTP connection
- Elasticsearch Python client connection
- Cluster information
- Existing indexes

### Step 2: Verify Docker Container Status

```bash
# Check if containers are running
docker-compose ps

# Expected output:
# NAME                        STATUS
# enterprise-ai-assistant-elasticsearch-1    Up
# enterprise-ai-assistant-redis-1            Up
# enterprise-ai-assistant-api-1              Up
```

### Step 3: Check Elasticsearch Logs

```bash
# View Elasticsearch container logs
docker-compose logs elasticsearch

# Watch logs in real-time
docker-compose logs -f elasticsearch
```

### Step 4: Test Direct Connection

```bash
# Test if Elasticsearch is responding
curl http://localhost:9200/

# Expected output (JSON cluster info)
{
  "name": "...",
  "cluster_name": "docker-cluster",
  "version": {...},
  ...
}
```

## Common Issues & Solutions

### Issue 1: Port 9200 Already in Use

**Error:** `Address already in use: ('127.0.0.1', 9200)`

**Solution:**
```bash
# Option A: Find and stop the process using port 9200
netstat -ano | findstr :9200
taskkill /PID <process_id> /F

# Option B: Use a different port in docker-compose.yml
# Change:   "9200:9200"
# To:       "9201:9200"
# Then update .env: ELASTICSEARCH_PORT=9201
```

### Issue 2: Docker Container Won't Start

**Error:** `Container exited with code 1`

**Solution:**
```bash
# Check logs
docker-compose logs elasticsearch

# Common fixes:
# 1. Not enough memory (Elasticsearch needs ~512MB)
# 2. Volume permission issues
# 3. Port conflicts

# Clean up and restart
docker-compose down
docker system prune -f
docker-compose up --build
```

### Issue 3: Elasticsearch Takes Too Long to Start

**Problem:** Container is running but not ready to accept connections

**Solution:**
```bash
# Wait for Elasticsearch to be ready
# It can take 30-60 seconds on first startup

# Option A: Wait and check status
for i in {1..60}; do
    curl -s http://localhost:9200/_cluster/health && break || sleep 1
done

# Option B: Use the app normally, it will retry automatically
```

### Issue 4: Connection Times Out

**Error:** `ConnectionError: Connection timeout`

**Causes:**
- Elasticsearch not running
- Wrong host/port in `.env`
- Firewall blocking connection
- Network issues

**Solutions:**
```bash
# Check connection parameters
cat .env | grep ELASTICSEARCH

# Verify connectivity
ping localhost
curl http://localhost:9200

# Check if port is open
netstat -ano | findstr :9200

# Test with explicit host resolution
curl http://127.0.0.1:9200
```

## Configuration Reference

### Connection Parameters (.env)

```env
# Elasticsearch settings
ELASTICSEARCH_HOST=localhost          # Host or IP
ELASTICSEARCH_PORT=9200               # Port number
ELASTICSEARCH_USERNAME=elastic        # Username (optional)
ELASTICSEARCH_PASSWORD=changeme       # Password (optional)
ELASTICSEARCH_INDEX=documents         # Index name prefix
```

### For Local Development

```env
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme
```

### For Docker Compose

```env
ELASTICSEARCH_HOST=elasticsearch      # Service name in docker-compose.yml
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme
```

### For Remote Server

```env
ELASTICSEARCH_HOST=your-server.com
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=your-user
ELASTICSEARCH_PASSWORD=your-password
```

## Advanced Debugging

### Enable Debug Logging

Add this to your FastAPI startup:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# In app/services/search_service.py
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Connecting to Elasticsearch at {host}:{port}")
```

### Test Elasticsearch Directly

```python
# Run in Python REPL
from elasticsearch import Elasticsearch

client = Elasticsearch(["http://localhost:9200"])
print(client.ping())  # Should return True
print(client.info())  # Should print cluster info
```

### Check Index Status

```bash
# List all indexes
curl http://localhost:9200/_cat/indices

# Get index settings
curl http://localhost:9200/documents/_settings

# Get index mappings
curl http://localhost:9200/documents/_mappings
```

## Connection Flow

The application tries to connect in this order:

```
1. Try Elasticsearch
   ├─ Success → Use Elasticsearch for storage
   └─ Fail ↓
2. Try Azure Cognitive Search
   ├─ Success → Use Azure Search
   └─ Fail ↓
3. Use Mock Search (local development)
   └─ No external dependencies, works offline
```

If Elasticsearch fails, the app automatically falls back to Azure Search or Mock Search.

## Performance Optimization

### For Production

```bash
# Update docker-compose.yml
environment:
  - ES_JAVA_OPTS=-Xms512m -Xmx512m  # Adjust memory as needed
  - discovery.type=single-node      # For single node clusters
```

### Monitor Health

```bash
# Check cluster health
curl http://localhost:9200/_cluster/health

# Get node stats
curl http://localhost:9200/_nodes/stats

# Monitor pending tasks
curl http://localhost:9200/_cluster/pending_tasks
```

## Getting Help

If you're still having issues:

1. **Run the diagnostic script:**
   ```bash
   python troubleshoot_elasticsearch.py
   ```

2. **Check the logs:**
   ```bash
   docker-compose logs elasticsearch
   ```

3. **Verify connectivity manually:**
   ```bash
   curl http://localhost:9200/
   ```

4. **Ensure Docker is running:**
   ```bash
   docker --version
   docker-compose --version
   ```

## Next Steps

Once Elasticsearch is connected:

1. Start your FastAPI app:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

2. Test the API:
   ```bash
   curl -X POST "http://localhost:8000/api/ask" \
     -H "Content-Type: application/json" \
     -d '{"query": "Who is Prime Minister of India?"}'
   ```

3. View query history:
   ```bash
   curl "http://localhost:8000/api/query-history"
   ```

See [ELASTICSEARCH_USAGE_GUIDE.md](ELASTICSEARCH_USAGE_GUIDE.md) for full API documentation.
