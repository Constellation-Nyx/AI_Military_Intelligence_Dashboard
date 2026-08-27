"""
insights.py
-----------
Generates a short, plain-language summary of the CURRENTLY SELECTED data.
Rule-based / template text built entirely from numbers computed here —
no external AI calls, nothing invented.
"""

import pandas as pd
from utils.anomaly import build_monthly_series, detect_anomalies


def generate_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"text": "No events match the current filters, so no summary can be generated.", "stats": {}}

    total_events = len(df)
    start, end = df["date_start"].min().date(), df["date_start"].max().date()

    top_country = df["country"].value_counts().idxmax()
    top_country_n = df["country"].value_counts().max()

    top_region = df["region"].value_counts().idxmax()
    top_region_share = df["region"].value_counts(normalize=True).max() * 100

    dominant_type = df["violence_type_label"].value_counts().idxmax()
    dominant_type_share = df["violence_type_label"].value_counts(normalize=True).max() * 100

    total_fatalities = int(df["best"].sum())
    deadliest = df.loc[df["best"].idxmax()]

    monthly = build_monthly_series(df)
    trend_note = "insufficient data to establish a trend"
    if len(monthly) >= 4:
        midpoint = len(monthly) // 2
        first_half_avg = monthly.iloc[:midpoint]["event_count"].mean()
        second_half_avg = monthly.iloc[midpoint:]["event_count"].mean()
        if second_half_avg > first_half_avg * 1.1:
            trend_note = "an increasing trend in monthly event counts across the selected period"
        elif second_half_avg < first_half_avg * 0.9:
            trend_note = "a decreasing trend in monthly event counts across the selected period"
        else:
            trend_note = "a broadly stable level of monthly event counts across the selected period"

    anomaly_count = 0
    if len(monthly) >= 3:
        an = detect_anomalies(monthly)
        anomaly_count = int(an["is_anomaly"].sum())

    stats = {
        "total_events": total_events, "start": str(start), "end": str(end),
        "top_country": top_country, "top_country_n": int(top_country_n),
        "top_region": top_region, "top_region_share": round(top_region_share, 1),
        "dominant_type": dominant_type, "dominant_type_share": round(dominant_type_share, 1),
        "total_fatalities": total_fatalities,
        "deadliest_country": deadliest["country"],
        "deadliest_date": str(deadliest["date_start"].date()),
        "deadliest_best": int(deadliest["best"]),
        "trend_note": trend_note, "anomaly_count": anomaly_count,
    }

    text = f"""**Selected-data summary ({stats['start']} to {stats['end']})**

The current selection contains **{stats['total_events']:,} recorded events**, with a combined UCDP best-estimate of **{stats['total_fatalities']:,} fatalities**.

**{stats['top_country']}** has the highest number of recorded events in this selection ({stats['top_country_n']:,} events). At the regional level, **{stats['top_region']}** accounts for the largest share of activity ({stats['top_region_share']}% of selected events).

The dominant event category is **{stats['dominant_type']}**, making up {stats['dominant_type_share']}% of the selection.

The single highest-fatality event in this selection occurred in **{stats['deadliest_country']}** on **{stats['deadliest_date']}**, with a best estimate of **{stats['deadliest_best']:,} fatalities**.

Looking at monthly event counts, the selection shows **{stats['trend_note']}**. The Anomaly Detection method identifies **{stats['anomaly_count']} month(s)** in this selection where event counts were statistically unusual compared to their trailing baseline.

*This summary is generated entirely from statistics computed on the current filter selection. It describes historical, publicly documented events only and is not a prediction or operational assessment.*
"""
    return {"text": text, "stats": stats}
