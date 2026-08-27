# AI-Based Military Intelligence Dashboard

An AI-assisted **Streamlit multipage dashboard** for exploratory analysis of the **UCDP Georeferenced Event Dataset (GED) v26.1**. The system provides interactive geospatial analysis, country and regional analysis, violence-type classification, threat-level assessment, anomaly detection, forecasting, AI-assisted intelligence summaries, event exploration, and data export.

> **Academic Use Notice:**
> This project analyzes historical, publicly documented conflict-event records for academic and analytical purposes only. It does not collect real-time intelligence and must not be used for operational military decision-making, targeting, or other real-world military activities.

---

## Features

The dashboard provides the following capabilities:

* 🌐 **Geospatial Intelligence** — Interactive visualization of historical events using geographic coordinates.
* 🌍 **Country & Regional Analysis** — Explore event patterns and trends across countries and regions.
* 🤖 **Violence Type Prediction** — Machine-learning classification of historical events into violence categories.
* 🚨 **Threat-Level Assessment** — Analytical classification of historical events into Low, Medium, and High severity levels.
* 📈 **Anomaly Detection** — Identification of unusual historical activity compared with established baselines.
* 🔮 **Forecasting** — Exploratory forecasting of historical event-count trends.
* 🧠 **AI Intelligence** — Rule-based generation of analytical intelligence summaries.
* 🔎 **Event Investigation** — Search and inspect individual historical event records.
* 📊 **Data Explorer** — Filter, explore, and download selected data.
* 📋 **Report Generation** — Generate analytical reports from the selected dataset and dashboard findings.
* ⚙️ **Settings & Validation** — Dataset and model validation, configuration, and cache controls.

---

## Technology Stack

The application is built using:

* **Python**
* **Streamlit**
* **Pandas**
* **NumPy**
* **Plotly**
* **Scikit-learn**
* **Joblib**
* **PyDeck** *(optional)*

---

# Setup

## 1. Install Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

The UCDP GED dataset is **not included** in this repository.

---

## 2. Add the Dataset

Obtain the **UCDP Georeferenced Event Dataset (GED) v26.1** separately and place the CSV file at:

```text
data/GEDEvent_v26_1.csv
```

The application expects this file to be available before the dashboard is launched.

---

## 3. Train the Violence-Type Prediction Model

The repository contains a training script for the violence-type classification model.

Run:

```bash
python train_violence_model.py
```

This generates the required model artifacts in the `models/` directory:

```text
models/
├── violence_type_model.pkl
├── feature_encoders.pkl
└── target_encoder.pkl
```

The Streamlit application loads these trained artifacts rather than retraining the model every time the dashboard starts.

---

## 4. Run the Dashboard

Launch the application with:

```bash
streamlit run app.py
```

The dashboard will normally be available at:

```text
http://localhost:8501
```

---

## Optional PyDeck Support

The Global Threat Map can optionally use **PyDeck** for WebGL-based visualization.

Install PyDeck with:

```bash
pip install pydeck
```

If PyDeck is unavailable, the application automatically falls back to Plotly.

---

# Project Structure

```text
Military_Intelligence_Dashboard/
│
├── app.py
├── train_violence_model.py
├── requirements.txt
├── README.md
├── LICENSE
│
├── data/
│   └── GEDEvent_v26_1.csv        ← add separately
│
├── models/                       ← generated model artifacts
│   ├── violence_type_model.pkl
│   ├── feature_encoders.pkl
│   └── target_encoder.pkl
│
├── pages/
│   ├── 2_Global_Threat_Map.py
│   ├── 3_Country_Analysis.py
│   ├── 4_Violence_Type_Prediction.py
│   ├── 5_Threat_Level.py
│   ├── 6_Forecasting.py
│   ├── 7_AI_Intelligence.py
│   ├── 8_Data_Explorer.py
│   └── 9_Settings.py
│
├── tests/
│   ├── test_ml_models.py
│   └── test_anomaly_forecasting.py
│
└── utils/
    ├── __init__.py
    ├── data_loader.py
    ├── theme.py
    ├── components.py
    ├── state.py
    ├── insights.py
    ├── ml_models.py
    ├── anomaly.py
    └── forecasting.py
```

