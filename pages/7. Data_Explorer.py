import io
import gzip

import streamlit as st

from utils.data_loader import load_data
from utils.theme import inject_css
from utils.components import page_header
from utils.state import render_global_filters

st.set_page_config(page_title="Data Explorer · MI Dashboard", page_icon="📊", layout="wide")
inject_css()

df = load_data()
filtered = render_global_filters(df)

page_header("📊 Data Explorer", "Search, filter, inspect, and export individual historical events")

search_col1, search_col2 = st.columns([2, 1])
with search_col1:
    query = st.text_input(
        "Search actor names (side_a / side_b) or conflict name", key="explorer_search",
        placeholder="e.g. a country, group, or conflict name...",
    )
with search_col2:
    min_fatal = st.number_input("Minimum fatalities (best est.)", min_value=0, value=0, step=1, key="explorer_minfatal")

result = filtered.copy()
if query:
    q = query.lower()
    mask = (
        result["side_a"].str.lower().str.contains(q, na=False)
        | result["side_b"].str.lower().str.contains(q, na=False)
        | result["conflict_name"].str.lower().str.contains(q, na=False)
    )
    result = result[mask]
if min_fatal > 0:
    result = result[result["best"] >= min_fatal]

st.markdown(f"**{len(result):,} events** match your search and filters.")

display_cols = [
    "date_start", "country", "region", "violence_type_label", "conflict_name",
    "side_a", "side_b", "best", "deaths_civilians", "source_headline", "adm_1",
]
rename_map = {
    "date_start": "Date", "country": "Country", "region": "Region",
    "violence_type_label": "Type", "conflict_name": "Conflict", "side_a": "Side A",
    "side_b": "Side B", "best": "Fatalities (best est.)", "deaths_civilians": "Civilian Deaths",
    "source_headline": "Source Headline", "adm_1": "Admin Region",
}
full_display = result[display_cols].rename(columns=rename_map).sort_values("Date", ascending=False)

st.markdown("#### Row Display")
row_option = st.radio("Rows to display", ["100", "1,000", "5,000", "All"], horizontal=True, key="explorer_row_option")

row_limits = {"100": 100, "1,000": 1000, "5,000": 5000}
proceed = True
if row_option == "All" and len(full_display) > 10000:
    proceed = st.checkbox(
        f"Confirm: display all {len(full_display):,} rows in the browser (this may be slow).",
        key="explorer_confirm_large",
    )
    if not proceed:
        st.info("Displaying the first 5,000 rows instead. Check the box above to view all rows.")
        show_df = full_display.head(5000)
    else:
        show_df = full_display
elif row_option == "All":
    show_df = full_display
else:
    show_df = full_display.head(row_limits[row_option])

st.dataframe(show_df, width="stretch", height=480, hide_index=True)

st.markdown("#### Export")
csv_buffer = io.StringIO()
full_display.to_csv(csv_buffer, index=False)
gz_buffer = io.BytesIO()
with gzip.GzipFile(fileobj=gz_buffer, mode="wb") as gz:
    gz.write(csv_buffer.getvalue().encode("utf-8"))

c1, c2 = st.columns(2)
with c1:
    st.download_button(
        "⬇ Download full filtered results (gzipped CSV)",
        data=gz_buffer.getvalue(), file_name="ged_filtered_events.csv.gz", mime="application/gzip",
    )
with c2:
    st.download_button(
        "⬇ Download displayed rows only (CSV)",
        data=show_df.to_csv(index=False).encode("utf-8"),
        file_name="ged_displayed_rows.csv", mime="text/csv",
    )

st.markdown("---")
st.markdown("#### Event Detail Lookup")
if not result.empty:
    ids = result["id"].astype(str).tolist()
    selected_id = st.selectbox("Select an event ID to view full details", ids, key="explorer_id_select")
    row = result[result["id"].astype(str) == selected_id].iloc[0]
    detail_cols = st.columns(2)
    with detail_cols[0]:
        st.markdown(f"""
        <div class='section-card'>
        <b>Event ID:</b> {row['id']}<br>
        <b>Date:</b> {row['date_start'].date()} to {row['date_end'].date()}<br>
        <b>Country / Region:</b> {row['country']} / {row['region']}<br>
        <b>Admin area:</b> {row['adm_1']} / {row['adm_2']}<br>
        <b>Type:</b> {row['violence_type_label']}<br>
        <b>Conflict:</b> {row['conflict_name']}<br>
        </div>
        """, unsafe_allow_html=True)
    with detail_cols[1]:
        st.markdown(f"""
        <div class='section-card'>
        <b>Side A:</b> {row['side_a']}<br>
        <b>Side B:</b> {row['side_b']}<br>
        <b>Fatalities (best/high/low):</b> {row['best']} / {row['high']} / {row['low']}<br>
        <b>Civilian deaths:</b> {row['deaths_civilians']}<br>
        <b>Sources reporting:</b> {row['number_of_sources']}<br>
        <b>Source headline:</b> {row['source_headline']}<br>
        </div>
        """, unsafe_allow_html=True)
