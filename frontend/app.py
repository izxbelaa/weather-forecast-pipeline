import sqlite3
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="WeatherGo Cyprus",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "weather.db"

RAIN_LABELS = {0: "Clear", 1: "Light rain", 2: "Heavy rain"}

ACTIVITY_OPTIONS = [
    "Walking 🚶",
    "Beach 🏖️",
    "Outdoor Sports ⚽",
    "Driving 🚗",
    "General outdoor activity 🌤️",
]

ACTIVITY_META = {
    "Walking 🚶": {"name": "Walking", "emoji": "🚶"},
    "Beach 🏖️": {"name": "Beach", "emoji": "🏖️"},
    "Outdoor Sports ⚽": {"name": "Outdoor Sports", "emoji": "⚽"},
    "Driving 🚗": {"name": "Driving", "emoji": "🚗"},
    "General outdoor activity 🌤️": {"name": "General outdoor activity", "emoji": "🌤️"},
}

STATUS_META = {
    "Good": {"tone": "good", "emoji": "●"},
    "Use Caution": {"tone": "caution", "emoji": "●"},
    "Not Recommended": {"tone": "risk", "emoji": "●"},
}

CONFIDENCE_COPY = {
    "High confidence":     "Conditions look stable based on recent signals.",
    "Moderate confidence": "The signal is useful, but conditions may vary.",
    "Low confidence":      "Conditions may change soon — plan with flexibility.",
    "Unavailable":         "No confidence signal available yet.",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg:        #f5f5f7;
    --surface:   #ffffff;
    --border:    #d2d2d7;
    --text:      #1d1d1f;
    --text-soft: #6e6e73;
    --text-faint:#a1a1a6;
    --good:      #1a9e6a;
    --caution:   #c07d2a;
    --risk:      #c0392b;
    --radius:    18px;
    --shadow:    0 2px 12px rgba(0,0,0,0.06);
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: var(--text) !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: var(--bg) !important;
    padding: 0 2rem 5rem !important;
    max-width: 1100px;
    margin: 0 auto;
}

[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

h1,h2,h3,h4,p,div,span,label {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* Selectbox */
[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 0.95rem !important;
    min-height: 44px !important;
    box-shadow: none !important;
}

/* Radio */
[data-testid="stRadio"] > div {
    gap: 0.4rem;
    flex-direction: row;
}
[data-testid="stRadio"] label {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.3rem 0.85rem;
    font-size: 0.88rem;
    color: var(--text-soft);
    cursor: pointer;
}

/* Charts */
[data-testid="stArrowVegaLiteChart"],
[data-testid="stVegaLiteChart"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.5rem;
    box-shadow: var(--shadow);
}

/* Tabs */
[data-baseweb="tab-list"] {
    gap: 0 !important;
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 999px !important;
    padding: 4px !important;
    width: fit-content !important;
    margin-bottom: 2rem !important;
}
[data-baseweb="tab"] {
    border-radius: 999px !important;
    border: none !important;
    background: transparent !important;
    color: var(--text-soft) !important;
    padding: 0.4rem 1.1rem !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: var(--text) !important;
    color: white !important;
}

/* ── Components ── */

.wg-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem 0 0.5rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.wg-nav-brand {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.01em;
}
.wg-nav-sub {
    font-size: 0.82rem;
    color: var(--text-faint);
}

.wg-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
}

.wg-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-faint);
}

