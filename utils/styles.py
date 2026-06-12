"""Global CSS theme for the AgriSense AI Streamlit application."""

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&display=swap');

:root {
    --primary: #1B7F4B;
    --primary-dark: #145C37;
    --primary-light: #E8F5EE;
    --accent: #2ECC71;
    --surface: #FFFFFF;
    --surface-muted: #F7FAF8;
    --text: #1A2E22;
    --text-muted: #5C7366;
    --border: #D8E8DE;
    --shadow: 0 8px 30px rgba(27, 127, 75, 0.08);
    --radius: 16px;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header[data-testid="stHeader"] {
    visibility: hidden;
    height: 0;
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #145C37 0%, #1B7F4B 55%, #218F58 100%);
    border-right: none;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] .stRadio > label {
    display: none;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 12px;
    padding: 0.65rem 0.85rem;
    margin-bottom: 0.45rem;
    transition: all 0.2s ease;
    font-weight: 500;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
    background: rgba(255, 255, 255, 0.16);
    transform: translateX(4px);
}

section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background: rgba(255, 255, 255, 0.22);
    border-color: rgba(255, 255, 255, 0.35);
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
}

.hero-section {
    background: linear-gradient(135deg, #E8F5EE 0%, #FFFFFF 45%, #F0FAF4 100%);
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 2.5rem 2rem;
    margin-bottom: 1.5rem;
    box-shadow: var(--shadow);
}

.hero-badge {
    display: inline-block;
    background: var(--primary-light);
    color: var(--primary-dark);
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
}

.hero-title {
    font-size: clamp(1.8rem, 4vw, 2.8rem);
    font-weight: 700;
    color: var(--primary-dark);
    margin: 0 0 0.5rem 0;
    line-height: 1.15;
}

.hero-subtitle {
    font-size: clamp(1rem, 2vw, 1.15rem);
    color: var(--text-muted);
    margin: 0;
    max-width: 720px;
}

.metric-card, .info-card, .result-card, .feature-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1.35rem;
    box-shadow: var(--shadow);
    height: 100%;
}

.metric-card h3, .info-card h3, .feature-card h3 {
    margin: 0 0 0.35rem 0;
    color: var(--text);
    font-size: 1rem;
}

.metric-card p, .info-card p, .feature-card p {
    margin: 0;
    color: var(--text-muted);
    font-size: 0.92rem;
}

.metric-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--primary);
    margin: 0.25rem 0 0 0;
}

.result-card {
    background: linear-gradient(135deg, #145C37 0%, #1B7F4B 100%);
    color: #FFFFFF;
    text-align: center;
    padding: 2rem 1.5rem;
}

.result-card .result-label {
    font-size: 0.95rem;
    opacity: 0.9;
    margin-bottom: 0.35rem;
}

.result-card .result-value {
    font-size: clamp(1.8rem, 4vw, 2.6rem);
    font-weight: 700;
    margin: 0;
    text-transform: capitalize;
}

.result-card .result-meta {
    margin-top: 0.75rem;
    font-size: 0.9rem;
    opacity: 0.85;
}

.page-header {
    margin-bottom: 1.25rem;
}

.page-header h1 {
    color: var(--primary-dark);
    font-size: clamp(1.5rem, 3vw, 2rem);
    margin: 0 0 0.35rem 0;
}

.page-header p {
    color: var(--text-muted);
    margin: 0;
}

.stButton > button {
    background: linear-gradient(135deg, #1B7F4B, #218F58);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.65rem 1.4rem;
    font-weight: 600;
    box-shadow: 0 6px 18px rgba(27, 127, 75, 0.25);
}

.stButton > button:hover {
    background: linear-gradient(135deg, #145C37, #1B7F4B);
    color: white;
    border: none;
}

.fertilizer-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 0.85rem;
    margin-top: 1rem;
}

.fertilizer-item {
    background: var(--surface-muted);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}

.fertilizer-item span {
    display: block;
    color: var(--text-muted);
    font-size: 0.85rem;
}

.fertilizer-item strong {
    display: block;
    color: var(--primary-dark);
    font-size: 1.35rem;
    margin-top: 0.25rem;
}

.sidebar-brand {
    padding: 0.5rem 0 1.25rem 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    margin-bottom: 1rem;
}

.sidebar-brand h2 {
    margin: 0;
    font-size: 1.35rem;
    font-weight: 700;
}

.sidebar-brand p {
    margin: 0.25rem 0 0 0;
    opacity: 0.85;
    font-size: 0.85rem;
}

@media (max-width: 768px) {
    .hero-section {
        padding: 1.5rem 1.25rem;
    }

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
"""
