
from fastapi import APIRouter, Query as QueryParam
from pydantic import BaseModel
from app.services.openai_service import generate_answer
from app.services.search_service import (
    search_documents, 
    store_query_response, 
    retrieve_query_responses,
    get_query_response_by_id,
    check_cached_response
)

router = APIRouter(prefix="/api", tags=["queries"])

class QueryRequest(BaseModel):
    query: str
    use_cache: bool = True

@router.post("/ask")
async def ask_question(request: QueryRequest):
    """
    Ask a question and get an answer with automatic Elasticsearch storage.
    
    The response includes:
    - answer: Generated answer from OpenAI
    - sources: Relevant documents used
    - cached: Whether the response was retrieved from cache
    - id: Elasticsearch document ID for retrieval
    - timestamp: When the response was stored
    """
    query_text = request.query
    use_cache = request.use_cache
    
    # Check cache first if enabled
    if use_cache:
        cached = check_cached_response(query_text)
        if cached:
            return {
                "answer": cached["answer"],
                "sources": cached["sources"],
                "cached": True,
                "id": cached.get("id"),
                "timestamp": cached.get("timestamp")
            }
    
    # Search for relevant documents
    docs = search_documents(query_text)
    
    # Generate answer using OpenAI
    answer = generate_answer(query_text, docs)
    
    # Store in Elasticsearch
    response_id = store_query_response(query_text, answer, docs)
    
    # Get the timestamp from the stored response
    stored_response = get_query_response_by_id(response_id) if response_id else None
    timestamp = stored_response.get("timestamp") if stored_response else None
    
    return {
        "answer": answer,
        "sources": docs,
        "cached": False,
        "id": response_id,
        "timestamp": timestamp
    }

@router.get("/query-history")
async def get_query_history(
    query: str = QueryParam(None, description="Search for specific queries"),
    limit: int = QueryParam(10, ge=1, le=100)
):
    """Retrieve stored query responses from Elasticsearch database"""
    responses = retrieve_query_responses(query_text=query, limit=limit)
    return {
        "total": len(responses),
        "responses": responses
    }

@router.get("/response/{response_id}")
async def get_response(response_id: str):
    """Retrieve a specific stored response by ID"""
    response = get_query_response_by_id(response_id)
    if response:
        return response
    return {"error": "Response not found", "id": response_id}

@router.get("/all-queries")
async def get_all_queries(limit: int = QueryParam(50, ge=1, le=500)):
    """Get all stored queries in chronological order (most recent first)"""
    responses = retrieve_query_responses(limit=limit)
    return {
        "total": len(responses),
        "responses": responses
    }
