"""Home page for AgriSense AI."""

from __future__ import annotations

import html
import json

import streamlit as st
import streamlit.components.v1 as components

from utils.config import APP_SUBTITLE, APP_TITLE
from utils.loaders import load_crop_dataset, load_production_dataset

HERO_HEADING = f"{APP_TITLE} – {APP_SUBTITLE}"


def _build_hero_html(heading_text: str) -> str:
    """Return self-contained HTML/CSS/JS for the animated hero section."""
    safe_heading = html.escape(heading_text)
    heading_json = json.dumps(heading_text)

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; }}

  body {{
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: 'DM Sans', sans-serif;
  }}

  .hero-section {{
    background: linear-gradient(135deg, #0A1812 0%, #0D1F17 42%, #122820 100%);
    border: 1px solid rgba(46, 204, 113, 0.22);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    margin: 0;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.28), 0 0 0 1px rgba(46, 204, 113, 0.06);
    position: relative;
    overflow: hidden;
  }}

  .hero-section::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at 50% 0%, rgba(46, 204, 113, 0.14) 0%, transparent 62%);
    pointer-events: none;
  }}

  .hero-badge {{
    display: inline-block;
    background: rgba(46, 204, 113, 0.14);
    color: #7DEDAD;
    border: 1px solid rgba(46, 204, 113, 0.28);
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.85rem;
    position: relative;
    z-index: 1;
  }}

  .hero-title-wrap {{
    position: relative;
    z-index: 2;
    min-height: clamp(2.2rem, 5vw, 3.4rem);
    margin: 0 0 0.65rem 0;
  }}

  .hero-title {{
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 700;
    margin: 0;
    line-height: 1.15;
    letter-spacing: -0.02em;
    position: relative;
    display: inline-block;
    max-width: 100%;
    transition: filter 0.35s ease, transform 0.35s ease;
  }}

  .hero-title-text {{
    background: linear-gradient(92deg, #3DFF9A 0%, #2ECC71 38%, #56F09A 72%, #1BDB6F 100%);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: #2ECC71;
    text-shadow: none;
    filter: drop-shadow(0 0 18px rgba(46, 204, 113, 0.35));
  }}

  .hero-title.hero-title--glow {{
    filter: drop-shadow(0 0 22px rgba(61, 255, 154, 0.55));
    transform: scale(1.012);
  }}

  .hero-title.hero-title--glow .hero-title-text {{
    filter: drop-shadow(0 0 28px rgba(61, 255, 154, 0.65));
  }}

  .hero-cursor {{
    display: inline-block;
    color: #3DFF9A;
    font-weight: 400;
    margin-left: 1px;
    -webkit-text-fill-color: #3DFF9A;
    animation: hero-cursor-blink 0.72s step-end infinite;
    text-shadow: 0 0 10px rgba(61, 255, 154, 0.75);
  }}

  .hero-cursor.is-hidden {{
    opacity: 0;
    animation: none;
  }}

  @keyframes hero-cursor-blink {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0; }}
  }}

  .hero-click-pointer {{
    position: absolute;
    width: 22px;
    height: 22px;
    opacity: 0;
    pointer-events: none;
    z-index: 5;
    transition: opacity 0.28s ease, left 0.62s cubic-bezier(0.22, 1, 0.36, 1),
                top 0.62s cubic-bezier(0.22, 1, 0.36, 1), transform 0.14s ease;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.45));
  }}

  .hero-click-pointer.is-visible {{
    opacity: 1;
  }}

  .hero-click-pointer.is-clicking {{
    transform: scale(0.82);
  }}

  .hero-click-pointer svg {{
    display: block;
    width: 100%;
    height: 100%;
  }}

  .hero-subtitle {{
    font-size: clamp(1rem, 2vw, 1.15rem);
    color: #A8C4B4;
    margin: 0;
    max-width: 720px;
    line-height: 1.55;
    position: relative;
    z-index: 1;
  }}

  @media (max-width: 768px) {{
    .hero-section {{
      padding: 1.5rem 1.25rem;
    }}
  }}

  @media (prefers-reduced-motion: reduce) {{
    .hero-cursor {{ animation: none; opacity: 1; }}
    .hero-click-pointer {{ display: none; }}
  }}
</style>
</head>
<body>
  <div class="hero-section">
    <div class="hero-badge">AI-Powered Agriculture Intelligence</div>
    <div class="hero-title-wrap" id="hero-title-wrap">
      <h1 class="hero-title" id="hero-title" aria-label="{safe_heading}">
        <span class="hero-title-text" id="hero-typed-text"></span><span class="hero-cursor" id="hero-cursor" aria-hidden="true">|</span>
      </h1>
      <div class="hero-click-pointer" id="hero-click-pointer" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M5.5 3.5L18.5 11.2L12.4 12.4L10.8 18.5L5.5 3.5Z" fill="#FFFFFF" stroke="#1A2E22" stroke-width="1.2" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>
    <p class="hero-subtitle">
      Make data-driven farming decisions with machine learning crop recommendations,
      production estimation, and fertilizer guidance — all in one modern dashboard.
    </p>
  </div>

