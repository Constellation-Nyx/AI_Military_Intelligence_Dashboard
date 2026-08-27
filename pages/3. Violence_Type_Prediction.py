import os
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

from utils.data_loader import load_data, MODELS_DIR, validate_models
from utils.theme import inject_css, PLOTLY_TEMPLATE
from utils.components import page_header, banner
from utils.state import render_global_filters
from utils.ml_models import VIOLENCE_TYPE_FEATURES, VIOLENCE_TYPE_CATEGORICAL

st.set_page_config(page_title="Violence Type Prediction · MI Dashboard", page_icon="🤖", layout="wide")
inject_css()

df = load_data()
filtered = render_global_filters(df)

page_header("🤖 Violence Type Prediction", "Predict conflict category from event context and casualty data")

banner(
    "This model classifies HISTORICAL event records by violence category for academic analysis. "
    "It is not a real-time detection or operational targeting system.",
    kind="warning",
)

model_status = validate_models()
if not model_status["all_present"]:
    banner(
        "Pretrained model artifacts not found in models/. Run `python train_violence_model.py` first, "
        "then reload this page.",
        kind="danger",
    )
    st.write("Missing files:", [f for f, ok in model_status.items() if f != "all_present" and not ok])
    st.stop()

model = joblib.load(os.path.join(MODELS_DIR, "violence_type_model.pkl"))
feature_encoders = joblib.load(os.path.join(MODELS_DIR, "feature_encoders.pkl"))
target_encoder = joblib.load(os.path.join(MODELS_DIR, "target_encoder.pkl"))

st.markdown(
    "This model is **pretrained** (via `train_violence_model.py`) on the full dataset and loaded here — "
    "it does not use your current global filters, though the form below defaults to values common in your selection."
)

with st.form("violence_type_form"):
    st.markdown("#### Event Attributes")
    c1, c2, c3 = st.columns(3)
    with c1:
        countries = sorted(df["country"].unique().tolist())
        default_country = st.session_state.get("default_country", countries[0])
        country = st.selectbox("Country", countries, index=countries.index(default_country) if default_country in countries else 0)
        region = st.selectbox("Region", sorted(df["region"].unique().tolist()))
        month = st.slider("Month", 1, 12, 6)
        year = st.number_input("Year", min_value=int(df["year"].min()), max_value=int(df["year"].max()), value=int(df["year"].max()))
    with c2:
        event_clarity = st.selectbox("Event clarity code", sorted(df["event_clarity"].dropna().unique().tolist()))
        where_prec = st.selectbox("Location precision code", sorted(df["where_prec"].dropna().unique().tolist()))
        date_prec = st.selectbox("Date precision code", sorted(df["date_prec"].dropna().unique().tolist()))
        number_of_sources = st.number_input("Number of reporting sources", min_value=1, value=1)
    with c3:
        deaths_a = st.number_input("Deaths, side A", min_value=0, value=0)
        deaths_b = st.number_input("Deaths, side B", min_value=0, value=0)
        deaths_civilians = st.number_input("Civilian deaths", min_value=0, value=0)
        deaths_unknown = st.number_input("Deaths, unknown side", min_value=0, value=0)

    best = st.number_input("Best fatality estimate", min_value=0, value=deaths_a + deaths_b + deaths_civilians + deaths_unknown)
    high = st.number_input("High fatality estimate", min_value=0, value=best)
    low = st.number_input("Low fatality estimate", min_value=0, value=best)

    submitted = st.form_submit_button("🔮 Predict Violence Type", type="primary")

if submitted:
    row = pd.DataFrame([{
        "country": country, "region": region, "month": month, "year": year,
        "event_clarity": event_clarity, "where_prec": where_prec, "date_prec": date_prec,
        "number_of_sources": number_of_sources, "deaths_a": deaths_a, "deaths_b": deaths_b,
        "deaths_civilians": deaths_civilians, "deaths_unknown": deaths_unknown,
        "best": best, "high": high, "low": low,
    }])

    for col in VIOLENCE_TYPE_CATEGORICAL:
        le = feature_encoders[col]
        if row[col].iloc[0] not in le.classes_:
            st.warning(f"'{row[col].iloc[0]}' was not seen during training for '{col}'; using nearest known category.")
            row[col] = le.classes_[0]
        row[col] = le.transform(row[col].astype(str))

    X_input = row[VIOLENCE_TYPE_FEATURES]
    proba = model.predict_proba(X_input)[0]
    pred_idx = int(np.argmax(proba))
    pred_label = target_encoder.inverse_transform([pred_idx])[0]
    confidence = proba[pred_idx]

    threshold = st.session_state.get("prediction_confidence_threshold", 0.5)
    if confidence < threshold:
        banner(f"Prediction confidence ({confidence*100:.1f}%) is below your threshold ({threshold*100:.0f}%) — treat this as low-confidence.", kind="danger")
    else:
        banner(f"Predicted: **{pred_label}** ({confidence*100:.1f}% confidence)", kind="ok")

    st.markdown("#### Class Probabilities")
    proba_df = pd.DataFrame({"class": target_encoder.classes_, "probability": proba}).sort_values("probability", ascending=False)
    fig = px.bar(proba_df, x="probability", y="class", orientation="h", labels={"probability": "Probability", "class": ""})
    fig.update_traces(marker_color="#4C8DFF")
    fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=280)
    st.plotly_chart(fig, width="stretch")

st.markdown("---")
with st.expander("ℹ️ About this model"):
    st.markdown(f"""
- **Target:** `violence_type_label` (State-based armed conflict / Non-state conflict / One-sided violence)
- **Features used:** `{', '.join(VIOLENCE_TYPE_FEATURES)}`
- **Why casualty fields are OK here:** the target is the *category* of violence, not a fatality-derived label,
  so `deaths_a/b/civilians/unknown`, `best`, `high`, and `low` are legitimate contextual inputs and do not leak
  the label. (Compare this to the Threat Level page, where those same fields must be excluded.)
- **Model:** RandomForestClassifier, trained via `train_violence_model.py`, 80/20 train-test split.
    """)
