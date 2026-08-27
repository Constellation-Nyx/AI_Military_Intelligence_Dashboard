import streamlit as st

from utils.data_loader import load_data, validate_dataset, validate_models, DATA_PATH, MODELS_DIR
from utils.theme import inject_css
from utils.components import page_header, banner

st.set_page_config(page_title="Settings · MI Dashboard", page_icon="⚙️", layout="wide")
inject_css()

page_header("⚙️ Settings", "Dataset and model diagnostics, cache controls")

st.markdown("#### Dataset Validation")
status = validate_dataset()
if not status["exists"]:
    banner(f"Dataset not found at `{DATA_PATH}`. Copy GEDEvent_v26_1.csv into the data/ folder.", kind="danger")
else:
    banner(f"Dataset found at `{DATA_PATH}` ({status.get('size_mb', '?')} MB).", kind="ok")
    if status.get("readable"):
        if status["missing_columns"]:
            banner(f"Missing expected columns: {status['missing_columns']}", kind="danger")
        else:
            banner("All expected columns are present.", kind="ok")
    else:
        banner(f"Could not read the CSV header: {status.get('error')}", kind="danger")

st.markdown("#### Model Artifact Validation")
model_status = validate_models()
for f in ["violence_type_model.pkl", "feature_encoders.pkl", "target_encoder.pkl"]:
    if model_status[f]:
        st.markdown(f"✅ `models/{f}` found")
    else:
        st.markdown(f"❌ `models/{f}` missing")

if not model_status["all_present"]:
    banner(f"Run `python train_violence_model.py` from the project root to generate model artifacts in `{MODELS_DIR}/`.", kind="warning")
else:
    banner("All Violence Type Prediction model artifacts are present.", kind="ok")

st.markdown("---")
st.markdown("#### Dataset Summary")
try:
    df = load_data()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Events", f"{len(df):,}")
    c2.metric("Countries", df["country"].nunique())
    c3.metric("Regions", df["region"].nunique())
    c4.metric("Year Range", f"{int(df['year'].min())}–{int(df['year'].max())}")
except FileNotFoundError:
    st.info("Load the dataset (see above) to see summary statistics.")

st.markdown("---")
st.markdown("#### Cache Controls")
st.caption("Clearing the cache forces the dataset and any cached models to reload/retrain on next use.")
if st.button("🔄 Clear data cache", key="clear_data_cache"):
    st.cache_data.clear()
    st.success("Data cache cleared. Reload the page to re-read the dataset.")
if st.button("🔄 Clear model cache (Threat Level page)", key="clear_resource_cache"):
    st.cache_resource.clear()
    st.success("Resource cache cleared. The Threat Level models will retrain on next visit.")

st.markdown("---")
st.markdown("#### About")
st.markdown(
    """
This is an academic exploratory-analysis project built on the UCDP Georeferenced Event Dataset (GED) v26.1.
It analyzes historical, publicly documented conflict-event records only and performs no real-time data
collection, surveillance, or targeting. See the project README for full details and limitations.
"""
)
