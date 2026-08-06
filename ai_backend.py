import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp


# ==========================================================
# Load Environment Variables
# ==========================================================

load_dotenv(Path(__file__).resolve().parent / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


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
    Fetches the title of a YouTube video.
    """

    try:

        ydl_opts = {

            "quiet": True,

            "skip_download": True,

            "extract_flat": True,

            "no_warnings": True

        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

        return info.get(
            "title",
            "Unknown Title"
        )

    except Exception:

        return "Unknown Title"

# ==========================================================
# Fetch Transcript
# ==========================================================

def get_transcript(video_id):
    """Fetch the best available transcript for the given video ID."""

    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        try:
            transcript = transcript_list.find_transcript(["en"])
        except Exception:
            transcript = next(iter(transcript_list))

        fetched = transcript.fetch()
        return " ".join(snippet.text for snippet in fetched)
    except Exception as exc:
        message = str(exc).lower()
        if "private" in message or "unavailable" in message or "live" in message or "disabled" in message:
            raise RuntimeError(
                "This video is private, unavailable, or does not provide captions/transcripts."
            ) from exc
        raise RuntimeError(
            "Unable to retrieve a transcript for this video. The video may be private, live, or missing captions."
        ) from exc

# ==========================================================
# Build Prompt
# ==========================================================

def build_prompt(video_title, transcript):
    """
    Injects the transcript and video title
    into prompt.md.
    """

    prompt = load_prompt()

    prompt = prompt.replace(
        "{{video_title}}",
        video_title
    )

    prompt = prompt.replace(
        "{{transcript}}",
        transcript
    )

    return prompt


# ==========================================================
# Invoke Groq LLM
# ==========================================================

def invoke_llm(prompt):
    """Send the prompt to Groq and return the parsed JSON response."""

    if client is None:
        raise RuntimeError("GROQ_API_KEY is not configured. Add it to your environment before running the app.")

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
        output = response.choices[0].message.content.strip()
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Groq returned an invalid response format.") from exc
    except Exception as exc:
        raise RuntimeError("Groq could not generate a summary right now. Please try again shortly.") from exc

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