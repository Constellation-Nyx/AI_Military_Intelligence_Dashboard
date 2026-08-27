import streamlit as st
import plotly.express as px

from utils.data_loader import load_data
from utils.theme import inject_css, PLOTLY_TEMPLATE, VIOLENCE_TYPE_COLOR_MAP
from utils.components import page_header, banner
from utils.state import render_global_filters

st.set_page_config(page_title="Global Threat Map · MI Dashboard", page_icon="🌍", layout="wide")
inject_css()

df = load_data()
filtered = render_global_filters(df)

page_header("🌍 Global Threat Map", "Event locations from the dataset's own latitude/longitude fields")

banner(
    "Locations are geocoded by UCDP from public reporting and represent historical events only. "
    "This map does not show live positions of any forces or ongoing activity.",
    kind="warning",
)

st.sidebar.markdown("### Map Options")
type_options = sorted(filtered["violence_type_label"].unique().tolist())
sel_types = st.sidebar.multiselect("Event type", type_options, default=[], key="map_type_filter")
if sel_types:
    filtered = filtered[filtered["violence_type_label"].isin(sel_types)]

DOWNSAMPLE_LIMIT = 20000
auto_downsample = st.sidebar.checkbox("Auto-downsample for performance", value=True, key="map_downsample")

try:
    import pydeck as pdk
    PYDECK_AVAILABLE = True
except ImportError:
    PYDECK_AVAILABLE = False

renderer = st.sidebar.radio(
    "Map renderer",
    ["Plotly (default)"] + (["PyDeck (WebGL)"] if PYDECK_AVAILABLE else []),
    key="map_renderer",
)
if not PYDECK_AVAILABLE:
    st.sidebar.caption("Install `pydeck` to enable WebGL rendering: `pip install pydeck`")

st.markdown(f"**{len(filtered):,} events** match your filters.")

plot_df = filtered
if auto_downsample and len(filtered) > DOWNSAMPLE_LIMIT:
    st.info(
        f"Showing a random sample of {DOWNSAMPLE_LIMIT:,} of {len(filtered):,} matching events for performance. "
        "This limit applies to this map only — it does not affect other pages or analyses."
    )
    plot_df = filtered.sample(DOWNSAMPLE_LIMIT, random_state=42)
elif not auto_downsample and len(filtered) > DOWNSAMPLE_LIMIT:
    st.warning(f"Rendering all {len(filtered):,} points — this may be slow.")

if renderer == "PyDeck (WebGL)" and PYDECK_AVAILABLE:
    color_lookup = {
        "State-based armed conflict": [255, 77, 79],
        "Non-state conflict": [255, 159, 67],
        "One-sided violence": [76, 141, 255],
    }
    plot_df = plot_df.copy()
    plot_df["color"] = plot_df["violence_type_label"].map(color_lookup).apply(lambda c: c if isinstance(c, list) else [139, 150, 170])

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=plot_df[["latitude", "longitude", "color", "country", "date_start"]],
        get_position="[longitude, latitude]",
        get_fill_color="color",
        get_radius=15000,
        pickable=True,
        opacity=0.6,
    )
    view_state = pdk.ViewState(latitude=15, longitude=20, zoom=1.3)
    deck = pdk.Deck(
        layers=[layer], initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v10",
        tooltip={"text": "{country}"},
    )
    st.pydeck_chart(deck)
else:
    fig = px.scatter_map(
        plot_df, lat="latitude", lon="longitude", color="violence_type_label",
        color_discrete_map=VIOLENCE_TYPE_COLOR_MAP, hover_name="country",
        hover_data={"date_start": True, "best": True, "latitude": False, "longitude": False},
        zoom=1.3, height=620,
    )
    fig.update_layout(
        map_style="carto-darkmatter", margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor=PLOTLY_TEMPLATE["layout"]["paper_bgcolor"],
        font=PLOTLY_TEMPLATE["layout"]["font"],
        legend=dict(bgcolor="rgba(0,0,0,0)", title="Event type"),
    )
    st.plotly_chart(fig, width="stretch")

st.markdown("#### Event Density by Country")
density = filtered["country"].value_counts().reset_index()
density.columns = ["country", "events"]
fig2 = px.choropleth(
    density, locations="country", locationmode="country names", color="events",
    color_continuous_scale=["#121A2E", "#4C8DFF", "#FF9F43", "#FF4D4F"],
)
fig2.update_layout(**PLOTLY_TEMPLATE["layout"], height=440, geo=dict(bgcolor="rgba(0,0,0,0)"))
st.plotly_chart(fig2, width="stretch")