/* Hero / recommendation */
.wg-hero-card {
    padding: 2.5rem 2.5rem 2rem;
    margin-bottom: 1rem;
}
.wg-hero-city {
    font-size: 0.9rem;
    font-weight: 500;
    color: var(--text-soft);
    margin-bottom: 0.75rem;
}
.wg-hero-status {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--text);
    margin-bottom: 0.7rem;
}
.wg-hero-status .dot-good    { color: var(--good); }
.wg-hero-status .dot-caution { color: var(--caution); }
.wg-hero-status .dot-risk    { color: var(--risk); }
.wg-hero-message {
    font-size: 1rem;
    color: var(--text-soft);
    line-height: 1.6;
    max-width: 38rem;
    margin-bottom: 1.25rem;
}
.wg-reason-block {
    display: grid;
    grid-template-columns: minmax(0, 1.2fr) minmax(240px, 0.8fr);
    gap: 1rem;
    margin: 1rem 0 1.25rem;
}
.wg-reason-panel {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1rem;
}
.wg-reason-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.45rem;
}
.wg-reason-list {
    margin: 0;
    padding-left: 1.1rem;
    color: var(--text-soft);
    line-height: 1.6;
    font-size: 0.9rem;
}
.wg-suggestion {
    color: var(--text);
    font-size: 0.92rem;
    line-height: 1.55;
}
.wg-better-city {
    margin-top: 0.7rem;
    color: var(--good);
    font-weight: 600;
}
.wg-pills {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.wg-pill {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.3rem 0.75rem;
    font-size: 0.8rem;
    color: var(--text-soft);
}
.wg-confidence-chip {
    display: inline-flex;
    align-items: baseline;
    gap: 0.35rem;
    border-radius: 999px;
    padding: 0.24rem 0.62rem;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid transparent;
}
.wg-confidence-chip.good {
    color: var(--good);
    background: rgba(26,158,106,0.08);
    border-color: rgba(26,158,106,0.2);
}
.wg-confidence-chip.caution {
    color: var(--caution);
    background: rgba(192,125,42,0.08);
    border-color: rgba(192,125,42,0.2);
}
.wg-confidence-chip.risk {
    color: var(--risk);
    background: rgba(192,57,43,0.08);
    border-color: rgba(192,57,43,0.2);
}
.wg-confidence-percent {
    color: var(--text-faint);
    font-size: 0.72rem;
    font-weight: 500;
}
.wg-confidence-note,
.wg-city-confidence {
    color: var(--text-faint);
    font-size: 0.76rem;
    line-height: 1.45;
}
.wg-confidence-note {
    margin-top: 0.5rem;
}
.wg-city-confidence {
    margin-top: 0.35rem;
}

/* Support block */
.wg-support-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: 1rem;
}
.wg-support-item {
    background: var(--surface);
    padding: 1.2rem 1.3rem;
}
.wg-support-value {
    margin-top: 0.35rem;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text);
}

/* Summary cards */
.wg-summary-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1rem;
}
.wg-summary-card {
    padding: 1.5rem;
}
.wg-summary-value {
    margin-top: 0.5rem;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    color: var(--text);
}
.wg-summary-copy {
    margin-top: 0.3rem;
    font-size: 0.85rem;
    color: var(--text-soft);
    line-height: 1.5;
}

/* Conditions strip */
.wg-strip {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    margin-bottom: 1rem;
}
.wg-strip-item {
    background: var(--surface);
    padding: 1.1rem 1rem;
}
.wg-strip-value {
    margin-top: 0.35rem;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text);
}
.wg-strip-sub {
    margin-top: 0.15rem;
    font-size: 0.75rem;
    color: var(--text-faint);
}

/* Trend cards */
.wg-trend-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
}
.wg-trend-card {
    padding: 1.4rem 1.5rem;
}
.wg-trend-title {
    margin-top: 0.3rem;
    font-size: 1.05rem;
    font-weight: 600;
    color: var(--text);
}
.wg-trend-copy {
    margin-top: 0.25rem;
    font-size: 0.85rem;
    color: var(--text-soft);
    line-height: 1.5;
}

/* Section heading */
.wg-section-head {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-faint);
    margin: 1.75rem 0 0.75rem;
}

/* Controls */
.wg-control-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--text-faint);
    margin-bottom: 0.4rem;
}
.wg-control-hint {
    font-size: 0.8rem;
    color: var(--text-faint);
    margin-top: 0.3rem;
}

/* City comparison */
.wg-compare-header {
    padding: 1.75rem 2rem 1.5rem;
    margin-bottom: 1rem;
}
.wg-compare-headline {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--text);
    margin-top: 0.3rem;
}
.wg-compare-sub {
    font-size: 0.9rem;
    color: var(--text-soft);
    margin-top: 0.35rem;
    line-height: 1.55;
}

.wg-city-list { display: grid; gap: 0.75rem; margin-bottom: 1rem; }

.wg-city-row {
    display: grid;
    grid-template-columns: minmax(220px, 2fr) minmax(100px, 1fr) minmax(110px, 1fr) minmax(130px, 1.2fr);
    gap: 1.5rem;
    align-items: center;
    padding: 1.25rem 1.5rem;
}
.wg-city-row.featured { border-color: rgba(26,158,106,0.3); }
.wg-city-row.warn     { border-color: rgba(192,57,43,0.25); }

.wg-city-main {
    display: flex;
    align-items: center;
    gap: 1rem;
}
.wg-city-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    background: var(--bg);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
}
.wg-city-name {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
}
.wg-city-takeaway {
    font-size: 0.82rem;
    color: var(--text-soft);
    margin-top: 0.2rem;
    line-height: 1.4;
}
.wg-badge {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 0.18rem 0.55rem;
    font-size: 0.7rem;
    font-weight: 600;
    margin-top: 0.3rem;
    border: 1px solid transparent;
}
.wg-badge.good    { color:var(--good);    background:rgba(26,158,106,0.08); border-color:rgba(26,158,106,0.2); }
.wg-badge.caution { color:var(--caution); background:rgba(192,125,42,0.08); border-color:rgba(192,125,42,0.2); }
.wg-badge.risk    { color:var(--risk);    background:rgba(192,57,43,0.08);  border-color:rgba(192,57,43,0.2); }

