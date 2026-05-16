# Quick Start: Elasticsearch Query Storage

## Summary of Changes

Your Enterprise AI Assistant now stores ALL query responses in Elasticsearch automatically.

## What Changed

### Before
```
User Query → OpenAI → Response → User
(No storage/history)
```

### After
```
User Query → Check Cache (ES) 
            → Search Docs (ES) 
            → OpenAI 
            → Store Response (ES) 
            → Response + ID
(Full query history with caching)
```

## Quick Test

### 1. Start Services
```bash
docker-compose up --build
```

### 2. Ask a Question (First Call - Generates Answer)
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is Prime Minister of India?"}'
```

Response:
```json
{
  "answer": "Narendra Modi",
  "sources": ["Who is Prime minister of India? Narendra Modi"],
  "cached": false,
  "id": "abc123def456"
}
```

### 3. Ask Similar Question (Cached - Instant)
```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is the PM of India?"}'
```

Response:
```json
{
  "answer": "Narendra Modi",
  "sources": ["Who is Prime minister of India? Narendra Modi"],
  "cached": true,
  "id": "abc123def456"
}
```

### 4. View All Query History
```bash
curl "http://localhost:8000/api/query-history"
```

### 5. Search Query History
```bash
curl "http://localhost:8000/api/query-history?query=India"
```

### 6. Get Specific Response
```bash
curl "http://localhost:8000/api/response/abc123def456"
```

## Key Features

✅ **Automatic Storage** - Every query automatically stored in Elasticsearch  
✅ **Query Caching** - Fuzzy matching caches similar queries (saves OpenAI calls)  
✅ **Query History** - Retrieve all past queries and responses  
✅ **Search Queries** - Full-text search across questions and answers  
✅ **Response IDs** - Track specific responses by ID  
✅ **Timestamps** - Know when each query was asked  

## Available Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/ask` | POST | Ask question with auto-storage & caching |
| `/api/query-history` | GET | Get stored queries (optionally search) |
| `/api/all-queries` | GET | Get all queries (most recent first) |
| `/api/response/{id}` | GET | Get specific response by ID |

## Environment Variables

Already configured in `.env.example`:
```env
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=documents
```

Elasticsearch automatically creates two indexes:
- `documents` - Knowledge base documents
- `documents-queries` - Query responses database

## Database Queries (Direct Elasticsearch)

### Get Last 5 Queries
```bash
curl -X GET "localhost:9200/documents-queries/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "size": 5,
    "sort": [{"timestamp": {"order": "desc"}}]
  }'
```

### Count Total Stored Queries
```bash
curl "http://localhost:9200/documents-queries/_count"
```

### Search by Keyword
```bash
curl -X GET "localhost:9200/documents-queries/_search" \
  -H 'Content-Type: application/json' \
  -d '{
    "query": {
      "multi_match": {
        "query": "India",
        "fields": ["query", "answer"]
      }
    }
  }'
```

## How It Works Behind the Scenes

1. **User asks question** → `/api/ask` endpoint
2. **Cache check** → Searches for similar questions in `documents-queries` index
3. **If cached** → Returns stored answer immediately
4. **If not cached** → 
   - Searches `documents` index for relevant info
   - Calls OpenAI to generate answer
   - Stores query + answer + sources in `documents-queries` index
5. **Returns response with ID** → Used to retrieve later

## Next Steps

1. Review [ELASTICSEARCH_USAGE_GUIDE.md](ELASTICSEARCH_USAGE_GUIDE.md) for detailed documentation
2. Test endpoints with provided curl examples
3. Monitor Elasticsearch with `docker logs` commands
4. Adjust caching strategy based on your needs

## Cost Savings with Caching

With intelligent caching:
- **Reduced API calls** - Similar questions answered from cache
- **Faster responses** - Cached answers returned instantly
- **Lower costs** - Fewer OpenAI API calls

Example: If 30% of queries are similar to previous ones, you save ~30% on OpenAI costs!

---

See [ELASTICSEARCH_USAGE_GUIDE.md](ELASTICSEARCH_USAGE_GUIDE.md) for comprehensive documentation.
