import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp


# ==========================================================
# Load Environment Variables & Groq Client Helper
# ==========================================================

load_dotenv(Path(__file__).resolve().parent / ".env")


def get_config(key: str, default: str = None) -> str:
    """Read configuration from environment variable, falling back to Streamlit secrets."""
    val = os.getenv(key)
    if val:
        return val.strip().strip('"').strip("'")
    try:
        import streamlit as st

        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key]).strip().strip('"').strip("'")
    except Exception:
        pass
    return default


def get_groq_client():
    """Lazily instantiate and return the Groq client."""
    api_key = get_config("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not configured. Please set it in your environment variables or Streamlit secrets."
        )
    return Groq(api_key=api_key)


# ==========================================================
# Prompt Loader
# ==========================================================

def load_prompt():
    """Load the prompt template from the project directory."""

    prompt_path = Path(__file__).resolve().parent / "prompt.md"

    try:
        with prompt_path.open("r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as exc:
        raise RuntimeError("The prompt template file is missing.") from exc


# ==========================================================
# YouTube URL Utilities
# ==========================================================

def extract_video_id(url):
    """
    Extracts the 11-character YouTube Video ID.

    Supported URLs:
    https://www.youtube.com/watch?v=xxxx
    https://youtu.be/xxxx
    https://youtube.com/embed/xxxx
    """

    pattern = r"(?:v=|\/|embed\/|youtu\.be\/)([A-Za-z0-9_-]{11})"

    match = re.search(pattern, url)

    if match:
        return match.group(1)

    raise ValueError("Invalid YouTube URL.")


# ==========================================================
# Fetch Video Title
# ==========================================================

def get_video_title(url):
    """
    Fetches the title of a YouTube video using YouTube oEmbed (cloud-friendly)
    with yt-dlp fallback.
    """
    import requests

    # 1. Try official YouTube oEmbed (fast, lightweight, never blocked on cloud IPs)
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        resp = requests.get(oembed_url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if "title" in data and data["title"]:
                return data["title"]
    except Exception:
        pass

    # 2. Fallback to yt-dlp
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "extract_flat": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return info.get("title", "Unknown Title")
    except Exception:
        return "Unknown Title"


# ==========================================================
# Fetch Transcript (RapidAPI + youtube-transcript-api fallback)
# ==========================================================

_last_rapidapi_error = None


def _fetch_transcript_rapidapi(video_id):
    """Fetch transcript via RapidAPI to bypass cloud IP blocks."""
    global _last_rapidapi_error
    _last_rapidapi_error = None
    import requests

    rapidapi_key = get_config("RAPIDAPI_KEY")
    if not rapidapi_key:
        _last_rapidapi_error = "RAPIDAPI_KEY is not configured or empty in environment"
        return None

    rapidapi_host = get_config("RAPIDAPI_HOST", "youtube-2-transcript.p.rapidapi.com")

    headers = {
        "x-rapidapi-key": rapidapi_key,
        "x-rapidapi-host": rapidapi_host,
    }

    try:
        if "youtube-2-transcript" in rapidapi_host:
            rapidapi_url = f"https://{rapidapi_host}/transcript-with-url"
            params = {
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "flat_text": "true",
            }
        else:
            rapidapi_url = f"https://{rapidapi_host}/transcript"
            params = {"video_id": video_id}

        response = requests.get(rapidapi_url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()

            # Format 1: {"success": true, "transcript": "..." or [...]} (youtube-2-transcript)
            if isinstance(data, dict):
                if data.get("success") is False:
                    err_msg = data.get("error") or data.get("message") or "Transcript not available from RapidAPI."
                    _last_rapidapi_error = f"RapidAPI ({rapidapi_host}): {str(err_msg).strip()}"
                    return None

                if "transcript" in data:
                    t = data["transcript"]
                    if isinstance(t, str) and t.strip():
                        return t.strip()
                    if isinstance(t, list):
                        joined = " ".join(seg.get("text", "") for seg in t if isinstance(seg, dict))
                        if joined.strip():
                            return joined.strip()

            # Target dictionary (first item if list, or dictionary itself)
            item = data[0] if isinstance(data, list) and len(data) > 0 else (data if isinstance(data, dict) else None)

            if isinstance(item, dict):
                # Format 2: transcriptionAsText string directly
                as_text = item.get("transcriptionAsText")
                if isinstance(as_text, str) and as_text.strip():
                    return as_text.strip()

                # Format 3: iterate through transcription list and concatenate subtitles
                transcription_list = item.get("transcription")
                if isinstance(transcription_list, list):
                    subtitles = [
                        seg.get("subtitle") or seg.get("text")
                        for seg in transcription_list
                        if isinstance(seg, dict)
                    ]
                    joined = " ".join(s for s in subtitles if s and isinstance(s, str))
                    if joined.strip():
                        return joined.strip()

                if "text" in item and isinstance(item["text"], str) and item["text"].strip():
                    return item["text"].strip()

            _last_rapidapi_error = f"RapidAPI ({rapidapi_host}) returned 200 but transcript field was missing."
            return None

        elif response.status_code == 429:
            _last_rapidapi_error = "RapidAPI monthly quota exceeded (HTTP 429). Please verify your RapidAPI plan or refresh your RAPIDAPI_KEY."
            print(f"[WARN] RapidAPI quota exceeded (HTTP 429): {response.text[:200]}")
            return None
        elif response.status_code in (401, 403):
            _last_rapidapi_error = f"RapidAPI authentication failed (HTTP {response.status_code}) for host '{rapidapi_host}'. Response: {response.text[:200]}"
            print(f"[WARN] RapidAPI authentication failed (HTTP {response.status_code}): {response.text[:200]}")
            return None
        else:
            _last_rapidapi_error = f"RapidAPI ({rapidapi_host}) returned HTTP {response.status_code}: {response.text[:200]}"
            print(f"[WARN] RapidAPI returned HTTP {response.status_code}: {response.text[:200]}")
            return None
    except Exception as exc:
        _last_rapidapi_error = f"RapidAPI request failed ({type(exc).__name__}): {exc}"
        print(f"[WARN] RapidAPI request failed: {exc}")
        return None


def _fetch_transcript_local(video_id):
    """Fetch transcript using youtube-transcript-api (works on residential IPs)."""
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)

    try:
        transcript = transcript_list.find_transcript(["en"])
    except Exception:
        transcript = next(iter(transcript_list))

    fetched = transcript.fetch()
    return " ".join(snippet.text for snippet in fetched)


def get_transcript(video_id):
    """Fetch the best available transcript for the given video ID."""
    rapid_key = get_config("RAPIDAPI_KEY")

    # 1. Try RapidAPI if configured (recommended for cloud deployments)
    if rapid_key:
        rapid_text = _fetch_transcript_rapidapi(video_id)
        if rapid_text and rapid_text.strip():
            return rapid_text.strip()
    else:
        # Detect cloud deployment (Render, Heroku, Docker, etc.)
        if os.getenv("RENDER") or os.getenv("PORT"):
            raise RuntimeError(
                "RAPIDAPI_KEY is missing or empty in Render Environment variables. Cloud hosting requires RAPIDAPI_KEY because YouTube blocks direct cloud IP access."
            )

    # 2. Try youtube-transcript-api (residential local IPs)
    try:
        return _fetch_transcript_local(video_id)
    except Exception as exc:
        if _last_rapidapi_error:
            raise RuntimeError(_last_rapidapi_error) from exc

        message = str(exc).lower()
        if "private" in message or "unavailable" in message or "live" in message or "disabled" in message:
            raise RuntimeError(
                "This video is private, unavailable, or does not provide captions/transcripts."
            ) from exc

        raise RuntimeError(
            f"Unable to retrieve a transcript for this video: {exc}"
        ) from exc


# ==========================================================
# Build Prompt
# ==========================================================

def build_prompt(video_title, transcript):
    """
    Injects the transcript and video title into prompt.md.
    """
    prompt = load_prompt()
    prompt = prompt.replace("{{video_title}}", video_title)
    prompt = prompt.replace("{{transcript}}", transcript)
    return prompt


# ==========================================================
# Invoke Groq LLM
# ==========================================================

def invoke_llm(prompt):
    """Send the prompt to Groq and return the parsed JSON response."""
    client = get_groq_client()
    model = get_config("GROQ_MODEL", "openai/gpt-oss-120b")

    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        output = response.choices[0].message.content.strip()
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Groq returned an invalid response format.") from exc
    except Exception as exc:
        err_str = str(exc).lower()
        if "decommissioned" in err_str or "not exist" in err_str or "model_not_found" in err_str:
            raise RuntimeError(
                f"Configured Groq model '{model}' is unavailable or decommissioned. Set GROQ_MODEL in your .env to an active model (e.g. openai/gpt-oss-120b or openai/gpt-oss-20b)."
            ) from exc
        raise RuntimeError(f"Groq generation failed: {exc}") from exc


# ==========================================================
# Complete AI Pipeline
# ==========================================================

def generate_summary(url):
    """Run the full summarization workflow for a YouTube URL."""

    try:
        video_id = extract_video_id(url)
    except ValueError as exc:
        raise RuntimeError("Please provide a valid YouTube video URL.") from exc

    video_title = get_video_title(url)
    transcript = get_transcript(video_id)

    MAX_WORDS = 2500
    words = transcript.split()

    if len(words) > MAX_WORDS:
        transcript = " ".join(words[:MAX_WORDS])

    prompt = build_prompt(video_title, transcript)
    response = invoke_llm(prompt)

    response["video_title"] = video_title
    response["video_id"] = video_id

    return response


# ==========================================================
# Local Testing
# ==========================================================

if __name__ == "__main__":

    print("=" * 60)
    print(" AI YOUTUBE VIDEO SUMMARIZER ")
    print("=" * 60)

    url = input("\nEnter YouTube URL:\n\n")

    try:

        result = generate_summary(url)

        print("\n")
        print("=" * 60)
        print("SUMMARY")
        print("=" * 60)

        print(

            json.dumps(

                result,

                indent=4,

                ensure_ascii=False

            )

        )

    except Exception as e:

        print("\n")
        print("=" * 60)
        print("ERROR")
        print("=" * 60)

        print(e)