.wg-city-metric-label {
    font-size: 0.7rem;
    color: var(--text-faint);
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin-bottom: 0.2rem;
}
.wg-city-metric-value {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
}
.wg-conf-track {
    width: 100%; max-width: 100px; height: 6px;
    background: var(--bg);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 0.35rem;
}
.wg-conf-fill {
    height: 100%;
    border-radius: 999px;
}
.wg-conf-label {
    font-size: 0.75rem;
    color: var(--text-faint);
    margin-top: 0.25rem;
}

/* About */
.wg-about-card {
    padding: 2rem 2.5rem;
    margin-bottom: 1rem;
}
.wg-about-card h2 {
    font-size: 1.3rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin: 0 0 0.5rem;
}
.wg-about-card p {
    font-size: 0.92rem;
    color: var(--text-soft);
    line-height: 1.7;
    margin: 0.5rem 0;
}

.wg-footer {
    text-align: center;
    font-size: 0.75rem;
    color: var(--text-faint);
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 2rem 0 1rem;
}

@media (max-width: 900px) {
    .wg-support-grid,
    .wg-summary-row,
    .wg-trend-row,
    .wg-reason-block { grid-template-columns: 1fr 1fr; }
    .wg-strip      { grid-template-columns: repeat(3, 1fr); }
    .wg-city-row   { grid-template-columns: 1fr; gap: 0.75rem; }
}
@media (max-width: 600px) {
    [data-testid="stAppViewContainer"] > .main { padding: 0 1rem 4rem !important; }
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 100% !important;
        min-width: 100% !important;
    }
    .wg-hero-card   { padding: 1.5rem; }
    .wg-support-grid,
    .wg-summary-row,
    .wg-reason-block { grid-template-columns: 1fr; }
    .wg-strip        { grid-template-columns: repeat(2, 1fr); }
    .wg-trend-row    { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────

def render_html(html: str) -> None:
    cleaned = "\n".join(line.lstrip() for line in dedent(html).splitlines()).strip()
    st.markdown(cleaned, unsafe_allow_html=True)

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_cities():
    conn = get_connection()
    df = pd.read_sql_query("SELECT DISTINCT city FROM weather_data ORDER BY city", conn)
    conn.close()
    return df["city"].tolist()

def load_weather_data(city, hours=24):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM weather_data WHERE city = ? ORDER BY timestamp DESC LIMIT ?",
        conn, params=(city, hours),
    )
    conn.close()
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp").reset_index(drop=True)

def load_latest_prediction(city):
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT p.*, w.city, w.timestamp AS weather_timestamp
           FROM predictions p
           JOIN weather_data w ON p.weather_data_id = w.id
           WHERE w.city = ?
           ORDER BY p.created_at DESC LIMIT 1""",
        conn, params=(city,),
    )
    conn.close()
    if not df.empty:
        df["weather_timestamp"] = pd.to_datetime(df["weather_timestamp"])
        df["created_at"]        = pd.to_datetime(df["created_at"])
    return df

def load_all_predictions():
    conn = get_connection()
    df = pd.read_sql_query(
        """SELECT p.*, w.city, w.timestamp AS weather_timestamp
           FROM predictions p
           JOIN weather_data w ON p.weather_data_id = w.id
           ORDER BY p.created_at DESC""",
        conn,
    )
    conn.close()
    if not df.empty:
        df["weather_timestamp"] = pd.to_datetime(df["weather_timestamp"])
        df["created_at"]        = pd.to_datetime(df["created_at"])
    return df

def load_latest_weather_by_city():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT w.*
        FROM weather_data w
        JOIN (
            SELECT city, MAX(timestamp) AS latest_timestamp
            FROM weather_data
            GROUP BY city
        ) latest
            ON w.city = latest.city
           AND w.timestamp = latest.latest_timestamp
        """,
        conn,
    )
    conn.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df

def get_confidence_band(prob):
    if prob is None:   return "Unavailable"
    if prob >= 75:     return "High confidence"
    if prob >= 50:     return "Moderate confidence"
    return "Low confidence"

def get_confidence_short(prob):
    return get_confidence_band(prob).replace(" confidence", "").replace("Unavailable", "Unavailable")