<script>
(function () {{
  const FULL_TEXT = {heading_json};
  const TYPING_DURATION_MS = 2600;
  const POST_TYPE_PAUSE_MS = 700;
  const POINTER_TRAVEL_MS = 620;
  const CLICK_HOLD_MS = 420;

  const typedEl = document.getElementById("hero-typed-text");
  const cursorEl = document.getElementById("hero-cursor");
  const titleEl = document.getElementById("hero-title");
  const wrapEl = document.getElementById("hero-title-wrap");
  const pointerEl = document.getElementById("hero-click-pointer");

  if (!typedEl || !cursorEl || !titleEl || !wrapEl || !pointerEl) {{
    return;
  }}

  let index = 0;
  let timers = [];
  let hasStarted = false;

  function schedule(fn, delay) {{
    const id = window.setTimeout(fn, delay);
    timers.push(id);
    return id;
  }}

  function clearAllTimers() {{
    timers.forEach((id) => window.clearTimeout(id));
    timers = [];
  }}

  function prefersReducedMotion() {{
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }}

  function showFinalState() {{
    typedEl.textContent = FULL_TEXT;
    cursorEl.classList.add("is-hidden");
    pointerEl.classList.remove("is-visible", "is-clicking");
    titleEl.classList.remove("hero-title--glow");
  }}

  function runClickAnimation() {{
    const wrapRect = wrapEl.getBoundingClientRect();
    const titleRect = titleEl.getBoundingClientRect();

    const endX = titleRect.left - wrapRect.left + titleRect.width * 0.52;
    const endY = titleRect.top - wrapRect.top + titleRect.height * 0.62;
    const startX = Math.min(endX + 72, wrapRect.width - 24);
    const startY = endY + 28;

    pointerEl.style.left = startX + "px";
    pointerEl.style.top = startY + "px";
    pointerEl.classList.add("is-visible");

    requestAnimationFrame(function () {{
      pointerEl.style.left = endX + "px";
      pointerEl.style.top = endY + "px";
    }});

    schedule(function () {{
      pointerEl.classList.add("is-clicking");
      titleEl.classList.add("hero-title--glow");
      cursorEl.classList.add("is-hidden");
    }}, POINTER_TRAVEL_MS);

    schedule(function () {{
      pointerEl.classList.remove("is-visible", "is-clicking");
      titleEl.classList.remove("hero-title--glow");
    }}, POINTER_TRAVEL_MS + CLICK_HOLD_MS);
  }}

  function startTyping() {{
    if (hasStarted) {{
      return;
    }}
    hasStarted = true;

    if (prefersReducedMotion()) {{
      showFinalState();
      return;
    }}

    const charDelay = Math.max(28, Math.round(TYPING_DURATION_MS / FULL_TEXT.length));

    function typeNext() {{
      if (index < FULL_TEXT.length) {{
        typedEl.textContent += FULL_TEXT.charAt(index);
        index += 1;
        schedule(typeNext, charDelay);
      }} else {{
        schedule(runClickAnimation, POST_TYPE_PAUSE_MS);
      }}
    }}

    typeNext();
  }}

  startTyping();

  window.addEventListener("beforeunload", clearAllTimers);
}})();
</script>
</body>
</html>
"""


def _render_hero_section() -> None:
    """Render the animated hero heading inside a lightweight Streamlit component."""
    components.html(
        _build_hero_html(HERO_HEADING),
        height=340,
        scrolling=False,
    )


def render_home() -> None:
    """Render the landing page with hero section and overview cards."""
    _render_hero_section()

    crop_df = load_crop_dataset()
    production_df = load_production_dataset()

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        (col1, "Crop Classes", f"{crop_df['label'].nunique()}", "Supported recommendation targets"),
        (col2, "Crop Records", f"{len(crop_df):,}", "Environmental training samples"),
        (col3, "Production Records", f"{len(production_df):,}", "District-wise yield entries"),
        (col4, "States Covered", f"{production_df['State_Name'].nunique()}", "Pan-India coverage"),
    ]
    for column, title, value, subtitle in metrics:
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>{title}</h3>
                    <p class="metric-value">{value}</p>
                    <p>{subtitle}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Platform Capabilities")

    features = [
        (
            "Crop Recommendation",
            "Predict the best crop for your soil and climate using a trained CatBoost classifier.",
        ),
        (
            "Production Estimation",
            "Estimate expected crop production from historical patterns with an XGBoost model.",
        ),
        (
            "Fertilizer Guidance",
            "Get NPK and pH recommendations from a curated fertilizer lookup dataset.",
        ),
    ]

    row1_col1, row1_col2, row1_col3 = st.columns(3)
    for column, (title, description) in zip([row1_col1, row1_col2, row1_col3], features):
        with column:
            st.markdown(
                f"""
                <div class="feature-card">
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.info(
        "Use the sidebar to navigate between modules. All predictions use pre-trained "
        "models — no retraining occurs at runtime."
    )
