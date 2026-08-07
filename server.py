import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ai_backend import generate_summary


# ==========================================================
# FastAPI App
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

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

    logger.info("Received summarize request for URL: %s", request.url)
    try:
        result = generate_summary(request.url)
        return result
    except RuntimeError as exc:
        logger.error("Summary request failed with client error: %s", str(exc))
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception:
        logger.exception("Unexpected server error during summarize request")
        raise HTTPException(status_code=500, detail="An unexpected server error occurred.")