def get_confidence_metric_label(rain_label):
    return "No Rain confidence" if rain_label == "Clear" else "Forecast confidence"

def get_confidence_tone(prob):
    if prob is None:
        return "caution"
    if prob >= 75:
        return "good"
    if prob >= 50:
        return "caution"
    return "risk"

def confidence_chip(prob, label="Confidence"):
    confidence_text = get_confidence_short(prob)
    tone = get_confidence_tone(prob)
    percent = f'<span class="wg-confidence-percent">({int(prob)}%)</span>' if prob is not None else ""
    return f'<span class="wg-confidence-chip {tone}">{label}: {confidence_text} {percent}</span>'

def get_confidence_guidance(prob):
    if prob is None:
        return "Confidence reflects how consistent recent signals are. It is not a guarantee."
    if prob >= 75:
        return "Conditions look stable based on recent signals. This is not a guarantee."
    if prob >= 50:
        return "The signal is moderate, so keep a little flexibility in your plan."
    return "Conditions may change soon — plan with flexibility."

def get_risk_level(rain_label, confidence):
    if rain_label == "Heavy rain":                            return "High"
    if rain_label == "Light rain" and confidence >= 60:       return "Medium"
    if rain_label == "Light rain":                            return "Low-Medium"
    return "Low"

def get_outdoor_suitability(rain_label, confidence, wind_speed):
    if rain_label == "Heavy rain":                            return "Not Recommended"
    if rain_label == "Light rain" and confidence >= 60:       return "Use Caution"
    if wind_speed >= 25:                                      return "Use Caution"
    return "Good"

def get_recommendation_status(suitability, risk):
    if suitability == "Not Recommended" or risk == "High":    return "Not Recommended"
    if suitability == "Use Caution" or risk in {"Medium","Low-Medium"}: return "Use Caution"
    return "Good"

def generate_decision_message(rain_label, confidence, temp, wind_speed):
    if rain_label == "Heavy rain":
        return "Rain risk is high. Outdoor plans are not recommended right now."
    if rain_label == "Light rain" and confidence >= 60:
        return "Light rain is likely. Consider carrying an umbrella."
    if wind_speed >= 25:
        return "Wind is picking up, but conditions are still manageable."
    if temp >= 30:
        return "Conditions are stable. Good time to head out — stay hydrated in the heat."
    return "Conditions look good. A comfortable time for outdoor activity."

def status_priority(status):
    return {"Good": 0, "Use Caution": 1, "Not Recommended": 2}.get(status, 1)

def max_status(*statuses):
    return max(statuses, key=status_priority)

def evaluate_activity(activity, rain_label, confidence, temp, wind_speed):
    confidence = 0 if confidence is None else float(confidence)
    temp = 0 if temp is None else float(temp)
    wind_speed = 0 if wind_speed is None else float(wind_speed)
    rain_expected = rain_label in {"Light rain", "Heavy rain"}
    activity_name = ACTIVITY_META[activity]["name"]

    status = "Good"
    reasons = []

    if activity == "Walking 🚶":
        if rain_label == "Heavy rain":
            status = "Not Recommended"
            reasons.append(f"Heavy rain expected with {get_confidence_short(confidence).lower()} confidence")
        if rain_label == "Light rain" and confidence >= 60:
            status = max_status(status, "Use Caution")
            reasons.append(f"Light rain likely with {get_confidence_short(confidence).lower()} confidence")
        if wind_speed > 25:
            status = max_status(status, "Use Caution")
            reasons.append(f"Wind speed is high ({wind_speed:.0f} km/h)")

    elif activity == "Beach 🏖️":
        if temp < 24:
            status = "Not Recommended"
            reasons.append(f"Temperature is below beach comfort ({temp:.1f}°C)")
        if wind_speed > 20:
            status = max_status(status, "Use Caution")
            reasons.append(f"Wind may be uncomfortable at the beach ({wind_speed:.0f} km/h)")
        if rain_expected:
            status = "Not Recommended"
            reasons.append(f"{rain_label} expected with {get_confidence_short(confidence).lower()} confidence")

    elif activity == "Outdoor Sports ⚽":
        if wind_speed > 25:
            status = "Not Recommended"
            reasons.append(f"Wind speed is high ({wind_speed:.0f} km/h)")
        if rain_expected:
            status = max_status(status, "Use Caution")
            reasons.append(f"{rain_label} expected with {get_confidence_short(confidence).lower()} confidence")

    elif activity == "Driving 🚗":
        if rain_label == "Heavy rain":
            status = "Use Caution"
            reasons.append(f"Heavy rain may reduce visibility")
        if rain_expected and confidence > 75:
            status = max_status(status, "Use Caution")
            reasons.append("Strong signal for rain")

    else:
        suitability = get_outdoor_suitability(rain_label, confidence, wind_speed)
        status = {
            "Good": "Good",
            "Use Caution": "Use Caution",
            "Not Recommended": "Not Recommended",
        }.get(suitability, "Use Caution")
        if rain_label == "Heavy rain":
            reasons.append(f"Heavy rain expected with {get_confidence_short(confidence).lower()} confidence")
        elif rain_label == "Light rain" and confidence >= 60:
            reasons.append(f"Light rain likely with {get_confidence_short(confidence).lower()} confidence")
        if wind_speed >= 25:
            reasons.append(f"Wind speed is high ({wind_speed:.0f} km/h)")

    if not reasons:
        reasons.append(f"Conditions fit {activity_name.lower()} right now")

    suggestion = (
        f"Good conditions for {activity_name.lower()}. You can continue with your plan."
        if status == "Good"
        else f"Consider switching activity or choosing another city for {activity_name.lower()}."
    )

    return {
        "status": status,
        "reasons": reasons,
        "suggestion": suggestion,
        "confidence_label": get_confidence_short(confidence),
    }

