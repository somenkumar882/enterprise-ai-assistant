# Using Elasticsearch as Query Response Database

This guide explains how to use Elasticsearch to store and retrieve all query responses in your Enterprise AI Assistant.

## Architecture

### Two Elasticsearch Indexes

Your Elasticsearch setup now maintains two indexes:

1. **`documents` index** - Stores knowledge base documents for search
2. **`documents-queries` index** - Stores all query requests and responses

### Data Flow

```
User Query
    ↓
Check Cache (Elasticsearch queries index)
    ├─ Cache Hit → Return cached answer (instant)
    └─ Cache Miss ↓
        Search Documents (Elasticsearch documents index)
            ↓
        Generate Answer (OpenAI)
            ↓
        Store Response (Elasticsearch queries index)
            ↓
        Return to User
```

## API Endpoints

### 1. Ask a Question (with automatic storage)

**POST** `/api/ask`

Store query responses and enable caching.

```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Who is the Prime Minister of India?",
    "use_cache": true
  }'
```

**Response:**
```json
{
  "answer": "Narendra Modi",
  "sources": [
    "Who is Prime minister of India? Narendra Modi"
  ],
  "cached": false,
  "id": "abc123def456",
  "timestamp": "2024-05-16T10:30:45.123456"
}
```

**Query Parameters:**
- `use_cache` (boolean, default: true) - Check for cached responses before generating new answers

### 2. Get Query History

**GET** `/api/query-history`

Retrieve stored query responses from Elasticsearch database.

```bash
# Get latest 10 queries
curl "http://localhost:8000/api/query-history?limit=10"

# Search for specific queries
curl "http://localhost:8000/api/query-history?query=Prime%20Minister&limit=20"
```

**Response:**
```json
{
  "total": 2,
  "responses": [
    {
      "id": "abc123def456",
      "query": "Who is the Prime Minister of India?",
      "answer": "Narendra Modi",
      "sources": ["Who is Prime minister of India? Narendra Modi"],
      "timestamp": "2024-05-16T10:30:45.123456",
      "source_count": 1
    },
    {
      "id": "def456ghi789",
      "query": "What is the capital of India?",
      "answer": "New Delhi",
      "sources": ["What is capital of India? New Delhi"],
      "timestamp": "2024-05-16T10:25:30.654321",
      "source_count": 1
    }
  ]
}
```

### 3. Get All Stored Queries

**GET** `/api/all-queries`

Retrieve all stored queries in reverse chronological order (most recent first).

```bash
curl "http://localhost:8000/api/all-queries?limit=50"
```

### 4. Retrieve Specific Response by ID

**GET** `/api/response/{response_id}`

Get a specific stored query response using its ID.

```bash
curl "http://localhost:8000/api/response/abc123def456"
```

**Response:**
```json
{
  "id": "abc123def456",
  "query": "Who is the Prime Minister of India?",
  "answer": "Narendra Modi",
  "sources": ["Who is Prime minister of India? Narendra Modi"],
  "timestamp": "2024-05-16T10:30:45.123456",
  "source_count": 1
}
```

## Features

### Automatic Caching

When `use_cache=true`, the system:
1. Searches for similar queries using fuzzy matching
2. Returns cached answers instantly without calling OpenAI
3. Saves costs and improves response time

**Example:**
```bash
# First call (generates answer)
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Prime Minister of India", "use_cache": true}'

# Second call (returns cached answer instantly)
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is Prime Minister", "use_cache": true}'
```

### Query Search

Search through stored queries and responses using Elasticsearch full-text search:

```bash
# Find all queries about India
curl "http://localhost:8000/api/query-history?query=India"

# Find all queries about presidents
curl "http://localhost:8000/api/query-history?query=President"
```

## Database Schema

### documents-queries Index Mappings

```json
{
  "mappings": {
    "properties": {
      "query": {
        "type": "text"
      },
      "answer": {
        "type": "text"
      },
      "sources": {
        "type": "nested",
        "properties": {
          "content": {
            "type": "text"
          }
        }
      },
      "timestamp": {
        "type": "date"
      },
      "source_count": {
        "type": "integer"
      }
    }
  }
}
```

## Elasticsearch Storage Functions

All storage functions are available in `app/services/search_service.py`:

### Store a Response
```python
from app.services.search_service import store_query_response

response_id = store_query_response(
    query="Your question",
    answer="The generated answer",
    sources=["source1", "source2"]
)
```

### Retrieve Responses
```python
from app.services.search_service import retrieve_query_responses

# Get latest 10 responses
responses = retrieve_query_responses(limit=10)

# Search for specific queries
responses = retrieve_query_responses(query_text="India", limit=20)
```

### Check Cache
```python
from app.services.search_service import check_cached_response

cached = check_cached_response("Your question")
if cached:
    print(f"Found cached answer: {cached['answer']}")
```

## Performance Optimization

### Query Optimization

1. **Fuzzy Matching** - Automatically handles typos and variations
2. **Full-Text Search** - Indexes both questions and answers
3. **Sorting by Timestamp** - Most recent responses first

### Index Configuration

The `documents-queries` index uses:
- 1 shard (suitable for queries index)
- 0 replicas (local development; adjust for production)
- Nested arrays for sources (efficient storage)

### For Production

Update your Elasticsearch settings in `app/core/config.py`:

```python
# More shards for distributed queries
"number_of_shards": 3,

# More replicas for high availability
"number_of_replicas": 2
```

## Monitoring Query Storage

### Check Index Statistics

```bash
# Get index stats
curl "http://localhost:9200/documents-queries/_stats"

# Get document count
curl "http://localhost:9200/documents-queries/_count"
```

### Search Elasticsearch Directly

```bash
# Get last 5 queries from Elasticsearch
curl -X GET "localhost:9200/documents-queries/_search?size=5" -H 'Content-Type: application/json' -d'
{
  "sort": [{"timestamp": {"order": "desc"}}]
}'
```

## Example Workflow

```bash
# 1. Start the application
docker-compose up

# 2. Ask a question (stored in Elasticsearch)
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the capital of France?"}'

# 3. Ask similar question (returns from cache)
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is capital of France?"}'

# 4. View query history
curl "http://localhost:8000/api/query-history?limit=10"

# 5. Search for queries about France
curl "http://localhost:8000/api/query-history?query=France"

# 6. Get specific response
curl "http://localhost:8000/api/response/abc123def456"
```

## Troubleshooting

### Index Not Created

Ensure Elasticsearch is running and accessible:
```bash
curl http://localhost:9200
```

### Cache Not Working

- Verify Elasticsearch connection is successful
- Check Elasticsearch logs for errors
- Ensure `use_cache=true` in request

### Query History Empty

- Make sure queries have been stored (call `/ask` endpoint first)
- Check if `documents-queries` index exists in Elasticsearch
- Verify Elasticsearch is storing documents

## Related Documentation

- [Elasticsearch Official Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Main README](README.md)
- [Search Service Implementation](app/services/search_service.py)
