"""
components.py
--------------
Reusable interface components built on top of theme.py's design tokens:
page headers, KPI cards, classification/leakage banners, threat badges,
and section labels. Pages import from here rather than hand-rolling HTML.
"""

import streamlit as st


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="app-header">
            <div>
                <div class="title">{title}</div>
                <div class="subtitle">{subtitle}</div>
            </div>
            <div class="status-pill">● DATA SOURCE: UCDP GED v26.1</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(label: str, value: str, delta: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def banner(text: str, kind: str = "warning"):
    """kind: 'warning' (orange, default caution), 'danger' (red, e.g. leakage
    warnings), or 'ok' (green, confirmations)."""
    icon = {"warning": "⚠", "danger": "⛔", "ok": "✅"}.get(kind, "⚠")
    cls = {"warning": "banner-warning", "danger": "banner-danger", "ok": "banner-ok"}.get(kind, "banner-warning")
    st.markdown(f"<div class='{cls}'>{icon} {text}</div>", unsafe_allow_html=True)


def severity_badge(level: str) -> str:
    level = str(level).lower()
    cls = {"low": "badge-low", "medium": "badge-medium", "high": "badge-high"}.get(level, "badge-medium")
    return f"<span class='{cls}'>{level.upper()}</span>"


def section_label(text: str):
    st.markdown(f"<div class='kpi-label' style='margin-top:0.6rem;'>{text}</div>", unsafe_allow_html=True)