def add_trend_columns(df):
    out = df.copy()
    out["temp_change_1h"] = out["temperature_2m"].diff()
    out["rain_change_1h"] = out["precipitation"].diff()
    return out

def summarize_trends(df):
    if len(df) < 2:
        return "Stable", "Stable", 0.0, 0.0
    temp_diff = df["temperature_2m"].iloc[-1] - df["temperature_2m"].iloc[0]
    rain_diff = df["precipitation"].iloc[-1]   - df["precipitation"].iloc[0]
    temp_text = (f"Rising {temp_diff:.1f}°C"   if temp_diff > 0.5
                 else f"Falling {abs(temp_diff):.1f}°C" if temp_diff < -0.5
                 else "Holding steady")
    rain_text = (f"Increasing {rain_diff:.1f} mm" if rain_diff > 0.1
                 else f"Easing {abs(rain_diff):.1f} mm" if rain_diff < -0.1
                 else "Remaining stable")
    return temp_text, rain_text, temp_diff, rain_diff

def get_temp_trend_note(diff):
    if diff > 0.5:  return "Temperature is rising over the selected period."
    if diff < -0.5: return "Temperature is easing down over the selected period."
    return "Temperature has remained relatively stable."

def get_rain_trend_note(diff):
    if diff > 0.1:  return "Precipitation is increasing slightly."
    if diff < -0.1: return "Rain intensity is easing."
    return "Rain signal remains stable."

def build_city_ranking_table(all_preds, latest_weather, activity):
    if all_preds.empty:
        return all_preds
    latest = (
        all_preds.sort_values("created_at", ascending=False)
        .groupby("city", as_index=False).head(1).copy()
    )
    if not latest_weather.empty:
        latest = latest.merge(
            latest_weather[
                [
                    "city",
                    "temperature_2m",
                    "wind_speed_10m",
                    "precipitation",
                    "timestamp",
                ]
            ],
            on="city",
            how="left",
        )
    latest["Rain"]       = latest["rain_prediction"].map(RAIN_LABELS)
    latest["Confidence"] = latest["rain_probability"].round(0).astype(int)
    latest["Temp"]       = latest["predicted_temperature"].round(1)
    latest["Wind"]       = latest["wind_speed_10m"].fillna(0).round(1)
    latest["Current Temp"] = latest["temperature_2m"].fillna(latest["Temp"]).round(1)
    decisions = latest.apply(
        lambda r: evaluate_activity(
            activity,
            r["Rain"],
            r["rain_probability"],
            r["Temp"],
            r["Wind"],
        ),
        axis=1,
    )
    latest["Recommendation"] = decisions.apply(lambda decision: decision["status"])
    latest["Suitability"] = latest["Recommendation"]
    latest["Decision Reason"] = decisions.apply(lambda decision: decision["reasons"][0])
    def score(row):
        return (
            status_priority(row["Recommendation"]) * 10
            + row["rain_probability"] / 100
            + row["Wind"] / 1000
        )
    latest["_score"] = latest.apply(score, axis=1)
    latest = latest.sort_values(["_score","city"]).reset_index(drop=True)
    latest["Rank"]            = range(1, len(latest)+1)
    latest["Confidence Band"] = latest["rain_probability"].apply(get_confidence_band)
    return latest

def weather_icon(rain_label):
    return {"Clear":"☀️","Light rain":"🌦️","Heavy rain":"🌧️"}.get(rain_label,"⛅")

