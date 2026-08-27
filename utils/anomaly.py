"""
anomaly.py
----------
Detects periods of UNUSUALLY HIGH historical event activity compared to
a rolling baseline. This is descriptive statistics on the past, not a
model of the future — see the disclaimer rendered on the Anomaly
Detection page.

Method: aggregate event counts into a regular time series (monthly),
compute a rolling mean/std baseline, and flag points whose z-score
exceeds a threshold. This is simple and fully explainable, which is
preferable to an opaque model for a "why was this flagged" use case.
"""

import pandas as pd


def build_monthly_series(df: pd.DataFrame, group_col: str = None):
    """Aggregate event counts by month, optionally split by a group column."""
    if group_col and group_col in df.columns:
        series = (
            df.groupby([pd.Grouper(key="date_start", freq="MS"), group_col])
            .size()
            .reset_index(name="event_count")
        )
    else:
        series = df.groupby(pd.Grouper(key="date_start", freq="MS")).size().reset_index(name="event_count")
    return series


def detect_anomalies(series: pd.DataFrame, window: int = 12, z_threshold: float = 2.0):
    """Flag rows where event_count is an outlier vs. its trailing rolling baseline.

    Returns the series with baseline_mean, baseline_std, z_score, and
    is_anomaly columns added.
    """
    s = series.sort_values("date_start").copy()
    s["baseline_mean"] = s["event_count"].rolling(window=window, min_periods=3).mean()
    s["baseline_std"] = s["event_count"].rolling(window=window, min_periods=3).std().fillna(0)

    # Avoid divide-by-zero: where std is 0, treat any deviation from mean as non-anomalous
    safe_std = s["baseline_std"].replace(0, pd.NA)
    s["z_score"] = ((s["event_count"] - s["baseline_mean"]) / safe_std).fillna(0)
    s["is_anomaly"] = (s["z_score"] >= z_threshold) & s["baseline_mean"].notna()

    return s
