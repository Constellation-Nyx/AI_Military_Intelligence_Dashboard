"""
train_violence_model.py
------------------------
Standalone training script (run from the command line, not inside
Streamlit) that trains the Violence-Type prediction model and saves it
to models/ as compressed joblib artifacts:

    models/violence_type_model.pkl   - the trained RandomForestClassifier
    models/feature_encoders.pkl      - dict of LabelEncoders for categorical features
    models/target_encoder.pkl        - LabelEncoder for the target labels

Run this once before starting the app (or whenever you want to retrain):

    python train_violence_model.py

The Violence Type Prediction page (pages/4) loads these artifacts rather
than retraining on every app run.

Note on leakage: this model predicts `violence_type_label` (state-based /
non-state / one-sided), which is NOT derived from casualty counts, so
casualty fields are legitimate features here — unlike the Threat Level
model (see utils/ml_models.py), which must exclude them.
"""

import os
import sys
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, top_k_accuracy_score
from sklearn.preprocessing import LabelEncoder

sys.path.insert(0, os.path.dirname(__file__))
from utils.data_loader import load_data, MODELS_DIR
from utils.ml_models import VIOLENCE_TYPE_FEATURES, VIOLENCE_TYPE_CATEGORICAL, VIOLENCE_TYPE_TARGET


def main():
    print("Loading UCDP GED dataset...")
    # load_data() is decorated with st.cache_data, which still works fine when
    # called outside a running Streamlit app (it just runs uncached).
    df = load_data()
    print(f"Loaded {len(df):,} rows.")

    work = df[VIOLENCE_TYPE_FEATURES + [VIOLENCE_TYPE_TARGET]].dropna()
    print(f"{len(work):,} rows after dropping missing values in required columns.")

    X = work[VIOLENCE_TYPE_FEATURES].copy()
    encoders = {}
    for col in VIOLENCE_TYPE_CATEGORICAL:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        encoders[col] = le

    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(work[VIOLENCE_TYPE_TARGET])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print("Training RandomForestClassifier...")
    model = RandomForestClassifier(
        n_estimators=200, max_depth=16, random_state=42, class_weight="balanced", n_jobs=-1
    )
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    acc = accuracy_score(y_test, y_pred)
    macro_f1 = f1_score(y_test, y_pred, average="macro")
    weighted_f1 = f1_score(y_test, y_pred, average="weighted")
    n_classes = len(target_encoder.classes_)
    top_k = min(2, n_classes - 1) if n_classes > 2 else n_classes
    top_k_acc = top_k_accuracy_score(y_test, y_proba, k=top_k, labels=range(n_classes)) if top_k < n_classes else 1.0

    print("\n--- Evaluation (20% held-out test set) ---")
    print(f"Test set size:      {len(X_test):,}")
    print(f"Top-1 Accuracy:     {acc*100:.2f}%")
    print(f"Top-{top_k} Accuracy:     {top_k_acc*100:.2f}%")
    print(f"Macro F1:           {macro_f1:.3f}")
    print(f"Weighted F1:        {weighted_f1:.3f}")

    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, os.path.join(MODELS_DIR, "violence_type_model.pkl"), compress=3)
    joblib.dump(encoders, os.path.join(MODELS_DIR, "feature_encoders.pkl"), compress=3)
    joblib.dump(target_encoder, os.path.join(MODELS_DIR, "target_encoder.pkl"), compress=3)

    print(f"\nSaved model artifacts to {MODELS_DIR}/")


if __name__ == "__main__":
    main()