def city_takeaway(row, best, worst):
    if row["city"] == best:  return "Best match for the selected activity."
    if row["city"] == worst: return "Weakest match for the selected activity."
    return row.get("Decision Reason", "Conditions look relatively steady.")

def conf_color(v):
    if v >= 75: return "var(--good)"
    if v >= 50: return "var(--caution)"
    return "var(--risk)"

def rec_tone(rec):
    return {"Good":"good","Use Caution":"caution","Not Recommended":"risk"}.get(rec,"caution")


# ── Data load ─────────────────────────────────────────────────────────────────

if not DB_PATH.exists():
    st.error(f"Database not found at: {DB_PATH}")
    st.stop()

cities = load_cities()
if not cities:
    st.error("No weather data found. Run the data collector first.")
    st.stop()

all_predictions_df = load_all_predictions()
latest_weather_df = load_latest_weather_by_city()


# ── Nav ───────────────────────────────────────────────────────────────────────

render_html("""
<div class="wg-nav">
    <div class="wg-nav-brand">WeatherGo Cyprus</div>
    <div class="wg-nav-sub">Activity decisions for Cyprus</div>
</div>
""")


# ── Controls ──────────────────────────────────────────────────────────────────

col_activity, col_city, col_time = st.columns([1.5, 1.4, 1])
with col_activity:
    render_html('<div class="wg-control-label">What are you planning?</div>')
    activity = st.selectbox(
        "What are you planning?",
        ACTIVITY_OPTIONS,
        key="activity_selector",
        label_visibility="collapsed",
        help="Choose the activity so the recommendation can match your plan.",
    )
    render_html('<div class="wg-control-hint">Recommendations adapt to the activity.</div>')

with col_city:
    render_html('<div class="wg-control-label">City</div>')
    city = st.selectbox(
        "City", cities, key="city_selector", label_visibility="collapsed",
        help="Choose a Cyprus city to view its current recommendation.",
    )
    render_html('<div class="wg-control-hint">Choose a city to view its current recommendation.</div>')

with col_time:
    render_html('<div class="wg-control-label">Time window</div>')
    time_window = st.radio(
        "Time window", ["12 h","24 h"], horizontal=True, label_visibility="collapsed",
    )
    render_html('<div class="wg-control-hint">Recent period for trend and charts.</div>')

ranking_df = build_city_ranking_table(all_predictions_df, latest_weather_df, activity)
best_city = ranking_df.iloc[0]["city"] if not ranking_df.empty else None
worst_city = ranking_df.iloc[-1]["city"] if not ranking_df.empty else None

hours_to_load = 12 if time_window == "12 h" else 24

weather_df    = load_weather_data(city, hours=hours_to_load)
prediction_df = load_latest_prediction(city)

if weather_df.empty:
    st.error(f"No data for {city}.")
    st.stop()

weather_df = add_trend_columns(weather_df)
latest     = weather_df.iloc[-1]
last_update_text = pd.to_datetime(latest["timestamp"]).strftime("%d %b, %H:%M")

predicted_temp       = None
predicted_prob       = None
predicted_rain_label = "Unavailable"
prediction_time_text = "Pending"

if not prediction_df.empty:
    pred = prediction_df.iloc[0]
    predicted_temp       = float(pred["predicted_temperature"])
    predicted_prob       = float(pred["rain_probability"])
    predicted_rain_label = RAIN_LABELS.get(int(pred["rain_prediction"]), "Unavailable")
    prediction_time_text = pd.to_datetime(pred["created_at"]).strftime("%H:%M")

confidence_band  = get_confidence_band(predicted_prob)
confidence_metric_label = get_confidence_metric_label(predicted_rain_label)
confidence_html = confidence_chip(predicted_prob)
forecast_confidence_html = confidence_chip(predicted_prob, confidence_metric_label)
confidence_guidance = get_confidence_guidance(predicted_prob)
activity_decision = evaluate_activity(
    activity,
    predicted_rain_label,
    predicted_prob,
    predicted_temp if predicted_temp is not None else float(latest["temperature_2m"]),
    float(latest["wind_speed_10m"]),
) if predicted_prob is not None else {
    "status": "Use Caution",
    "reasons": ["Short-term prediction is not available yet"],
    "suggestion": "Use the current readings below and keep plans flexible.",
    "confidence_label": "Unavailable",
}
decision_status = activity_decision["status"]
decision_reasons = activity_decision["reasons"]
decision_suggestion = activity_decision["suggestion"]
activity_name = ACTIVITY_META[activity]["name"]
activity_emoji = ACTIVITY_META[activity]["emoji"]
decision_message = f"{activity_emoji} Activity: {activity_name}. {confidence_guidance}"
better_city = None
if decision_status != "Good" and not ranking_df.empty:
    better_matches = ranking_df[
        (ranking_df["city"] != city) & (ranking_df["Recommendation"] == "Good")
    ]
    if not better_matches.empty:
        better_city = better_matches.iloc[0]["city"]

