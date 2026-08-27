import streamlit as st
import plotly.express as px
import pandas as pd

from utils.data_loader import load_data
from utils.theme import inject_css, PLOTLY_TEMPLATE
from utils.components import page_header
from utils.state import render_global_filters

st.set_page_config(page_title="Country Analysis · MI Dashboard", page_icon="🌎", layout="wide")
inject_css()

df = load_data()
filtered = render_global_filters(df)

page_header("🌎 Country / Regional Analysis", "Compare regions and countries by event volume, type, and trend")

if filtered.empty:
    st.warning("No events match the current filters.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Region Comparison", "Country Comparison", "Trend by Region"])

with tab1:
    st.markdown("#### Events and Fatalities by Region")
    region_stats = filtered.groupby("region").agg(events=("id", "count"), fatalities=("best", "sum")).reset_index()
    region_stats = region_stats.sort_values("events", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(region_stats, x="region", y="events", labels={"region": "", "events": "Events"})
        fig.update_traces(marker_color="#4C8DFF")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
        st.plotly_chart(fig, width="stretch")
    with c2:
        fig = px.bar(region_stats, x="region", y="fatalities", labels={"region": "", "fatalities": "Fatalities (best est.)"})
        fig.update_traces(marker_color="#FF4D4F")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=380)
        st.plotly_chart(fig, width="stretch")

    st.dataframe(
        region_stats.rename(columns={"region": "Region", "events": "Events", "fatalities": "Fatalities"}),
        width="stretch", hide_index=True,
    )

with tab2:
    st.markdown("#### Top Countries Comparison")
    top_n = st.slider("Number of countries to compare", 5, 30, 15, key="country_topn")
    country_stats = filtered.groupby("country").agg(events=("id", "count"), fatalities=("best", "sum")).reset_index()
    country_stats = country_stats.sort_values("events", ascending=False).head(top_n)

    fig = px.bar(
        country_stats.sort_values("events"), x="events", y="country", orientation="h",
        labels={"events": "Events", "country": ""}, hover_data={"fatalities": True},
    )
    fig.update_traces(marker_color="#FF9F43")
    fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=max(380, top_n * 24))
    st.plotly_chart(fig, width="stretch")

with tab3:
    st.markdown("#### Monthly Event Trend by Region")
    trend = filtered.groupby([pd.Grouper(key="date_start", freq="MS"), "region"]).size().reset_index(name="events")
    fig = px.line(trend, x="date_start", y="events", color="region", labels={"date_start": "Month", "events": "Events"})
    fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=440)
    st.plotly_chart(fig, width="stretch")

    st.markdown("#### Event Type Composition by Region")
    comp = filtered.groupby(["region", "violence_type_label"]).size().reset_index(name="events")
    fig2 = px.bar(comp, x="region", y="events", color="violence_type_label", barmode="stack",
                   labels={"region": "", "events": "Events", "violence_type_label": "Event type"})
    fig2.update_layout(**PLOTLY_TEMPLATE["layout"], height=420)
    st.plotly_chart(fig2, width="stretch")
