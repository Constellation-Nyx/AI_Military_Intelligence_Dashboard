import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from utils.data_loader import load_data
from utils.theme import inject_css, PLOTLY_TEMPLATE
from utils.components import page_header, banner, severity_badge
from utils.state import render_global_filters
from utils.ml_models import train_threat_models, prepare_severity_dataset, LEAKAGE_COLUMNS, CONTEXT_FEATURES

st.set_page_config(page_title="Threat Level · MI Dashboard", page_icon="🚨", layout="wide")
inject_css()

df = load_data()
filtered = render_global_filters(df)

page_header("🚨 Threat Level Assessment", "Severity classification of historical events — leaked vs. corrected evaluation")

banner(
    "This model classifies HISTORICAL events by severity for academic study. It is a descriptive/analytical "
    "tool, not a predictive or operational threat system.",
    kind="warning",
)

if len(filtered) < 200:
    st.warning("Select a broader set of filters (at least ~200 events) to train a meaningful model.")
    st.stop()

banner(
    "This page deliberately trains TWO versions of the model side by side: one with a data-leakage bug "
    "left in (casualty fields used to predict a casualty-derived label) and one corrected. The leaked "
    "version's near-perfect score is NOT genuine predictive skill — see the explanation below.",
    kind="danger",
)

with st.expander("ℹ️ How severity labels are defined, and what 'leakage' means here", expanded=False):
    st.markdown(f"""
- **Label** — each event is bucketed from UCDP's own `best` fatality estimate:
  `Low` (0–1), `Medium` (2–9), `High` (10+).
- **Leaked model features** — contextual features **plus** `{', '.join(LEAKAGE_COLUMNS)}`. Since these
  columns are the label's source (or near-exact components of it), the model can largely just read the
  label back off its own inputs. Its accuracy will look excellent but is not a genuine test of predictive skill.
- **Corrected model features** — only `{', '.join(CONTEXT_FEATURES)}`. No casualty information at all.
  This is the honest evaluation of how well severity can be estimated from context alone.
    """)

sample_size = st.slider(
    "Training sample size (for speed)", min_value=5000, max_value=min(100000, len(filtered)),
    value=min(30000, len(filtered)), step=5000, key="threat_sample",
)

with st.spinner("Training both models..."):
    result = train_threat_models(filtered, sample_size=sample_size)

leaked, corrected = result["leaked"], result["corrected"]

st.markdown("#### Class Distribution in Training Data")
class_df = pd.DataFrame(list(result["class_counts"].items()), columns=["Severity", "Count"])
fig0 = px.bar(class_df, x="Severity", y="Count", color="Severity",
              color_discrete_map={"Low": "#2ED573", "Medium": "#FF9F43", "High": "#FF4D4F"})
fig0.update_layout(**PLOTLY_TEMPLATE["layout"], height=280, showlegend=False)
st.plotly_chart(fig0, width="stretch")

st.markdown("### Side-by-side comparison")
col_leak, col_fix = st.columns(2)

with col_leak:
    st.markdown("##### ⛔ Leaked model (casualty fields included)")
    st.metric("Accuracy", f"{leaked['accuracy']*100:.2f}%")
    st.metric("Macro F1", f"{leaked['macro_f1']:.3f}")
    banner("This score is inflated by leakage — do not treat it as real predictive performance.", kind="danger")

with col_fix:
    st.markdown("##### ✅ Corrected model (context only)")
    st.metric("Accuracy", f"{corrected['accuracy']*100:.2f}%")
    st.metric("Macro F1", f"{corrected['macro_f1']:.3f}")
    banner("This is the honest evaluation: predicting severity from context alone, no fatality data.", kind="ok")

st.markdown("---")
tab_leak, tab_fix = st.tabs(["⛔ Leaked model details", "✅ Corrected model details"])

for tab, res, name in [(tab_leak, leaked, "leaked"), (tab_fix, corrected, "corrected")]:
    with tab:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Confusion Matrix (test set)**")
            cm, labels = res["confusion_matrix"], res["labels"]
            fig = go.Figure(data=go.Heatmap(
                z=cm, x=[f"Pred: {l}" for l in labels], y=[f"Actual: {l}" for l in labels],
                colorscale=[[0, "#121A2E"], [1, "#FF4D4F"]], showscale=True, text=cm, texttemplate="%{text}",
            ))
            fig.update_layout(**PLOTLY_TEMPLATE["layout"], height=360)
            st.plotly_chart(fig, width="stretch", key=f"cm_{name}")
        with c2:
            st.markdown("**Feature Importance**")
            fi = res["feature_importance"]
            fig2 = px.bar(fi.sort_values("importance"), x="importance", y="feature", orientation="h",
                           labels={"importance": "Importance", "feature": ""})
            fig2.update_traces(marker_color="#4C8DFF" if name == "corrected" else "#FF4D4F")
            fig2.update_layout(**PLOTLY_TEMPLATE["layout"], height=360)
            st.plotly_chart(fig2, width="stretch", key=f"fi_{name}")

        st.markdown("**Per-Class Precision / Recall / F1**")
        report_df = pd.DataFrame(res["report"]).T
        report_df = report_df.loc[[l for l in res["labels"] if l in report_df.index]]
        st.dataframe(report_df.style.format("{:.2f}"), width="stretch")

st.markdown("---")
st.markdown("#### Sample Classified Events (corrected model's labels)")
classified = prepare_severity_dataset(filtered).sample(min(15, len(filtered)), random_state=1)
show_cols = ["date_start", "country", "region", "violence_type_label", "severity", "best"]
display = classified[show_cols].rename(columns={
    "date_start": "Date", "country": "Country", "region": "Region",
    "violence_type_label": "Type", "severity": "Severity", "best": "Fatalities (best est.)",
})
display["Severity"] = display["Severity"].apply(lambda s: severity_badge(s))
st.write(display.to_html(escape=False, index=False), unsafe_allow_html=True)
