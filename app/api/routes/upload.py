
from fastapi import APIRouter, UploadFile
from app.workers.tasks import process_document

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile):
    content = await file.read()
    process_document.delay(content.decode())
    return {"message": "Processing started"}
