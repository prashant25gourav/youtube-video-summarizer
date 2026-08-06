import json
from html import escape

import requests
import streamlit as st


# ==========================================================
# Streamlit Configuration
# ==========================================================

st.set_page_config(
    page_title="AI YouTube Video Summarizer",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ==========================================================
# Session State
# ==========================================================

if "summary_result" not in st.session_state:
    st.session_state.summary_result = None

if "copy_feedback" not in st.session_state:
    st.session_state.copy_feedback = ""


# ==========================================================
# Custom CSS
# ==========================================================

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: #060816;
        color: #f8fafc;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .hero-shell {
        position: relative;
        overflow: hidden;
        padding: 1.35rem 1.6rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 45%, #7c3aed 100%);
        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.3);
        margin-bottom: 0.85rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }

    .hero-shell::after {
        content: "";
        position: absolute;
        inset: -20% auto auto 64%;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(255,255,255,0.22), transparent 68%);
        filter: blur(6px);
    }

    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 0.7rem;
        background: rgba(255, 255, 255, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        backdrop-filter: blur(10px);
        margin-bottom: 0.7rem;
    }

    .hero-title {
        font-size: clamp(1.75rem, 2.3vw, 2.55rem);
        font-weight: 800;
        margin: 0 0 0.35rem 0;
        line-height: 1.12;
    }

    .hero-subtitle {
        font-size: 1rem;
        max-width: 760px;
        color: rgba(248, 250, 252, 0.9);
        margin: 0;
        line-height: 1.65;
    }

    .input-card {
        background: rgba(6, 10, 24, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 22px;
        padding: 1rem 1.1rem 1.15rem;
        box-shadow: 0 16px 36px rgba(2, 6, 23, 0.22);
        margin-bottom: 1.2rem;
        backdrop-filter: blur(16px);
    }

    .section-title {
        font-size: 1.08rem;
        font-weight: 800;
        color: #e2e8f0;
        margin-top: 0.25rem;
        margin-bottom: 0.7rem;
        letter-spacing: 0.01em;
    }

    .pill-caption {
        font-size: 0.82rem;
        color: #94a3b8;
        margin-top: 0.45rem;
    }

    .card-surface {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.94), rgba(9, 13, 30, 0.96));
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        box-shadow: 0 16px 40px rgba(2, 6, 23, 0.2);
        transition: transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease;
    }

    .card-surface:hover {
        transform: translateY(-2px);
        box-shadow: 0 22px 48px rgba(2, 6, 23, 0.26);
        border-color: rgba(96, 165, 250, 0.35);
    }

    .media-card img {
        width: 100%;
        border-radius: 18px;
        box-shadow: 0 16px 38px rgba(15, 23, 42, 0.3);
        display: block;
        object-fit: cover;
    }

    .video-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        line-height: 1.2;
        color: #f8fafc;
        display: flex;
        align-items: center;
        min-height: 72px;
        padding-right: 0.25rem;
    }

    .video-info-card {
        display: flex;
        flex-direction: column;
        justify-content: center;
        height: 100%;
    }

    .info-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.9rem;
        margin-top: 0.75rem;
    }

    .info-card {
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 0.35rem;
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        min-height: 124px;
        height: 100%;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    .info-label {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #7dd3fc;
    }

    .info-value {
        font-size: 1rem;
        line-height: 1.6;
        color: #f8fafc;
        overflow-wrap: anywhere;
        white-space: normal;
        flex: 1;
    }

    .stat-row {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 0.95rem 0 1.15rem;
    }

    .stat-card {
        background: rgba(9, 13, 30, 0.82);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 16px;
        padding: 0.8rem 0.85rem;
        box-shadow: 0 12px 28px rgba(2, 6, 23, 0.14);
        min-height: 88px;
    }

    .stat-label {
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94a3b8;
        margin-bottom: 0.35rem;
    }

    .stat-value {
        font-size: 0.96rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.4;
        overflow-wrap: anywhere;
    }

    .summary-card {
        max-width: 980px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(9, 13, 30, 0.97));
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 22px;
        padding: 1.2rem 1.35rem;
        box-shadow: 0 20px 46px rgba(2, 6, 23, 0.22);
        margin-top: 0.75rem;
    }

    .summary-card p {
        margin: 0 0 0.9rem 0;
        font-size: 1rem;
        line-height: 1.95;
        color: #e2e8f0;
    }

    .summary-card p:last-child {
        margin-bottom: 0;
    }

    .point-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.9rem;
        margin-top: 0.8rem;
    }

    .point-card {
        display: flex;
        gap: 0.75rem;
        align-items: flex-start;
        background: rgba(15, 23, 42, 0.84);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        min-height: 132px;
        box-shadow: 0 14px 34px rgba(2, 6, 23, 0.18);
        transition: transform 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
    }

    .point-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.35);
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.22);
    }

    .point-icon {
        flex-shrink: 0;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px;
        height: 34px;
        border-radius: 999px;
        background: linear-gradient(135deg, #38bdf8, #818cf8);
        color: white;
        font-size: 1rem;
        font-weight: 700;
        margin-top: 0.06rem;
    }

    .point-text {
        font-size: 0.96rem;
        line-height: 1.65;
        color: #e2e8f0;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 0.8rem;
    }

    .chip {
        display: inline-flex;
        align-items: center;
        padding: 0.62rem 0.92rem;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #f8fafc;
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.32), rgba(129, 140, 248, 0.3));
        border: 1px solid rgba(125, 211, 252, 0.26);
        box-shadow: 0 10px 20px rgba(56, 189, 248, 0.12);
        transition: transform 200ms ease, background 200ms ease, box-shadow 200ms ease;
    }

    .chip:hover {
        transform: translateY(-1px);
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.38), rgba(129, 140, 248, 0.35));
        box-shadow: 0 12px 24px rgba(56, 189, 248, 0.18);
    }

    .takeaway-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-left: 5px solid #38bdf8;
        border-radius: 18px;
        padding: 1rem 1.05rem;
        margin-top: 0.8rem;
        box-shadow: 0 14px 34px rgba(2, 6, 23, 0.16);
        transition: transform 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
    }

    .takeaway-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.35);
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.2);
    }

    .timeline-stack {
        display: grid;
        gap: 0.9rem;
        margin-top: 0.8rem;
    }

    .timeline-card {
        display: grid;
        grid-template-columns: 48px 1fr;
        gap: 0.9rem;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        box-shadow: 0 14px 34px rgba(2, 6, 23, 0.16);
        transition: transform 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
    }

    .timeline-card:hover {
        transform: translateY(-2px);
        border-color: rgba(96, 165, 250, 0.35);
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.2);
    }

    .timeline-step {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        color: white;
        font-weight: 700;
        font-size: 0.95rem;
    }

    .timeline-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: #f8fafc;
        margin-bottom: 0.28rem;
    }

    .timeline-text {
        font-size: 0.94rem;
        line-height: 1.6;
        color: #cbd5e1;
    }

    .error-card {
        margin-top: 1rem;
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.95), rgba(153, 27, 27, 0.95));
        border: 1px solid rgba(248, 113, 113, 0.28);
        color: #fee2e2;
        box-shadow: 0 16px 38px rgba(127, 29, 29, 0.24);
    }

    div.stButton > button {
        width: min(430px, 100%);
        height: 56px;
        padding: 0 1.2rem;
        border: none;
        border-radius: 16px;
        font-size: 0.98rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        box-shadow: 0 16px 28px rgba(37, 99, 235, 0.24);
        transition: transform 200ms ease, box-shadow 200ms ease, filter 200ms ease;
        cursor: pointer;
        display: block;
        margin: 0 auto;
    }

    div.stButton > button:hover {
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 18px 34px rgba(37, 99, 235, 0.32);
        filter: brightness(1.03);
    }

    .stTextInput > div > div > input {
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        color: white;
        padding: 0.8rem 0.95rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
    }

    .stTextInput > div > div > input:focus {
        border-color: rgba(96, 165, 250, 0.45);
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.1);
    }

    .footer-note {
        margin-top: 2.2rem;
        text-align: center;
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.8;
        letter-spacing: 0.01em;
    }

    .export-heading {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 0.2rem 0 0.25rem;
    }

    .export-subtitle {
        font-size: 0.82rem;
        color: #94a3b8;
        margin: 0 0 0.9rem;
    }

    @media (max-width: 1100px) {
        .stat-row {
            grid-template-columns: repeat(3, minmax(0, 1fr));
        }
    }

    @media (max-width: 980px) {
        .result-shell {
            grid-template-columns: 1fr;
        }

        .point-grid {
            grid-template-columns: 1fr;
        }

        .info-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media (max-width: 720px) {
        .hero-shell {
            padding: 1.4rem 1.1rem;
        }

        .stat-row {
            grid-template-columns: 1fr;
        }

        .info-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# Helpers
# ==========================================================


def build_markdown(result):
    lines = []
    lines.append("# AI YouTube Video Summary")
    lines.append("")
    lines.append(f"- Video Title: {result.get('video_title', 'Unknown Title')}")
    lines.append(f"- Difficulty: {result.get('difficulty', 'Unknown')}")
    lines.append(f"- Audience: {result.get('target_audience', 'Not specified')}")
    lines.append(f"- Video ID: {result.get('video_id', 'Unknown')}")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(result.get("summary", ""))
    lines.append("")
    lines.append("## Key Points")
    for point in result.get("key_points", []):
        lines.append(f"- {point}")
    lines.append("")
    lines.append("## Takeaways")
    for takeaway in result.get("takeaways", []):
        lines.append(f"- {takeaway}")
    lines.append("")
    lines.append("## Keywords")
    lines.append(", ".join(result.get("keywords", [])))
    lines.append("")
    lines.append("## Next Steps")
    for index, step in enumerate(result.get("next_steps", []), start=1):
        lines.append(f"{index}. {step}")
    return "\n".join(lines)


def render_error(message):
    """Render a clean, user-friendly error message in the UI."""

    st.markdown(
        f"""
        <div class="error-card">
            <div style="font-weight:700; margin-bottom:0.25rem;">Something went wrong</div>
            <div>{escape(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_metadata_stat(result):
    return ("Video ID", result.get("video_id", "Unknown"))


def render_results(result):
    thumbnail = (
        f"https://img.youtube.com/vi/{result.get('video_id', '')}/maxresdefault.jpg"
    )
    _, metadata_value = get_metadata_stat(result)

    st.markdown("<div class='section-title'>Video Insights</div>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.02, 1.2], gap="large")

    with left_col:
        st.markdown(
            f"""
            <div class="card-surface media-card">
                <img src="{thumbnail}" alt="Video thumbnail" />
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown(
            f"""
            <div class="card-surface video-info-card">
                <div class="video-title">{escape(result.get('video_title', 'Untitled Video'))}</div>
                <div class="info-grid">
                    <div class="info-card">
                        <div class="info-label">Difficulty</div>
                        <div class="info-value">{escape(result.get('difficulty', 'Unknown'))}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Audience</div>
                        <div class="info-value">{escape(result.get('target_audience', 'Not specified'))}</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">Video ID</div>
                        <div class="info-value">{escape(metadata_value)}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>AI Summary</div>", unsafe_allow_html=True)

    summary_text = escape(result.get("summary", ""))
    summary_html = summary_text.replace("\n\n", "</p><p>").replace("\n", "<br>")
    st.markdown(
        f"""
        <div class="summary-card">
            <p>{summary_html}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 1.0rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='export-heading'>Export Summary</div>", unsafe_allow_html=True)
    st.markdown("<div class='export-subtitle'>Download or copy the generated summary.</div>", unsafe_allow_html=True)

    action_cols = st.columns([1, 1, 1], gap="small")
    with action_cols[0]:
        st.download_button(
            label="Download JSON",
            data=json.dumps(result, indent=2, ensure_ascii=False),
            file_name="summary.json",
            mime="application/json",
            use_container_width=True,
        )
    with action_cols[1]:
        st.download_button(
            label="Download Markdown",
            data=build_markdown(result),
            file_name="summary.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with action_cols[2]:
        if st.button("Copy Summary", use_container_width=True):
            st.session_state.copy_feedback = "Summary is ready to copy from the generated output."

    if st.session_state.copy_feedback:
        st.caption(st.session_state.copy_feedback)

    st.markdown("<div style='margin-top: 1.3rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Key Points</div>", unsafe_allow_html=True)

    points_html = ""
    for point in result.get("key_points", []):
        safe_point = escape(point)
        points_html += (
            f"<div class='point-card'><div class='point-icon'>✓</div><div class='point-text'>{safe_point}</div></div>"
        )

    st.markdown(
        f"<div class='point-grid'>{points_html}</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='margin-top: 1.3rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Keywords</div>", unsafe_allow_html=True)

    chips_html = "".join(
        f"<span class='chip'>{escape(keyword)}</span>" for keyword in result.get("keywords", [])
    )
    st.markdown(f"<div class='chip-row'>{chips_html}</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 1.3rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Takeaways</div>", unsafe_allow_html=True)

    for takeaway in result.get("takeaways", []):
        st.markdown(
            f"""
            <div class='takeaway-card'>
                <div style='display:flex; gap:0.55rem; align-items:flex-start;'>
                    <div style='font-size:1rem;'>💡</div>
                    <div style='color:#e2e8f0; line-height:1.7;'>{escape(takeaway)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='margin-top: 1.3rem;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Next Steps</div>", unsafe_allow_html=True)

    timeline_html = ""
    for index, step in enumerate(result.get("next_steps", []), start=1):
        timeline_html += (
            f"<div class='timeline-card'>"
            f"<div class='timeline-step'>{index}</div>"
            f"<div><div class='timeline-title'>Step {index}</div><div class='timeline-text'>{escape(step)}</div></div>"
            f"</div>"
        )

    st.markdown(f"<div class='timeline-stack'>{timeline_html}</div>", unsafe_allow_html=True)


# ==========================================================
# UI Structure
# ==========================================================

st.markdown(
    """
    <div class="hero-shell">
        <div class="hero-pill">⚡ Premium AI Workspace</div>
        <h1 class="hero-title">🎥 AI YouTube Video Summarizer</h1>
        <p class="hero-subtitle">Summarize any YouTube video instantly using Groq LLM and turn long content into concise, polished insights with structured takeaways and next steps.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='input-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Paste a YouTube URL</div>", unsafe_allow_html=True)
youtube_url = st.text_input(
    "",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

center_col = st.columns([1, 1, 1])[1]
with center_col:
    generate = st.button("Generate Summary", use_container_width=True)

st.markdown("<div class='pill-caption'>The app will read the transcript, build a tailored prompt and return a premium summary experience.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if generate:
    if not youtube_url.strip():
        render_error("Please enter a YouTube URL before generating a summary.")
    else:
        with st.status("🎥 Reading Transcript", expanded=True) as status:
            st.write("Reading transcript...")
            try:
                status.update(label="🧠 Building Prompt", state="running")
                st.write("Building prompt...")
                response = requests.post(
                    "http://127.0.0.1:8000/summarize",
                    json={"url": youtube_url},
                    timeout=300,
                )

                if response.status_code != 200:
                    status.update(label="Generation failed", state="error")
                    detail = response.json().get("detail", "The backend returned an error.")
                    render_error(detail)
                    st.session_state.summary_result = None
                    st.stop()

                status.update(label="🤖 Generating Summary", state="running")
                st.write("Generating summary...")
                result = response.json()
                st.session_state.summary_result = result
                status.update(label="📋 Formatting Output", state="running")
                st.write("Formatting output...")
                status.update(label="✅ Finished", state="complete")

            except requests.exceptions.ConnectionError:
                status.update(label="Connection error", state="error")
                render_error(
                    "The backend is currently unavailable. Please start the FastAPI server before generating a summary."
                )
                st.session_state.summary_result = None
                st.stop()

            except Exception as exc:
                status.update(label="Generation failed", state="error")
                render_error(str(exc))
                st.session_state.summary_result = None
                st.stop()

if st.session_state.summary_result:
    render_results(st.session_state.summary_result)

st.markdown(
    """
    <div class="footer-note">
        ────────────────────────<br>
        
        Groq • FastAPI • Streamlit
       
    </div>
    """,
    unsafe_allow_html=True,
)
