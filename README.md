# 🎥 AI YouTube Video Summarizer

An AI-powered web application that summarizes any YouTube video into clear, structured insights using Large Language Models (LLMs).

Simply paste a YouTube link and get an easy-to-read summary with key points, takeaways, keywords, and recommended next steps.

---

## ✨ Features

- 📺 Summarize any YouTube video
- 🤖 AI-generated summaries using Groq LLM
- 📝 Automatic transcript extraction
- ⭐ Key Points
- 💡 Takeaways
- 🏷️ Keywords
- 🎯 Target Audience
- 📊 Difficulty Level
- 🚀 Next Learning Steps
- 📥 Download summary as JSON or Markdown
- 🎨 Modern Streamlit interface

---

## 🛠️ Tech Stack

- Python
- FastAPI
- Streamlit
- Groq API
- yt-dlp
- YouTube Transcript API

---

## 📂 Project Structure

```text
youtube-video-summarizer/
│
├── screenshots/          # Images used in the README
├── ai_backend.py         # AI summarization pipeline
├── server.py             # FastAPI backend
├── ui.py                 # Streamlit frontend
├── prompt.md             # Prompt template for the LLM
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
├── .env                  # Environment variables (local only)
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd youtube-video-summarizer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the API Key

Create a `.env` file.

```text
GROQ_API_KEY=your_api_key_here
```

### 4. Start the Backend

```bash
uvicorn server:app --reload
```

### 5. Launch the Frontend

```bash
streamlit run ui.py
```

---

## 📷 Screenshots

### Home Page

> ![Home Page](image.png)

### Generated Summary

> ![Generated Summary](image-1.png)

---

## 🔄 How It Works

```
YouTube URL
      │
      ▼
Extract Video ID
      │
      ▼
Download Transcript
      │
      ▼
Build AI Prompt
      │
      ▼
Groq LLM
      │
      ▼
Structured Summary
      │
      ▼
Beautiful Streamlit UI
```

---

## 🎯 Future Improvements

- Support videos without transcripts
- Multiple language support
- Chat with YouTube videos
- PDF export
- User history
- Authentication

---

## 👨‍💻 Author

**Prashant**
**Suhana**

Built as part of the Samsung Innovation Campus GenAI Project.

