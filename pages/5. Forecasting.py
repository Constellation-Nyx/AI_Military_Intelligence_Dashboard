import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import load_data
from utils.theme import inject_css, PLOTLY_TEMPLATE
from utils.components import page_header, banner
from utils.state import render_global_filters
from utils.anomaly import build_monthly_series
from utils.forecasting import forecast_counts

st.set_page_config(page_title="Forecasting · MI Dashboard", page_icon="📈", layout="wide")
inject_css()

df = load_data()
filtered = render_global_filters(df)

page_header("📈 Forecasting", "Simple historical trend extrapolation for event counts — estimates only")

banner(
    "These are simple ESTIMATES based on extrapolating the recent historical trend. They are NOT predictions "
    "of future attacks, incidents, or operational risk, and should not be used for decision-making.",
    kind="warning",
)

if filtered.empty:
    st.warning("No events match the current filters.")
    st.stop()

default_periods = st.session_state.get("forecast_years_ahead", 6)
periods = st.slider("Months to forecast ahead", 1, 24, default_periods, key="forecast_periods")

monthly = build_monthly_series(filtered)
if len(monthly) < 6:
    st.warning("Not enough time span in the current filter selection to fit a trend.")
    st.stop()

combined, trend_direction, slope, r2 = forecast_counts(monthly, periods_ahead=periods)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Historical Trend Direction", trend_direction.capitalize())
with c2:
    st.metric("Approx. Monthly Change (slope)", f"{slope:+.2f} events/month")
with c3:
    st.metric("Trend Fit (R²)", f"{r2:.2f}")

if r2 < 0.3:
    banner("R² is low — the recent trend line explains relatively little of the month-to-month variation. Treat the estimate with extra caution.", kind="danger")

st.markdown("#### Historical Events + Trend Estimate")
hist = combined[combined["kind"] == "historical"]
fut = combined[combined["kind"] == "forecast"]

fig = go.Figure()
fig.add_trace(go.Scatter(x=hist["date_start"], y=hist["event_count"], mode="lines", name="Historical", line=dict(color="#4C8DFF")))
fig.add_trace(go.Scatter(x=fut["date_start"], y=fut["event_count"], mode="lines+markers", name="Estimate (future)", line=dict(color="#FF9F43", dash="dot")))
layout_overrides = {**PLOTLY_TEMPLATE["layout"], "height": 460, "legend": dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)")}
fig.update_layout(**layout_overrides)
st.plotly_chart(fig, width="stretch")

st.markdown("#### Estimated Values")
show = fut[["date_start", "event_count"]].copy()
show["date_start"] = show["date_start"].dt.strftime("%Y-%m")
show["event_count"] = show["event_count"].round(1)
show = show.rename(columns={"date_start": "Month", "event_count": "Estimated Event Count"})
st.dataframe(show, width="stretch", hide_index=True)

st.caption(
    "Method: ordinary least-squares linear regression fit on the trailing 24 months of the current filter "
    "selection, extrapolated forward. No seasonality, external events, or intent signals are modeled."
)
