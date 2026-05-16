
# Enterprise AI Assistant

Multi-backend search support with **Elasticsearch** (primary), Azure Cognitive Search (fallback), and mock search for local development.

## Features

- **Elasticsearch Integration**: Fast, scalable search with full-text capabilities
- **Azure Search Fallback**: Seamless fallback to Azure Cognitive Search
- **Mock Search**: Local development without external dependencies
- **FastAPI**: Modern async Python web framework
- **Celery Workers**: Background job processing

## Setup

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Elasticsearch (Primary)
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=elastic
ELASTICSEARCH_PASSWORD=changeme
ELASTICSEARCH_INDEX=documents

# OpenAI
OPENAI_API_KEY=your-api-key
OPENAI_ENDPOINT=your-endpoint

# Redis (for Celery)
REDIS_URL=redis://localhost:6379/0
```

### Quick Start with Docker Compose

```bash
docker-compose up --build
```

This will automatically start:
- **API** (FastAPI) on `http://localhost:8000`
- **Elasticsearch** on `http://localhost:9200`
- **Redis** on `http://localhost:6379`
- **Celery Worker** for background tasks

### Local Development Setup

1. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run with local Elasticsearch:
```bash
# Make sure Elasticsearch is running
python -m uvicorn app.main:app --reload
```

## Search Backends

The application automatically tries backends in this order:
1. **Elasticsearch** - Primary, fastest, most scalable
2. **Azure Cognitive Search** - Enterprise fallback
3. **Mock Search** - Local development/testing

## API Endpoints

- `GET /` - Health check
- `POST /search` - Search documents
- `POST /upload` - Upload documents
- `POST /query` - Query with OpenAI

## Docker Compose Services

| Service | Port | Purpose |
|---------|------|---------|
| api | 8000 | FastAPI application |
| elasticsearch | 9200 | Search backend |
| redis | 6379 | Cache & Celery broker |
| worker | - | Background task processor |

## Troubleshooting

**Elasticsearch connection issues:**
- Ensure `ELASTICSEARCH_HOST` and `ELASTICSEARCH_PORT` match your setup
- Check credentials if using authentication
- Verify Elasticsearch is running: `curl http://localhost:9200`

**Using Azure Search instead:**
- Set `ELASTICSEARCH_HOST` to unreachable value or remove Elasticsearch service
- Configure `SEARCH_ENDPOINT` and `SEARCH_KEY`
