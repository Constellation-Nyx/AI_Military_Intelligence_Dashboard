"""
app.py
------
Main entry point: dashboard overview, live KPIs, and navigation.
The remaining eight pages live in pages/ and are picked up automatically
by Streamlit's built-in multipage navigation.
"""

import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import inject_css, PLOTLY_TEMPLATE
from utils.components import page_header, kpi_card, banner
from utils.state import render_global_filters

st.set_page_config(
    page_title="AI-Based Military Intelligence Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

st.sidebar.markdown("## 🛰️ Military Intelligence Dashboard")
st.sidebar.caption("Exploratory analysis of UCDP GED v26.1")
st.sidebar.markdown("---")

try:
    df = load_data()
except FileNotFoundError as e:
    st.error(str(e))
    st.info("Copy GEDEvent_v26_1.csv into the `data/` folder, then reload the app.")
    st.stop()

filtered = render_global_filters(df)

page_header("🏠 Home", "Academic analysis of historical, publicly documented conflict events · Not for operational use")

banner(
    "This dashboard analyzes historical, publicly available conflict-event records for academic purposes only. "
    "It does not use real-time data and must not be used for operational military decision-making or targeting.",
    kind="warning",
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Total Events (filtered)", f"{len(filtered):,}", f"of {len(df):,} total in dataset")
with c2:
    kpi_card("Countries Represented", f"{filtered['country'].nunique()}", f"across {filtered['region'].nunique()} regions")
with c3:
    kpi_card("Total Fatalities (best est.)", f"{int(filtered['best'].sum()):,}", "UCDP 'best' estimate sum")
with c4:
    yr = st.session_state["year_range"]
    kpi_card("Year Coverage", f"{yr[0]} → {yr[1]}", "based on current global filters")

st.markdown("<br>", unsafe_allow_html=True)

col_a, col_b = st.columns([2, 1])
with col_a:
    st.markdown("#### Event Trend Over Time")
    monthly = filtered.groupby(filtered["date_start"].dt.to_period("M")).size()
    monthly.index = monthly.index.to_timestamp()
    fig = px.area(x=monthly.index, y=monthly.values, labels={"x": "Month", "y": "Events"})
    fig.update_traces(line_color="#4C8DFF", fillcolor="rgba(76,141,255,0.15)")
    fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=360)
    st.plotly_chart(fig, width="stretch")

with col_b:
    st.markdown("#### Events by Type")
    type_counts = filtered["violence_type_label"].value_counts()
    fig2 = px.pie(names=type_counts.index, values=type_counts.values, hole=0.55)
    fig2.update_layout(**PLOTLY_TEMPLATE["layout"], height=360, showlegend=True)
    st.plotly_chart(fig2, width="stretch")

col_c, col_d = st.columns(2)
with col_c:
    st.markdown("#### Top 10 Countries by Event Count")
    top_countries = filtered["country"].value_counts().head(10).sort_values()
    fig3 = px.bar(x=top_countries.values, y=top_countries.index, orientation="h", labels={"x": "Events", "y": ""})
    fig3.update_traces(marker_color="#FF9F43")
    fig3.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
    st.plotly_chart(fig3, width="stretch")

with col_d:
    st.markdown("#### Events by Region")
    region_counts = filtered["region"].value_counts()
    fig4 = px.bar(x=region_counts.index, y=region_counts.values, labels={"x": "", "y": "Events"})
    fig4.update_traces(marker_color="#2ED573")
    fig4.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
    st.plotly_chart(fig4, width="stretch")

st.markdown("---")
st.markdown("#### Navigate")
st.markdown(
    """
- 🗺️ **Global Threat Map** — interactive geospatial view of events
- 🌎 **Regional Analysis** — compare countries and regions
- 🤖 **Violence Type Prediction** — predict conflict category from context + casualty data (no leakage)
- 🚨 **Threat Level** — severity classification, with an explicit leaked-vs-corrected comparison
- 📈 **Forecasting** — simple historical trend estimates
- 🧠 **AI Intelligence** — automated summary of the current selection
- 📊 **Data Explorer** — search, filter, and export events
- ⚙️ **Settings** — dataset and model diagnostics
"""
)

st.caption("Data source: Uppsala Conflict Data Program (UCDP) Georeferenced Event Dataset, version 26.1.")
