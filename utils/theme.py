"""
theme.py
--------
Centralized visual identity for the dashboard: color tokens, typography,
the injected dark "command-center" CSS, and a shared Plotly layout
template so every chart on every page looks consistent.

This module intentionally contains ONLY styling/theme concerns. Reusable
UI *components* (KPI cards, page headers, badges) live in components.py.
"""

import streamlit as st

# ---- Design tokens -------------------------------------------------------
BG = "#0B1120"
PANEL = "#121A2E"
PANEL_ALT = "#161F38"
BORDER = "#22304F"
TEXT = "#E6EAF2"
MUTED = "#8B96AA"
ACCENT_RED = "#FF4D4F"
ACCENT_ORANGE = "#FF9F43"
ACCENT_GREEN = "#2ED573"
ACCENT_BLUE = "#4C8DFF"

FONT_BODY = "'Inter', sans-serif"
FONT_MONO = "'JetBrains Mono', monospace"


def inject_css():
    """Inject the shared dark theme CSS. Call once near the top of every page."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

        html, body, [class*="css"] {{
            font-family: {FONT_BODY};
        }}

        .stApp {{
            background: {BG};
            color: {TEXT};
        }}

        section[data-testid="stSidebar"] {{
            background: {PANEL};
            border-right: 1px solid {BORDER};
        }}

        .filter-count {{
            color: {MUTED};
            font-size: 0.78rem;
            margin-top: 0.4rem;
            letter-spacing: 0.02em;
        }}

        h1, h2, h3 {{
            color: {TEXT};
            font-weight: 700;
            letter-spacing: -0.01em;
        }}

        .app-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.9rem 1.3rem;
            background: linear-gradient(90deg, {PANEL} 0%, {PANEL_ALT} 100%);
            border: 1px solid {BORDER};
            border-radius: 10px;
            margin-bottom: 1.4rem;
        }}

        .app-header .title {{
            font-size: 1.15rem;
            font-weight: 700;
            color: {TEXT};
            letter-spacing: 0.01em;
        }}

        .app-header .subtitle {{
            font-size: 0.78rem;
            color: {MUTED};
            margin-top: 2px;
        }}

        .status-pill {{
            font-family: {FONT_MONO};
            font-size: 0.72rem;
            padding: 4px 10px;
            border-radius: 20px;
            border: 1px solid {ACCENT_GREEN};
            color: {ACCENT_GREEN};
            background: rgba(46, 213, 115, 0.08);
        }}

        .kpi-card {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1rem 1.1rem;
            height: 100%;
        }}

        .kpi-label {{
            color: {MUTED};
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 6px;
        }}

        .kpi-value {{
            font-family: {FONT_MONO};
            font-size: 1.9rem;
            font-weight: 700;
            color: {TEXT};
        }}

        .kpi-delta {{
            font-size: 0.78rem;
            margin-top: 4px;
            color: {MUTED};
        }}

        .section-card {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1.2rem 1.3rem;
            margin-bottom: 1rem;
        }}

        .badge-low {{
            color: {ACCENT_GREEN};
            border: 1px solid {ACCENT_GREEN};
            background: rgba(46, 213, 115, 0.08);
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-family: {FONT_MONO};
        }}

        .badge-medium {{
            color: {ACCENT_ORANGE};
            border: 1px solid {ACCENT_ORANGE};
            background: rgba(255, 159, 67, 0.08);
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-family: {FONT_MONO};
        }}

        .badge-high {{
            color: {ACCENT_RED};
            border: 1px solid {ACCENT_RED};
            background: rgba(255, 77, 79, 0.08);
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-family: {FONT_MONO};
        }}

        .banner-warning {{
            border-left: 3px solid {ACCENT_ORANGE};
            background: rgba(255, 159, 67, 0.06);
            padding: 0.7rem 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: {MUTED};
            margin: 0.8rem 0 1.2rem 0;
        }}

        .banner-danger {{
            border-left: 3px solid {ACCENT_RED};
            background: rgba(255, 77, 79, 0.06);
            padding: 0.7rem 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: {TEXT};
            margin: 0.8rem 0 1.2rem 0;
        }}

        .banner-ok {{
            border-left: 3px solid {ACCENT_GREEN};
            background: rgba(46, 213, 115, 0.06);
            padding: 0.7rem 1rem;
            border-radius: 6px;
            font-size: 0.85rem;
            color: {TEXT};
            margin: 0.8rem 0 1.2rem 0;
        }}

        div[data-testid="stMetric"] {{
            background: {PANEL};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 0.8rem 1rem;
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
        }}

        .stTabs [data-baseweb="tab"] {{
            background: {PANEL};
            border-radius: 8px 8px 0 0;
            border: 1px solid {BORDER};
        }}

        footer, #MainMenu {{visibility: hidden;}}
        </style>
        """,
        unsafe_allow_html=True,
    )


# Shared Plotly layout — pass as **PLOTLY_TEMPLATE["layout"] into fig.update_layout()
PLOTLY_TEMPLATE = {
    "layout": {
        "paper_bgcolor": PANEL,
        "plot_bgcolor": PANEL,
        "font": {"color": TEXT, "family": "Inter"},
        "colorway": [ACCENT_BLUE, ACCENT_ORANGE, ACCENT_RED, ACCENT_GREEN, "#A78BFA", "#5EEAD4"],
        "xaxis": {"gridcolor": BORDER, "zerolinecolor": BORDER},
        "yaxis": {"gridcolor": BORDER, "zerolinecolor": BORDER},
        "legend": {"bgcolor": "rgba(0,0,0,0)"},
        "margin": {"t": 40, "b": 30, "l": 30, "r": 20},
    }
}

SEVERITY_COLOR_MAP = {"Low": ACCENT_GREEN, "Medium": ACCENT_ORANGE, "High": ACCENT_RED}
VIOLENCE_TYPE_COLOR_MAP = {
    "State-based armed conflict": ACCENT_RED,
    "Non-state conflict": ACCENT_ORANGE,
    "One-sided violence": ACCENT_BLUE,
}
