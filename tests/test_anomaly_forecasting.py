"""
Unit tests for utils/anomaly.py and utils/forecasting.py using small
synthetic monthly series (no dependency on the actual GED CSV, since it
is not shipped in this repository).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd

from utils.anomaly import detect_anomalies
from utils.forecasting import forecast_counts


def _synthetic_monthly_series(n=24, baseline=10, spike_at=20, spike_value=200):
    dates = pd.date_range("2023-01-01", periods=n, freq="MS")
    counts = [baseline] * n
    counts[spike_at] = spike_value
    return pd.DataFrame({"date_start": dates, "event_count": counts})


def test_detect_anomalies_flags_spike():
    series = _synthetic_monthly_series()
    result = detect_anomalies(series, window=12, z_threshold=2.0)
    flagged_months = result[result["is_anomaly"]]["date_start"].tolist()
    assert series.iloc[20]["date_start"] in flagged_months


def test_detect_anomalies_no_false_positive_on_flat_series():
    series = _synthetic_monthly_series(spike_value=10)  # no spike, flat series
    result = detect_anomalies(series, window=12, z_threshold=2.0)
    assert result["is_anomaly"].sum() == 0


def test_forecast_counts_returns_expected_shape():
    series = _synthetic_monthly_series(spike_value=10)
    combined, direction, slope, r2 = forecast_counts(series, periods_ahead=6)
    forecast_rows = combined[combined["kind"] == "forecast"]
    assert len(forecast_rows) == 6
    assert direction in {"increasing", "decreasing", "roughly flat"}
