from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ai_backend import generate_summary


# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(
    title="AI YouTube Video Summarizer API",
    description="Generate AI-powered summaries from YouTube videos using Groq LLM.",
    version="1.0.0"
)


# ==========================================================
# Request Model
# ==========================================================

class VideoRequest(BaseModel):
    """Request payload for the summarization endpoint."""

    url: str


# ==========================================================
# Root Endpoint
# ==========================================================

@app.get("/")
def home():

    return {
        "message": "AI YouTube Video Summarizer API is running.",
        "docs": "/docs"
    }


# ==========================================================
# Summarization Endpoint
# ==========================================================

@app.post("/summarize")
def summarize_video(request: VideoRequest):
    """Generate a summary for a valid YouTube video URL."""

    try:
        result = generate_summary(request.url)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc