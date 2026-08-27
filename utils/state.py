"""
state.py
--------
Manages shared application state via st.session_state so that filters
and settings persist as the user navigates between pages, instead of
resetting on every page load. Covers:

    - global year-range filter
    - global region filter
    - default country (used to pre-select values on ML/forecast pages)
    - forecast-horizon setting
    - prediction-confidence-threshold setting (for the ML pages)
"""

import streamlit as st


def init_state(df):
    """Initialize session_state defaults exactly once per session."""
    if st.session_state.get("_state_initialized"):
        return

    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    st.session_state["year_range"] = (min_year, max_year)
    st.session_state["region_filter"] = []
    st.session_state["country_filter"] = []
    st.session_state["default_country"] = df["country"].value_counts().idxmax()
    st.session_state["forecast_years_ahead"] = 5
    st.session_state["prediction_confidence_threshold"] = 0.5
    st.session_state["_state_initialized"] = True


def get_filtered_df(df):
    """Apply the current global filters (year range, region, country) to df."""
    lo, hi = st.session_state["year_range"]
    mask = (df["year"] >= lo) & (df["year"] <= hi)
    if st.session_state["region_filter"]:
        mask &= df["region"].isin(st.session_state["region_filter"])
    if st.session_state["country_filter"]:
        mask &= df["country"].isin(st.session_state["country_filter"])
    return df[mask]


def render_global_filters(df):
    """Render the shared sidebar filter controls and return the filtered df.
    Call this once near the top of every page, after init_state(df)."""
    init_state(df)

    st.sidebar.markdown("### Global Filters")
    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    yr = st.sidebar.slider(
        "Year range", min_value=min_year, max_value=max_year,
        value=st.session_state["year_range"], key="global_year_slider",
    )
    st.session_state["year_range"] = yr

    regions = sorted(df["region"].dropna().unique().tolist())
    valid_default_regions = [r for r in st.session_state["region_filter"] if r in regions]
    reg = st.sidebar.multiselect(
        "Region", options=regions, default=valid_default_regions, key="global_region_select",
    )
    st.session_state["region_filter"] = reg

    region_scoped = df[df["region"].isin(reg)] if reg else df
    countries = sorted(region_scoped["country"].dropna().unique().tolist())
    valid_default_countries = [c for c in st.session_state["country_filter"] if c in countries]
    cty = st.sidebar.multiselect(
        "Country", options=countries, default=valid_default_countries, key="global_country_select",
    )
    st.session_state["country_filter"] = cty

    filtered = get_filtered_df(df)
    st.sidebar.markdown(
        f"<div class='filter-count'>{len(filtered):,} events match global filters</div>",
        unsafe_allow_html=True,
    )

    with st.sidebar.expander("⚙️ Advanced settings"):
        st.session_state["forecast_years_ahead"] = st.slider(
            "Default forecast horizon (months)", 1, 24,
            st.session_state["forecast_years_ahead"], key="global_forecast_horizon",
        )
        st.session_state["prediction_confidence_threshold"] = st.slider(
            "Prediction confidence threshold", 0.0, 1.0,
            st.session_state["prediction_confidence_threshold"], 0.05,
            key="global_confidence_threshold",
            help="Predictions below this confidence are flagged as low-confidence on ML pages.",
        )
        if st.button("Reset all filters", key="reset_filters_btn"):
            st.session_state["year_range"] = (min_year, max_year)
            st.session_state["region_filter"] = []
            st.session_state["country_filter"] = []
            st.rerun()

    return filtered
