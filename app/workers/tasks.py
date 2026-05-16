
from app.workers.celery_app import celery
from app.services.embedding_service import get_embedding
from app.services.search_service import client

@celery.task
def process_document(text):
    chunks = text.split("\n")
    for chunk in chunks:
        emb = get_embedding(chunk)
        client.upload_documents([{
            "id": chunk[:50],
            "content": chunk,
            "embedding": emb
        }])
    return "done"
