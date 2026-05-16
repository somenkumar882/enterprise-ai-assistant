
from fastapi import APIRouter
from app.services.openai_service import generate_answer
from app.services.search_service import search_documents

router = APIRouter()

@router.post("/ask")
async def ask_question(query: str):
    docs = search_documents(query)
    answer = generate_answer(query, docs)
    return {"answer": answer, "sources": docs}