`app.py` acts as the **Home / Overview page**, so a separate `1_Home.py` file is not required.

---

# Dashboard Modules

## 1. Home — Intelligence Overview

The main dashboard provides an overall view of the selected dataset.

It displays:

* Total recorded events
* Countries represented
* Regions represented
* Relevant casualty/impact statistics
* Event trends
* Event-type distribution
* Regional highlights
* Global filtering controls

All displayed statistics are calculated from the loaded dataset rather than being hard-coded.

---

## 2. Geospatial Intelligence

Provides an interactive geographic view of historical events using latitude and longitude information from the dataset.

Features include:

* Interactive map navigation
* Country and region filtering
* Date/year filtering
* Event-type filtering
* Event-level hover information
* Automatic handling of missing coordinates
* Visualization downsampling for large datasets

### Map Performance

The application uses:

```text
DOWNSAMPLE_LIMIT = 20,000
```

When the filtered dataset exceeds this limit, a subset may be displayed for map performance.

This affects **only the map visualization**. It does not reduce the data used for analytical or machine-learning components.

---

## 3. Country & Regional Analysis

This page provides comparative analysis across countries and regions.

It includes:

* Event counts
* Historical trends
* Event categories
* Regional comparisons
* Casualty/impact statistics where supported
* Ranking tables
* Interactive visualizations

The page can be used to examine how historical activity differs across geographical areas.

---

## 4. Violence Type Prediction

The application uses a **Random Forest classifier** to classify historical event records into:

* State-based violence
* Non-state violence
* One-sided violence

The model uses contextual and event-level features available in the dataset, including:

* Country
* Region
* Month
* Year
* Event precision/clarity indicators
* Number of sources
* Casualty-related fields

The casualty fields are valid inputs for this task because the target variable is **not derived from those casualty values**.

The model uses an 80/20 train-test split.

The page provides:

* Predicted violence category
* Prediction probabilities where available
* Model performance
* Confusion matrix
* Feature importance

---

## 5. Threat-Level Assessment

Historical events are assigned analytical severity categories:

* **Low:** 0–1 deaths
* **Medium:** 2–9 deaths
* **High:** 10+ deaths

Because these labels are directly derived from the `best` casualty field, the project explicitly addresses the risk of **target leakage**.

Two Random Forest models are therefore presented:

### Leaked Model

Uses casualty-derived features, including:

* `best`
* `high`
* `low`
* Per-side death fields

This produces an inflated performance result because the model has access to information directly related to how the target label was created.

The result is shown for methodological comparison only.

### Corrected Model

Uses context-only features and excludes casualty information:

* Type of violence
* Region
* Country
* Month
* Year
* Date precision
* Location precision
* Event clarity
* Number of sources

This provides the more honest assessment of predictive performance.

The project explicitly avoids interpreting the model as a real-world operational threat predictor.

---

## 6. Anomaly Detection

The anomaly-detection module identifies **unusual historical activity** compared with an established baseline.

For example, the system can detect when the number of recorded events in a region or period is substantially different from its historical pattern.

The output is presented as:

> **Unusual historical activity detected**

and not as a prediction of a future attack.

Possible analytical methods include baseline comparisons and statistical anomaly detection.

---

## 7. Trends & Forecasting

The forecasting module analyzes historical event-count trends and provides an exploratory estimate of future values.

The current implementation uses:

**Linear Regression**

applied to the trailing 24 months of the selected data.

The page reports the trend fit's **R² value** alongside the forecast.

Forecasts are explicitly presented as **estimates based on historical trends**, not as high-confidence predictions of future real-world events.

---

## 8. AI Intelligence

The AI Intelligence page generates automated analytical summaries from the results calculated by the dashboard.

Example areas include:

* Key findings
* Regional activity
* Changes over time
* Notable patterns
* Unusual historical activity
* High-level observations

The current implementation uses **rule-based intelligence summarization** rather than requiring an external generative-AI API.

This keeps the application reproducible and allows it to operate without an API key.

The summaries are based only on information available in the loaded dataset and dashboard calculations.

---

## 9. Event Investigation

The Event Investigation functionality allows users to inspect individual historical records.

Relevant information may include:

