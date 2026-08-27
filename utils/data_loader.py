"""
data_loader.py
----------------
The single place the raw UCDP GED CSV is read. Every page imports
`load_data()` from here so the whole app works from one consistent,
cached copy of the data (mirrors the shared-loader pattern used
throughout the app for @st.cache_data reuse).

No fields are invented. Every column used elsewhere in the app comes
directly from GEDEvent_v26_1.csv.
"""

import os
import pandas as pd
import streamlit as st

USE_COLUMNS = [
    "id", "year", "type_of_violence", "conflict_name", "dyad_name",
    "side_a", "side_b", "number_of_sources", "source_headline",
    "where_prec", "where_description", "adm_1", "adm_2",
    "latitude", "longitude", "country", "region", "event_clarity",
    "date_prec", "date_start", "date_end",
    "deaths_a", "deaths_b", "deaths_civilians", "deaths_unknown",
    "best", "high", "low",
]

TYPE_OF_VIOLENCE_MAP = {
    1: "State-based armed conflict",
    2: "Non-state conflict",
    3: "One-sided violence",
}

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(ROOT_DIR, "data", "GEDEvent_v26_1.csv")
MODELS_DIR = os.path.join(ROOT_DIR, "models")


@st.cache_data(show_spinner="Loading UCDP GED v26.1 dataset...")
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load the raw GED CSV and apply light, non-invasive preprocessing."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. Place GEDEvent_v26_1.csv inside the data/ folder."
        )

    df = pd.read_csv(path, usecols=USE_COLUMNS, low_memory=False)

    df["date_start"] = pd.to_datetime(df["date_start"], errors="coerce")
    df["date_end"] = pd.to_datetime(df["date_end"], errors="coerce")
    df = df.dropna(subset=["date_start"])

    df["year_month"] = df["date_start"].dt.to_period("M").dt.to_timestamp()
    df["month"] = df["date_start"].dt.month
    df["weekday"] = df["date_start"].dt.day_name()
    df["violence_type_label"] = df["type_of_violence"].map(TYPE_OF_VIOLENCE_MAP).fillna("Unknown")

    for col in ["adm_1", "adm_2", "source_headline"]:
        df[col] = df[col].fillna("Unknown")

    df = df.dropna(subset=["latitude", "longitude"])

    return df


def validate_dataset(path: str = DATA_PATH) -> dict:
    """Check the dataset file/columns without loading the full dataframe into
    the app's main cache. Used by the Settings page for diagnostics."""
    result = {"path": path, "exists": os.path.exists(path)}
    if not result["exists"]:
        return result

    result["size_mb"] = round(os.path.getsize(path) / (1024 * 1024), 1)
    try:
        header = pd.read_csv(path, nrows=0)
        found_cols = set(header.columns)
        expected = set(USE_COLUMNS)
        result["missing_columns"] = sorted(expected - found_cols)
        result["found_columns"] = sorted(found_cols)
        result["readable"] = True
    except Exception as e:
        result["readable"] = False
        result["error"] = str(e)
    return result


def validate_models(models_dir: str = MODELS_DIR) -> dict:
    """Check whether the pretrained violence-type model artifacts exist."""
    required = ["violence_type_model.pkl", "feature_encoders.pkl", "target_encoder.pkl"]
    status = {}
    for f in required:
        p = os.path.join(models_dir, f)
        status[f] = os.path.exists(p)
    status["all_present"] = all(status.values())
    return status