temp_trend_text, rain_trend_text, temp_diff, rain_diff = summarize_trends(weather_df)
status_tone = STATUS_META[decision_status]["tone"]


# ── Tabs ──────────────────────────────────────────────────────────────────────

tab_main, tab_compare, tab_about = st.tabs(["Overview", "Across Cyprus", "About"])


# ── Tab: Overview ─────────────────────────────────────────────────────────────

with tab_main:

    # Hero recommendation
    reasons_html = "".join(f"<li>{reason}</li>" for reason in decision_reasons)
    better_city_html = (
        f'<div class="wg-better-city">👉 Better option right now: {better_city} '
        f'(Good conditions for {activity_name.lower()})</div>'
        if better_city
        else ""
    )
    render_html(f"""
    <div class="wg-card wg-hero-card">
        <div class="wg-hero-city">{city} &nbsp;·&nbsp; {activity_emoji} {activity_name} &nbsp;·&nbsp; Updated {last_update_text}</div>
        <div class="wg-hero-status">
            <span class="dot-{status_tone}">●</span> Recommendation: {decision_status}
        </div>
        <div class="wg-hero-message">{decision_message}</div>
        <div class="wg-reason-block">
            <div class="wg-reason-panel">
                <div class="wg-reason-title">Reason</div>
                <ul class="wg-reason-list">{reasons_html}</ul>
            </div>
            <div class="wg-reason-panel">
                <div class="wg-reason-title">Suggestion</div>
                <div class="wg-suggestion">👉 {decision_suggestion}</div>
                {better_city_html}
            </div>
        </div>
        <div class="wg-pills">
            <div class="wg-pill">Activity: {activity_emoji} {activity_name}</div>
            <div class="wg-pill">Outlook: {predicted_rain_label}</div>
            <div class="wg-pill">Wind: {latest["wind_speed_10m"]:.1f} km/h</div>
        </div>
        <div class="wg-confidence-note">Confidence reflects how consistent recent signals are. It is not a guarantee.</div>
    </div>
    """)

   
    # Prediction summary cards
    render_html('<div class="wg-section-head">Prediction</div>')
    render_html(f"""
    <div class="wg-summary-row">
        <div class="wg-card wg-summary-card">
            <div class="wg-label">Temperature</div>
            <div class="wg-summary-value">{f"{predicted_temp:.1f}°C" if predicted_temp else "—"}</div>
            <div class="wg-summary-copy">Expected temperature over the next hour.</div>
        </div>
        <div class="wg-card wg-summary-card">
            <div class="wg-label">Rain outlook</div>
            <div class="wg-summary-value">{predicted_rain_label}</div>
            <div class="wg-summary-copy">Short-term precipitation forecast.</div>
        </div>
        <div class="wg-card wg-summary-card">
            <div class="wg-label">Confidence</div>
            <div class="wg-summary-value">{get_confidence_short(predicted_prob)}</div>
            <div class="wg-summary-copy">{CONFIDENCE_COPY[confidence_band]} {f"Signal strength: {int(predicted_prob)}%." if predicted_prob is not None else ""}</div>
        </div>
    </div>
    """)

    # Current conditions strip
    render_html('<div class="wg-section-head">Current conditions</div>')
    render_html(f"""
    <div class="wg-strip">
        <div class="wg-strip-item">
            <div class="wg-label">Temp</div>
            <div class="wg-strip-value">{latest['temperature_2m']:.1f}°C</div>
            <div class="wg-strip-sub">Current reading</div>
        </div>
        <div class="wg-strip-item">
            <div class="wg-label">Humidity</div>
            <div class="wg-strip-value">{int(latest['relative_humidity_2m'])}%</div>
            <div class="wg-strip-sub">Air moisture</div>
        </div>
        <div class="wg-strip-item">
            <div class="wg-label">Wind</div>
            <div class="wg-strip-value">{latest['wind_speed_10m']:.1f} km/h</div>
            <div class="wg-strip-sub">Surface wind</div>
        </div>
        <div class="wg-strip-item">
            <div class="wg-label">Rain</div>
            <div class="wg-strip-value">{latest['precipitation']:.1f} mm</div>
            <div class="wg-strip-sub">Recent precipitation</div>
        </div>
        <div class="wg-strip-item">
            <div class="wg-label">Cloud</div>
            <div class="wg-strip-value">{int(latest['cloud_cover'])}%</div>
            <div class="wg-strip-sub">Sky coverage</div>
        </div>
        <div class="wg-strip-item">
            <div class="wg-label">Pressure</div>
            <div class="wg-strip-value">{latest['pressure_msl']:.0f}</div>
            <div class="wg-strip-sub">hPa</div>
        </div>
    </div>
    """)

    # Trend insight
    render_html('<div class="wg-section-head">Trends</div>')
    render_html(f"""
    <div class="wg-trend-row">
        <div class="wg-card wg-trend-card">
            <div class="wg-label">Temperature trend</div>
            <div class="wg-trend-title">{temp_trend_text}</div>
            <div class="wg-trend-copy">{get_temp_trend_note(temp_diff)}</div>
        </div>
        <div class="wg-card wg-trend-card">
            <div class="wg-label">Rain trend</div>
            <div class="wg-trend-title">{rain_trend_text}</div>
            <div class="wg-trend-copy">{get_rain_trend_note(rain_diff)}</div>
        </div>
    </div>
    """)

    # Charts
    indexed_df = weather_df.set_index("timestamp")
    chart_col_1, chart_col_2 = st.columns(2)
    with chart_col_1:
        st.caption("Temperature over selected period")
        st.area_chart(indexed_df[["temperature_2m"]], color=["#4a90d9"], height=200, width="stretch")
    with chart_col_2:
        st.caption("Precipitation over selected period")
        st.area_chart(indexed_df[["precipitation"]], color=["#5aab8c"], height=200, width="stretch")


