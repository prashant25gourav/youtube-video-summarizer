import json
import os
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from ai_backend import extract_video_id, generate_summary


# ==========================================================
# Streamlit Configuration
# ==========================================================

st.set_page_config(
    page_title="AI YouTube Video Summarizer",
    page_icon="▶️",
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
        background: linear-gradient(135deg, #0f172a 0%, #CC0000 45%, #FF0000 100%);
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
        background: rgba(255, 245, 245, 0.18);
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
        border-color: rgba(255, 0, 0, 0.35);
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
        color: #FF0000;
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
        border-color: rgba(255, 0, 0, 0.35);
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
        background: linear-gradient(135deg, #CC0000, #FF0000);
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
        padding: 0.52rem 0.95rem;
        border-radius: 999px;
        font-size: 0.88rem;
        font-weight: 600;
        color: #f8fafc;
        background: rgba(30, 41, 59, 0.85);
        border: 1px solid rgba(239, 68, 68, 0.4);
        box-shadow: 0 4px 14px rgba(2, 6, 23, 0.25);
        transition: transform 200ms ease, background 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
    }

    .chip:hover {
        transform: translateY(-1px);
        background: rgba(51, 65, 85, 0.95);
        border-color: rgba(239, 68, 68, 0.7);
        color: #ffffff;
        box-shadow: 0 6px 18px rgba(239, 68, 68, 0.2);
    }

    .takeaway-card {
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-left: 5px solid #FF0000;
        border-radius: 18px;
        padding: 1rem 1.05rem;
        margin-top: 0.8rem;
        box-shadow: 0 14px 34px rgba(2, 6, 23, 0.16);
        transition: transform 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
    }

    .takeaway-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 0, 0, 0.35);
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
        border-color: rgba(255, 0, 0, 0.35);
        box-shadow: 0 18px 40px rgba(2, 6, 23, 0.2);
    }

    .timeline-step {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #CC0000, #FF0000);
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

    .input-card div.stButton > button {
        width: min(430px, 100%);
        height: 56px;
        padding: 0 1.2rem;
        border: none;
        border-radius: 16px;
        font-size: 0.98rem;
        font-weight: 700;
        background: linear-gradient(135deg, #CC0000, #FF0000);
        color: white;
        box-shadow: 0 16px 28px rgba(255, 0, 0, 0.24);
        transition: transform 200ms ease, box-shadow 200ms ease, filter 200ms ease;
        cursor: pointer;
        display: block;
        margin: 0 auto;
    }

    .input-card div.stButton > button:hover {
        transform: translateY(-1px) scale(1.01);
        box-shadow: 0 18px 34px rgba(230, 0, 0, 0.32);
        filter: brightness(1.03);
    }

    div.stDownloadButton > button {
        width: 100%;
        height: 44px;
        min-height: 44px;
        padding: 0 1rem;
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        background: rgba(15, 23, 42, 0.85);
        color: #f1f5f9;
        border: 1px solid rgba(148, 163, 184, 0.24);
        box-shadow: 0 4px 14px rgba(2, 6, 23, 0.25);
        transition: transform 200ms ease, background 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-sizing: border-box;
    }

    div.stDownloadButton > button:hover {
        background: rgba(30, 41, 59, 0.95);
        border-color: rgba(239, 68, 68, 0.5);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(239, 68, 68, 0.18);
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
        border-color: rgba(255, 0, 0, 0.45);
        box-shadow: 0 0 0 3px rgba(255, 0, 0, 0.1);
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


def render_copy_button(text_to_copy: str):
    escaped_json = json.dumps(text_to_copy)
    comp_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: transparent; overflow: hidden; }}
      .copy-btn {{
        width: 100%;
        height: 44px;
        background: rgba(15, 23, 42, 0.85);
        color: #f1f5f9;
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 12px;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.45rem;
        transition: transform 200ms ease, background 200ms ease, border-color 200ms ease, box-shadow 200ms ease;
      }}
      .copy-btn:hover {{
        background: rgba(30, 41, 59, 0.95);
        border-color: rgba(239, 68, 68, 0.5);
        color: #ffffff;
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(239, 68, 68, 0.18);
      }}
      .copy-btn.copied {{
        background: rgba(6, 78, 59, 0.9);
        border-color: #10b981;
        color: #ecfdf5;
      }}
    </style>
    </head>
    <body>
      <button id="copy-btn" class="copy-btn" onclick="copy()">
        <span id="btn-icon">📋</span> <span id="btn-text">Copy Summary</span>
      </button>
      <script>
        const text = {escaped_json};
        function copy() {{
          const btn = document.getElementById('copy-btn');
          const btnIcon = document.getElementById('btn-icon');
          const btnText = document.getElementById('btn-text');
          
          function showSuccess() {{
            btn.classList.add('copied');
            btnIcon.innerText = '✓';
            btnText.innerText = 'Copied!';
            setTimeout(() => {{
              btn.classList.remove('copied');
              btnIcon.innerText = '📋';
              btnText.innerText = 'Copy Summary';
            }}, 2000);
          }}

          if (navigator.clipboard && window.isSecureContext) {{
            navigator.clipboard.writeText(text).then(showSuccess).catch(() => {{
              fallbackCopy();
            }});
          }} else {{
            fallbackCopy();
          }}

          function fallbackCopy() {{
            try {{
              const ta = document.createElement('textarea');
              ta.value = text;
              ta.style.position = 'fixed';
              ta.style.opacity = '0';
              document.body.appendChild(ta);
              ta.focus();
              ta.select();
              document.execCommand('copy');
              document.body.removeChild(ta);
              showSuccess();
            }} catch(e) {{
              btnText.innerText = 'Error copying';
            }}
          }}
        }}
      </script>
    </body>
    </html>
    """
    if hasattr(st, "iframe"):
        st.iframe(comp_html, height=44)
    else:
        components.html(comp_html, height=44)


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


@st.cache_data(ttl=86400, show_spinner=False)
def get_cached_summary(video_id: str, _url: str) -> dict:
    """
    Generate and cache video summary for 24 hours keyed by video ID.
    Prevents repeat videos from consuming API quota.
    """
    return generate_summary(_url)


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
        render_copy_button(summary_text)

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
        <h1 class="hero-title">🎥 AI YouTube Video Summarizer</h1>
        <p class="hero-subtitle">Summarize any YouTube video instantly using Groq LLM and turn long content into concise, polished insights with structured takeaways and next steps.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='input-card'>", unsafe_allow_html=True)
st.markdown("<div class='section-title'>Paste a YouTube URL</div>", unsafe_allow_html=True)
youtube_url = st.text_input(
    "YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

center_col = st.columns([1, 1, 1])[1]
with center_col:
    generate = st.button("Generate Summary", use_container_width=True)

st.markdown("<div class='pill-caption'>The app will read the transcript, build a tailored prompt and return a premium summary experience.</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

if generate:
    clean_url = youtube_url.strip()
    if not clean_url:
        render_error("Please enter a YouTube URL before generating a summary.")
    else:
        try:
            video_id = extract_video_id(clean_url)
        except ValueError:
            render_error(
                "Please enter a valid YouTube video URL (e.g., https://www.youtube.com/watch?v=... or https://youtu.be/...)."
            )
            st.stop()

        with st.status("🎥 Processing Video...", expanded=True) as status:
            try:
                status.update(label="🤖 Generating AI Summary...", state="running")
                st.write("Extracting transcript and generating structured summary with Groq...")

                result = get_cached_summary(video_id, _url=clean_url)
                st.session_state.summary_result = result

                status.update(label="✅ Summary Ready", state="complete")
                st.write("Summary generated successfully!")

            except RuntimeError as exc:
                status.update(label="Generation failed", state="error")
                msg = str(exc)
                msg_lower = msg.lower()

                if "429" in msg_lower or "quota" in msg_lower or "rate limit" in msg_lower:
                    render_error(
                        "API rate limit or monthly quota exceeded (HTTP 429). Please wait a few moments or check your API key quota."
                    )
                elif "private" in msg_lower or "unavailable" in msg_lower or "live" in msg_lower or "captions" in msg_lower or "transcript" in msg_lower:
                    render_error(
                        "Unable to retrieve a transcript for this video. The video may be private, live, or have closed captions disabled by the creator."
                    )
                elif "groq_api_key" in msg_lower or "not configured" in msg_lower or "auth_failed" in msg_lower or "401" in msg_lower or "403" in msg_lower:
                    render_error(
                        "API key is not configured or authentication failed. Please set GROQ_API_KEY in your environment or Streamlit secrets."
                    )
                elif "decommissioned" in msg_lower or "model" in msg_lower:
                    render_error(
                        "The configured Groq model is unavailable. Please check the GROQ_MODEL setting."
                    )
                else:
                    render_error(msg)

                st.session_state.summary_result = None
                st.stop()

            except Exception as exc:
                status.update(label="Generation failed", state="error")
                render_error(f"An unexpected error occurred while generating the summary: {exc}")
                st.session_state.summary_result = None
                st.stop()

if st.session_state.summary_result:
    render_results(st.session_state.summary_result)

st.markdown(
    """
    <div class="footer-note">
        ────────────────────────<br>
        
        Groq • Streamlit
       
    </div>
    """,
    unsafe_allow_html=True,
)
