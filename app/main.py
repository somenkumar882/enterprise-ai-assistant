
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from app.api.routes import query, upload
import os

app = FastAPI(title="Enterprise AI Assistant")

app.include_router(query.router)
app.include_router(upload.router)

# Get the base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Serve chat UI
@app.get("/")
async def root():
    """Serve the ChatGPT-like chat interface"""
    chat_file = os.path.join(BASE_DIR, "chat.html")
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"error": f"Chat file not found at {chat_file}"}

@app.get("/chat")
async def chat():
    """Alternative route to access chat interface"""
    chat_file = os.path.join(BASE_DIR, "chat.html")
    try:
        with open(chat_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return HTMLResponse(content=content)
    except FileNotFoundError:
        return {"error": f"Chat file not found at {chat_file}"}