* Date
* Country
* Region
* Location
* Conflict
* Actors
* Violence type
* Casualties
* Geographic coordinates
* Other relevant dataset fields

Users can search and filter the dataset before selecting an event for detailed inspection.

---

## 10. Data Explorer

The Data Explorer provides controlled access to the underlying records.

Available display options include:

* 100 rows
* 1,000 rows
* 5,000 rows
* All rows

Large table displays require additional confirmation.

Filtered data can be downloaded as:

* CSV
* Gzip-compressed CSV

These limits help prevent unnecessarily large browser and Streamlit payloads.

---

## 11. Report Generation

The application can generate an analytical report from the selected data and dashboard results.

Reports may include:

* Reporting period
* Dataset statistics
* Regional findings
* Threat assessment results
* Detected anomalies
* Trend/forecast information
* Model performance
* Key analytical observations
* Methodology and limitations

Generated reports are intended for **academic and analytical use only**.

---

## 12. Settings

The Settings page provides utilities for:

* Dataset validation
* Model-artifact validation
* Configuration checks
* Cache management
* Application status information

---

# Data Loading & Caching

All dashboard pages use a shared `load_data()` function located in:

```text
utils/data_loader.py
```

The dataset is loaded with Pandas and cached using:

```python
@st.cache_data
```

During loading, missing values in selected fields such as:

* `adm_1`
* `adm_2`
* `source_headline`

are replaced with:

```text
Unknown
```

This processing is disclosed within the application.

---

# Machine Learning Methodology

The project currently contains:

* Two classification approaches for threat/severity assessment
* One violence-type classification model
* Historical anomaly detection
* Exploratory forecasting

The models are designed to be **interpretable and appropriate for a student-level analytical system** rather than relying on unnecessarily complex deep-learning architectures.

Model evaluation is performed using standard metrics such as:

* Accuracy
* Macro F1
* Weighted F1
* Confusion Matrix
* Feature Importance
* R² for forecasting

Model performance should always be interpreted in the context of the dataset, feature selection, class distribution, and known limitations.

---

# Dataset

This repository does **not** include the UCDP GED dataset.

The dataset should be obtained separately from the **Uppsala Conflict Data Program (UCDP)** and placed at:

```text
data/GEDEvent_v26_1.csv
```

The dataset used by this project contains:

* **417,968 events**
* **28 columns used by the application**
* **49 columns in the raw file**
* Coverage from **1989–2025**
* **126 countries**

The dataset is used for historical and academic analytical purposes.

---

# Testing

Automated tests are included in the `tests/` directory.

Run them with:

```bash
pytest tests/
```

The tests cover areas including:

* Severity-label threshold logic
* Leakage protection for the corrected threat model
* Anomaly-detection logic
* Forecasting logic

The anomaly and forecasting tests use small synthetic datasets rather than requiring the full GED dataset.

---

# Design System

The application uses a consistent dark operations-style interface.

### `utils/theme.py`

Defines:

* Color tokens
* Typography
* Plotly styling
* Shared visual configuration

### `utils/components.py`

Provides reusable components such as:

* Page headers
* KPI cards
* Classification banners
* Threat badges
* Section labels

### `utils/state.py`

Maintains shared dashboard state, including:

* Global year range
* Region filters
* Country filters
* Forecast settings
* Prediction-confidence settings

### `utils/insights.py`

Contains the rule-based logic used to generate analytical intelligence summaries.

---

# Ethical & Analytical Limitations

This project is intended as an **academic intelligence-analysis and visualization system**.

It does not provide:

* Real-time military intelligence
* Classified information
* Target identification
* Operational military recommendations
* Attack planning
* Weapon guidance
* Reliable prediction of future military actions

Historical trends and machine-learning outputs are presented as **analytical observations and estimates** and should not be interpreted as definitive real-world predictions.

---

# Running the Project

After installing the dependencies and placing the dataset in the required location:

```bash
pip install -r requirements.txt
```

Train the violence-type model:

```bash
python train_violence_model.py
```

Launch the application:

```bash
streamlit run app.py
```

To run the test suite:

```bash
pytest tests/
```

---

# License

This project is distributed under the **Apache License 2.0**.

See [`LICENSE`](LICENSE) for the full license text.
