"""
forecasting.py
--------------
Very simple historical trend extrapolation for monthly event counts.
This is explicitly an ESTIMATE based on past trend + linear regression —
not a prediction of future attacks or operational guidance.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


def forecast_counts(monthly_series: pd.DataFrame, periods_ahead: int = 6, trend_window: int = 24):
    """Fit a simple linear trend on RECENT monthly event counts and extrapolate.

    Only the trailing `trend_window` months (default 24, or the full series if
    shorter) are used to fit the trend line. This keeps the estimate anchored
    to recent behavior rather than letting an old, unrelated spike decades ago
    dominate the extrapolation -- still a simple, explainable linear model,
    just fit on the relevant recent window.

    monthly_series must have columns: date_start (Timestamp, monthly), event_count.
    Returns a dataframe with both historical and forecast rows, plus a
    'kind' column ('historical' / 'forecast').
    """
    s = monthly_series.sort_values("date_start").reset_index(drop=True)
    s["t"] = np.arange(len(s))

    fit_window = s.tail(min(trend_window, len(s))).copy()

    model = LinearRegression()
    model.fit(fit_window[["t"]], fit_window["event_count"])

    future_t = np.arange(len(s), len(s) + periods_ahead)
    future_dates = pd.date_range(
        s["date_start"].max() + pd.offsets.MonthBegin(1), periods=periods_ahead, freq="MS"
    )
    future_t_df = pd.DataFrame({"t": future_t})
    future_pred = model.predict(future_t_df)
    future_pred = np.clip(future_pred, a_min=0, a_max=None)

    hist = s[["date_start", "event_count"]].copy()
    hist["kind"] = "historical"

    fut = pd.DataFrame({"date_start": future_dates, "event_count": future_pred})
    fut["kind"] = "forecast"

    combined = pd.concat([hist, fut], ignore_index=True)
    slope = float(model.coef_[0])
    r2 = float(r2_score(fit_window["event_count"], model.predict(fit_window[["t"]])))
    trend_direction = "increasing" if slope > 0.5 else ("decreasing" if slope < -0.5 else "roughly flat")

    return combined, trend_direction, slope, r2
