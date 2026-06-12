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

/* Home hero is rendered via components.html; keep iframe seamless on the home page. */
iframe[height="340"] {
    border: none !important;
    margin-bottom: 1.5rem;
    background: transparent;
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
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}

/* ── Farm Assistant (Crop Recommendation) Dark Theme ── */

.farm-page {
    background: linear-gradient(180deg, #0D1F17 0%, #122820 100%);
    border-radius: 20px;
    padding: 1.75rem;
    margin-bottom: 1rem;
}

.farm-page .page-header h1 {
    color: #FFFFFF;
}

.farm-page .page-header p {
    color: #A8C4B4;
}

.workflow-step-header {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    margin-bottom: 1rem;
    padding: 1rem 1.25rem;
    background: #FFFFFF;
    border-radius: 14px 14px 0 0;
    border-left: 4px solid #2ECC71;
}

.workflow-step-header .step-icon {
    font-size: 1.4rem;
}

.workflow-step-header .step-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #145C37;
    margin: 0;
}

.location-pins {
    background: #F0FAF4;
    border: 1px solid #D8E8DE;
    border-radius: 14px;
    padding: 1rem 1.25rem;
    color: #1A2E22;
    font-weight: 600;
    line-height: 1.8;
}

.season-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(46, 204, 113, 0.15);
    border: 1px solid rgba(46, 204, 113, 0.35);
    color: #2ECC71;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    font-size: 0.9rem;
    font-weight: 600;
    margin: 0.75rem 0 1rem 0;
}

.workflow-connector {
    text-align: center;
    color: #2ECC71;
    font-size: 1.25rem;
    margin: 0.15rem 0;
    opacity: 0.7;
}

.weather-card {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 0.85rem;
}

.weather-stat {
    background: #F0FAF4;
    border: 1px solid #D8E8DE;
    border-radius: 14px;
    padding: 1rem;
    text-align: center;
}

.weather-stat .label {
    font-size: 0.8rem;
    color: #5C7366;
    margin-bottom: 0.25rem;
}

.weather-stat .value {
    font-size: 1.25rem;
    font-weight: 700;
    color: #145C37;
}

.crop-result-card {
    background: linear-gradient(135deg, #145C37 0%, #1B7F4B 60%, #218F58 100%);
    border-radius: 18px;
    padding: 2rem;
    text-align: center;
    color: #FFFFFF;
}

.crop-result-card .crop-name {
    font-size: clamp(2rem, 5vw, 3rem);
    font-weight: 700;
    margin: 0.25rem 0;
    text-transform: capitalize;
}

.crop-result-card .confidence {
    font-size: 1.1rem;
    opacity: 0.9;
}

.harvest-card {
    background: linear-gradient(135deg, #1A2E22 0%, #243D30 100%);
    border-radius: 18px;
    padding: 1.75rem;
    color: #FFFFFF;
}

.harvest-card .harvest-title {
    font-size: 1rem;
    opacity: 0.85;
    margin-bottom: 0.25rem;
}

.harvest-card .harvest-value {
    font-size: clamp(1.6rem, 4vw, 2.4rem);
    font-weight: 700;
    color: #2ECC71;
    margin: 0;
}

.harvest-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.harvest-stat {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1rem;
}

.harvest-stat .label {
    font-size: 0.8rem;
    opacity: 0.75;
}

.harvest-stat .value {
    font-size: 1.2rem;
    font-weight: 700;
    margin-top: 0.25rem;
}

.fert-card {
    background: #FFFFFF;
    border: 1px solid #D8E8DE;
    border-radius: 16px;
    padding: 1.25rem;
    height: 100%;
}

.fert-card.primary {
    border-color: #2ECC71;
    background: linear-gradient(135deg, #F0FAF4, #FFFFFF);
}

.fert-card h4 {
    margin: 0 0 0.5rem 0;
    color: #145C37;
}

.fert-card p {
    margin: 0;
    color: #5C7366;
    font-size: 0.92rem;
}

.explanation-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 1.5rem;
    border-left: 4px solid #2ECC71;
    line-height: 1.7;
    color: #1A2E22;
}

</style>
"""
