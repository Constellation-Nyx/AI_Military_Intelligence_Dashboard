"""
Unit tests for utils/ml_models.py: severity labeling thresholds and the
leakage guard (leaked-vs-corrected feature sets must not overlap in the
way that would defeat the corrected model's purpose).

Run with: pytest tests/
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.ml_models import label_severity, LEAKAGE_COLUMNS, CONTEXT_FEATURES


def test_label_severity_low():
    assert label_severity(0) == "Low"
    assert label_severity(1) == "Low"


def test_label_severity_medium():
    assert label_severity(2) == "Medium"
    assert label_severity(9) == "Medium"


def test_label_severity_high():
    assert label_severity(10) == "High"
    assert label_severity(1000) == "High"


def test_context_features_exclude_leakage_columns():
    """The corrected model's feature set must never include any
    casualty-derived column used to build the severity label."""
    overlap = set(CONTEXT_FEATURES) & set(LEAKAGE_COLUMNS)
    assert overlap == set(), f"Leakage columns found in context features: {overlap}"
