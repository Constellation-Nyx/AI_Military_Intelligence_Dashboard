"""
ml_models.py
------------
Two classification tasks live in this project, and they behave very
differently with respect to data leakage:

1. Violence-type prediction (see train_violence_model.py + pages/4):
   predicts `violence_type_label` (state-based / non-state / one-sided).
   This label is NOT derived from casualty counts, so casualty fields
   (deaths_a, deaths_b, deaths_civilians, best, high, low) are legitimate,
   non-leaking features here.

2. Threat-level / severity classification (pages/5):
   predicts Low/Medium/High severity, which IS derived from the `best`
   fatality estimate. This module trains BOTH:
     - a "leaked" model that (incorrectly) includes casualty fields as
       features, to demonstrate what leakage looks like and why its
       near-perfect accuracy is not real predictive skill, and
     - a "corrected" model that uses only contextual features with no
       casualty information, for an honest evaluation.
   Both are shown side-by-side on the Threat Level page so the leakage
   lesson is visible, not hidden.
"""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, f1_score
from sklearn.preprocessing import LabelEncoder
import streamlit as st

# --- Shared: violence-type prediction feature set (casualty fields OK here) ---
VIOLENCE_TYPE_FEATURES = [
    "country", "region", "month", "year", "event_clarity", "where_prec",
    "date_prec", "number_of_sources", "deaths_a", "deaths_b",
    "deaths_civilians", "deaths_unknown", "best", "high", "low",
]
VIOLENCE_TYPE_CATEGORICAL = ["country", "region"]
VIOLENCE_TYPE_TARGET = "violence_type_label"

# --- Threat-level / severity ---
LEAKAGE_COLUMNS = ["best", "high", "low", "deaths_a", "deaths_b", "deaths_civilians", "deaths_unknown"]
CONTEXT_FEATURES = [
    "type_of_violence", "region", "country", "month", "year",
    "date_prec", "where_prec", "event_clarity", "number_of_sources",
]
CATEGORICAL_FEATURES = ["region", "country"]


def label_severity(best: int) -> str:
    """Low: 0-1, Medium: 2-9, High: 10+ reported fatalities (fixed, disclosed thresholds)."""
    if best <= 1:
        return "Low"
    elif best <= 9:
        return "Medium"
    else:
        return "High"


def prepare_severity_dataset(df: pd.DataFrame) -> pd.DataFrame:
    data = df.copy()
    data["severity"] = data["best"].apply(label_severity)
    return data


def _sample_stratified(data: pd.DataFrame, label_col: str, sample_size: int, random_state: int = 42):
    if len(data) <= sample_size:
        return data
    parts = []
    for _, group in data.groupby(label_col):
        n = min(len(group), max(1, int(sample_size * len(group) / len(data))))
        parts.append(group.sample(n, random_state=random_state))
    return pd.concat(parts, ignore_index=True)


def _fit_rf(work: pd.DataFrame, feature_cols: list, categorical_cols: list, label_col: str, random_state=42):
    X = work[feature_cols].copy()
    encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le
    y = work[label_col]

    labels = sorted(y.unique().tolist())
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=random_state, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=150, max_depth=12, random_state=random_state, class_weight="balanced", n_jobs=-1
    )
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    report = classification_report(y_test, y_pred, labels=labels, output_dict=True, zero_division=0)
    importances = pd.DataFrame({"feature": feature_cols, "importance": model.feature_importances_}).sort_values(
        "importance", ascending=False
    )
    return {
        "model": model, "encoders": encoders, "accuracy": acc, "macro_f1": macro_f1,
        "confusion_matrix": cm, "labels": labels, "report": report,
        "feature_importance": importances, "n_train": len(X_train), "n_test": len(X_test),
    }


@st.cache_resource(show_spinner="Training threat-level models (leaked vs. corrected)...")
def train_threat_models(df: pd.DataFrame, sample_size: int, random_state: int = 42):
    """Train both the leaked and the corrected severity classifiers and
    return both result dicts for side-by-side comparison."""
    data = prepare_severity_dataset(df)
    data = _sample_stratified(data, "severity", sample_size, random_state)

    # Leaked: contextual features PLUS the casualty fields the label was derived from
    leaked_features = CONTEXT_FEATURES + LEAKAGE_COLUMNS
    work_leaked = data[leaked_features + ["severity"]].dropna()
    leaked_result = _fit_rf(work_leaked, leaked_features, CATEGORICAL_FEATURES, "severity", random_state)

    # Corrected: contextual features only, casualty fields excluded
    work_corrected = data[CONTEXT_FEATURES + ["severity"]].dropna()
    corrected_result = _fit_rf(work_corrected, CONTEXT_FEATURES, CATEGORICAL_FEATURES, "severity", random_state)

    return {"leaked": leaked_result, "corrected": corrected_result, "class_counts": data["severity"].value_counts().to_dict()}
