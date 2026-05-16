
from fastapi import FastAPI
from app.api.routes import query, upload

app = FastAPI(title="Enterprise AI Assistant")

app.include_router(query.router)
app.include_router(upload.router)