# ── Tab: Across Cyprus ────────────────────────────────────────────────────────

with tab_compare:

    takeaway_sentence = (
        f"Right now, {best_city} is the best option for {activity_name.lower()}."
        if best_city else "City outlooks will appear here once data is available."
    )

    render_html(f"""
    <div class="wg-card wg-compare-header">
        <div class="wg-label">{activity_emoji} Activity-aware city comparison</div>
        <div class="wg-compare-headline">Where should you go for {activity_name.lower()}?</div>
        <div class="wg-compare-sub">{takeaway_sentence}</div>
    </div>
    """)

    if ranking_df.empty:
        st.info("No cross-city data available yet.")
    else:
        rows_html = ""
        for _, row in ranking_df.iterrows():
            extra_class = ""
            badge       = ""
            if row["city"] == best_city:
                extra_class = " featured"
                badge = f'<span class="wg-badge good">Best for {activity_name.lower()}</span>'
            elif row["city"] == worst_city:
                extra_class = " warn"
                badge = '<span class="wg-badge risk">Weakest match</span>'
            elif row["Recommendation"] == "Use Caution":
                badge = '<span class="wg-badge caution">Use caution</span>'

            tone = rec_tone(row["Recommendation"])
            tk   = city_takeaway(row, best_city, worst_city)
            city_confidence_html = confidence_chip(row["Confidence"])

            rows_html += f"""
            <div class="wg-card wg-city-row{extra_class}">
                <div class="wg-city-main">
                    <div class="wg-city-icon">{weather_icon(row["Rain"])}</div>
                    <div>
                        <div class="wg-city-name">{row["city"]}</div>
                        {badge}
                        <div class="wg-city-takeaway">{tk}</div>
                        <div class="wg-city-confidence">{city_confidence_html}</div>
                    </div>
                </div>
                <div>
                    <div class="wg-city-metric-label">Activity fit</div>
                    <div class="wg-city-metric-value" style="color:var(--{tone});">{row["Recommendation"]}</div>
                </div>
                <div>
                    <div class="wg-city-metric-label">Rain outlook</div>
                    <div class="wg-city-metric-value">{row["Rain"]}</div>
                </div>
                <div>
                    <div class="wg-city-metric-label">Wind / Temp</div>
                    <div class="wg-city-metric-value">{row["Wind"]:.1f} km/h · {row["Temp"]:.1f}°C</div>
                </div>
            </div>
            """
        render_html(f'<div class="wg-city-list">{rows_html}</div>')


# ── Tab: About ────────────────────────────────────────────────────────────────

with tab_about:
    render_html("""
    <div class="wg-card wg-about-card">
        <h2>Decision assistant weather dashboard</h2>
        <p>WeatherGo Cyprus starts with what you want to do, then translates rain, wind, temperature into a practical recommendation.</p>
    </div>
    """)


# ── Footer ────────────────────────────────────────────────────────────────────

render_html('<div class="wg-footer">WeatherGo Cyprus</div>')