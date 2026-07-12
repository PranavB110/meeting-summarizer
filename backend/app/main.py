"""
Meeting Summarizer — FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.core.config import get_settings
from app.db.session import Base, engine
from app.models import meeting  
from app.api import health, meetings

settings = get_settings()

Path(settings.audio_storage_dir).mkdir(parents=True, exist_ok=True)
Path(settings.transcript_storage_dir).mkdir(parents=True, exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Meeting Summarizer API",
    description="Transcribe meeting audio and generate action-oriented summaries.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(meetings.router, prefix="/api")


FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "templates"


@app.get("/", response_class=HTMLResponse)
def root():
    html_path = FRONTEND_DIR / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/api")
def api_info():
    return {"message": "Meeting Summarizer API is running. See /docs for API documentation."}