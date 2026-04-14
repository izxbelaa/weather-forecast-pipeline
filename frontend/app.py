import sqlite3
from pathlib import Path
from textwrap import dedent

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="WeatherGo Cyprus",
    page_icon="W",
    layout="wide",
    initial_sidebar_state="expanded",
)


DB_PATH = Path(__file__).resolve().parent.parent / "database" / "weather.db"

RAIN_LABELS = {
    0: "Clear",
    1: "Light rain",
    2: "Heavy rain",
}

STATUS_META = {
    "Safe to go out": {"tone": "good", "emoji": "🌤️"},
    "Use caution": {"tone": "caution", "emoji": "🌦️"},
    "Stay indoors": {"tone": "risk", "emoji": "🌧️"},
}

SUITABILITY_COLOR = {
    "Good": "var(--good)",
    "Use Caution": "var(--caution)",
    "Not Recommended": "var(--risk)",
    "Unknown": "var(--muted)",
}

RISK_COLOR = {
    "Low": "var(--good)",
    "Low-Medium": "var(--good-soft)",
    "Medium": "var(--caution)",
    "High": "var(--risk)",
    "Unknown": "var(--muted)",
}

CONFIDENCE_COPY = {
    "High confidence": "Conditions are consistent across the latest signals.",
    "Moderate confidence": "The outlook is directionally clear, with some variation.",
    "Low confidence": "Conditions may shift soon, so plan with flexibility.",
    "Unavailable": "No confidence signal is available yet.",
}

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #f6f3ee;
        --surface: #ffffff;
        --surface-soft: #fbfaf8;
        --border: #e7e1d9;
        --text: #17212b;
        --text-soft: #5f6b76;
        --text-faint: #86929d;
        --good: #2f8f67;
        --good-soft: #6aa287;
        --caution: #c88b2f;
        --risk: #c35f57;
        --info: #4f6f8f;
        --shadow: 0 10px 30px rgba(28, 39, 49, 0.06);
        --radius-lg: 24px;
        --radius-md: 18px;
        --radius-sm: 14px;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
        color: var(--text) !important;
        font-family: 'Manrope', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: var(--bg) !important;
        padding: 0 2.5rem 4rem !important;
    }

    [data-testid="stSidebar"] { display: none !important; }

    #MainMenu, footer, header { visibility: hidden; }
    [data-testid="stToolbar"] { display: none; }

    h1, h2, h3, h4, p, div, span, label {
        font-family: 'Manrope', sans-serif !important;
    }

    [data-testid="stMarkdownContainer"] p {
        color: var(--text);
    }

    [data-baseweb="tab-list"] {
        gap: 0.4rem !important;
        background: transparent !important;
        border: none !important;
        margin-bottom: 1.25rem;
    }

    [data-baseweb="tab"] {
        border-radius: 999px !important;
        border: 1px solid var(--border) !important;
        background: rgba(255,255,255,0.55) !important;
        color: var(--text-soft) !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.88rem !important;
        font-weight: 600 !important;
    }

    [aria-selected="true"][data-baseweb="tab"] {
        background: var(--surface) !important;
        color: var(--text) !important;
        box-shadow: var(--shadow) !important;
    }

    [data-baseweb="select"] > div,
    [data-testid="stRadio"] label {
        font-family: 'Manrope', sans-serif !important;
    }

    [data-baseweb="select"] > div {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        color: var(--text) !important;
        min-height: 48px !important;
        box-shadow: none !important;
    }

    [data-testid="stRadio"] > div {
        gap: 0.5rem;
    }

    [data-testid="stRadio"] label {
        background: rgba(255,255,255,0.7);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 0.35rem 0.8rem;
    }

    [data-testid="stAlert"] {
        border-radius: 14px !important;
    }

    [data-testid="stArrowVegaLiteChart"],
    [data-testid="stVegaLiteChart"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 0.35rem;
        box-shadow: var(--shadow);
    }

    .wg-shell {
        max-width: 1240px;
        margin: 0 auto;
        padding-top: 1.5rem;
    }

    .wg-topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.4rem;
        padding: 0.95rem 1.15rem;
        background: rgba(255,255,255,0.62);
        border: 1px solid rgba(231,225,217,0.9);
        border-radius: 18px;
        backdrop-filter: blur(14px);
    }

    .wg-kicker {
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--text-faint);
        margin-bottom: 0.55rem;
    }

    .wg-meta {
        font-size: 0.88rem;
        color: var(--text-soft);
    }

    .wg-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        border-radius: 999px;
        padding: 0.55rem 0.9rem;
        font-size: 0.82rem;
        font-weight: 700;
        border: 1px solid transparent;
        white-space: nowrap;
    }

    .wg-badge.good {
        background: rgba(47, 143, 103, 0.10);
        color: var(--good);
        border-color: rgba(47, 143, 103, 0.18);
    }

    .wg-badge.caution {
        background: rgba(200, 139, 47, 0.10);
        color: var(--caution);
        border-color: rgba(200, 139, 47, 0.18);
    }

    .wg-badge.risk {
        background: rgba(195, 95, 87, 0.10);
        color: var(--risk);
        border-color: rgba(195, 95, 87, 0.18);
    }

    .wg-hero {
        display: grid;
        grid-template-columns: 1.55fr 0.95fr;
        gap: 1rem;
        margin-bottom: 1.35rem;
    }

    .wg-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow);
    }

    .wg-hero-main {
        padding: 2rem 2.1rem;
    }

    .wg-hero-main h1 {
        margin: 0;
        font-size: clamp(2.2rem, 4vw, 3.5rem);
        line-height: 1.02;
        letter-spacing: -0.04em;
        color: var(--text);
    }

    .wg-hero-main .subtitle {
        margin-top: 0.7rem;
        font-size: 1.02rem;
        color: var(--text-soft);
        max-width: 42rem;
        line-height: 1.55;
    }

    .wg-hero-side {
        padding: 1.55rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .wg-label {
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-faint);
    }

    .wg-side-city {
        margin-top: 0.6rem;
        font-size: 1.85rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.03em;
    }

    .wg-side-time {
        margin-top: 0.3rem;
        color: var(--text-soft);
        font-size: 0.92rem;
        line-height: 1.5;
    }

    .wg-section-label {
        margin: 1.7rem 0 0.9rem;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-faint);
    }

    .wg-decision {
        padding: 1.9rem 2rem;
        margin-bottom: 1.1rem;
    }

    .wg-decision-grid {
        display: grid;
        grid-template-columns: 1.4fr 0.8fr;
        gap: 1.4rem;
        align-items: start;
    }

    .wg-decision-title {
        font-size: 2rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.04em;
        margin-bottom: 0.5rem;
    }

    .wg-decision-copy {
        color: var(--text-soft);
        font-size: 1rem;
        line-height: 1.7;
        max-width: 44rem;
    }

    .wg-pill-row {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }

    .wg-pill {
        background: var(--surface-soft);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 0.55rem 0.8rem;
        font-size: 0.83rem;
        color: var(--text-soft);
    }

    .wg-scorebox {
        padding: 1rem;
        border: 1px solid var(--border);
        border-radius: 18px;
        background: linear-gradient(180deg, #ffffff 0%, #fcfbf9 100%);
    }

    .wg-scorebox .big {
        margin-top: 0.35rem;
        font-size: 1.35rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.03em;
    }

    .wg-scorebox .small {
        margin-top: 0.35rem;
        font-size: 0.88rem;
        color: var(--text-soft);
        line-height: 1.55;
    }

    .wg-summary-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .wg-summary-card {
        padding: 1.35rem 1.4rem;
    }

    .wg-summary-value {
        margin-top: 0.55rem;
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.04em;
        color: var(--text);
    }

    .wg-summary-copy {
        margin-top: 0.35rem;
        font-size: 0.9rem;
        line-height: 1.55;
        color: var(--text-soft);
    }

    .wg-strip {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 0.8rem;
        margin-bottom: 1rem;
    }

    .wg-mini-card {
        background: rgba(255,255,255,0.7);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1rem;
    }

    .wg-mini-value {
        margin-top: 0.38rem;
        font-size: 1.15rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.03em;
    }

    .wg-mini-copy {
        margin-top: 0.2rem;
        font-size: 0.78rem;
        color: var(--text-faint);
    }

    .wg-trend-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .wg-trend-card {
        padding: 1.25rem 1.25rem 1rem;
    }

    .wg-trend-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text);
        margin-top: 0.2rem;
    }

    .wg-trend-copy {
        margin-top: 0.3rem;
        color: var(--text-soft);
        font-size: 0.9rem;
        line-height: 1.55;
    }

    .wg-city-list {
        display: grid;
        gap: 0.8rem;
    }

.wg-city-row {
        display: grid;
        grid-template-columns: 1.35fr 0.9fr 0.95fr 1.1fr;
        gap: 1rem;
        align-items: start;
        padding: 1.15rem 1.2rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 20px;
        box-shadow: var(--shadow);
    }

    .wg-city-row.featured {
        border-color: rgba(47, 143, 103, 0.24);
        background: linear-gradient(180deg, #ffffff 0%, #fbf9f5 100%);
        box-shadow: 0 14px 34px rgba(47, 143, 103, 0.08);
    }

    .wg-city-row.warn {
        border-color: rgba(195, 95, 87, 0.22);
    }

    .wg-city-main {
        display: flex;
        align-items: flex-start;
        gap: 0.9rem;
    }

    .wg-rank {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #f3efe9;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: var(--text-soft);
        font-size: 0.9rem;
        font-weight: 800;
    }

    .wg-city-icon {
        width: 52px;
        height: 52px;
        border-radius: 16px;
        background: #f6f2eb;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        flex-shrink: 0;
    }

    .wg-city-name {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--text);
    }

    .wg-city-takeaway {
        margin-top: 0.45rem;
        color: var(--text-soft);
        font-size: 0.84rem;
        line-height: 1.55;
        max-width: 20rem;
    }

    .wg-tag {
        display: inline-flex;
        align-items: center;
        margin-top: 0.3rem;
        border-radius: 999px;
        padding: 0.22rem 0.55rem;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        border: 1px solid transparent;
    }

    .wg-tag.best {
        color: var(--good);
        background: rgba(47, 143, 103, 0.1);
        border-color: rgba(47, 143, 103, 0.14);
    }

    .wg-tag.caution {
        color: var(--caution);
        background: rgba(200, 139, 47, 0.1);
        border-color: rgba(200, 139, 47, 0.14);
    }

    .wg-tag.risk {
        color: var(--risk);
        background: rgba(195, 95, 87, 0.1);
        border-color: rgba(195, 95, 87, 0.14);
    }

    .wg-city-metric-label {
        font-size: 0.73rem;
        color: var(--text-faint);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.2rem;
    }

    .wg-city-metric-value {
        font-size: 0.96rem;
        font-weight: 700;
        color: var(--text);
    }

    .wg-city-confidence {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .wg-confidence-track {
        width: 100%;
        max-width: 132px;
        height: 8px;
        background: #eee8df;
        border-radius: 999px;
        overflow: hidden;
    }

    .wg-confidence-fill {
        height: 100%;
        border-radius: 999px;
    }

    .wg-confidence-copy {
        font-size: 0.78rem;
        color: var(--text-faint);
        margin-top: 0.3rem;
    }

    .wg-utility-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .wg-note-card {
        padding: 1.15rem 1.2rem;
    }

    .wg-note-title {
        margin-top: 0.25rem;
        font-size: 1rem;
        font-weight: 700;
        color: var(--text);
    }

    .wg-note-copy {
        margin-top: 0.3rem;
        color: var(--text-soft);
        font-size: 0.88rem;
        line-height: 1.6;
    }

    .wg-selector-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin: 0.75rem 0 0.9rem;
        box-shadow: var(--shadow);
    }

    .wg-selector-status {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.28rem 0.55rem;
        border-radius: 999px;
        font-size: 0.73rem;
        font-weight: 700;
        margin-top: 0.55rem;
        border: 1px solid transparent;
    }

    .wg-selector-status.good {
        background: rgba(47, 143, 103, 0.1);
        color: var(--good);
        border-color: rgba(47, 143, 103, 0.16);
    }

    .wg-selector-status.caution {
        background: rgba(200, 139, 47, 0.1);
        color: var(--caution);
        border-color: rgba(200, 139, 47, 0.16);
    }

    .wg-selector-status.risk {
        background: rgba(195, 95, 87, 0.1);
        color: var(--risk);
        border-color: rgba(195, 95, 87, 0.16);
    }

    .wg-selector-copy {
        margin-top: 0.35rem;
        font-size: 0.82rem;
        color: var(--text-soft);
        line-height: 1.6;
    }

    .wg-control-shell {
        max-width: 1240px;
        margin: 0 auto 1rem;
    }

    .wg-control-group {
        max-width: 1240px;
        margin: 0 auto 1rem;
        background: rgba(255,255,255,0.72);
        border: 1px solid var(--border);
        border-radius: 22px;
        box-shadow: var(--shadow);
        padding: 1rem;
    }

    .wg-control-group [data-testid="stRadio"] {
        margin-top: 1.55rem;
    }

    .wg-control-label {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-faint);
        margin-bottom: 0.45rem;
    }

    .wg-control-helper {
        font-size: 0.82rem;
        color: var(--text-soft);
        line-height: 1.6;
        margin-top: 0.35rem;
    }

    .wg-compare-hero {
        display: grid;
        grid-template-columns: 1.2fr 0.8fr;
        gap: 1rem;
        margin-bottom: 1rem;
    }

    .wg-compare-panel {
        padding: 1.25rem 1.35rem;
    }

    .wg-compare-panel .headline {
        margin-top: 0.35rem;
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text);
        letter-spacing: -0.04em;
    }

    .wg-compare-panel .subcopy {
        margin-top: 0.35rem;
        color: var(--text-soft);
        font-size: 0.92rem;
        line-height: 1.6;
    }

    .wg-about {
        padding: 1.35rem 1.5rem;
        margin-bottom: 1rem;
    }

    .wg-about p {
        margin: 0.35rem 0 0;
        color: var(--text-soft);
        line-height: 1.65;
    }

    .wg-footer {
        text-align: center;
        color: var(--text-faint);
        font-size: 0.76rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        padding: 1.2rem 0 0.2rem;
    }

    @media (max-width: 1080px) {
        .wg-hero,
        .wg-decision-grid,
        .wg-summary-grid,
        .wg-trend-grid,
        .wg-utility-grid,
        .wg-compare-hero {
            grid-template-columns: 1fr;
        }

        .wg-strip {
            grid-template-columns: repeat(2, 1fr);
        }

        .wg-city-row {
            grid-template-columns: 1fr;
            gap: 0.8rem;
        }
    }

    @media (max-width: 720px) {
        [data-testid="stAppViewContainer"] > .main {
            padding: 0 1rem 3rem !important;
        }

        .wg-topbar {
            flex-direction: column;
            align-items: flex-start;
        }

        .wg-hero-main,
        .wg-hero-side,
        .wg-decision {
            padding: 1.35rem;
        }

        .wg-strip {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


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
        conn,
        params=(city, hours),
    )
    conn.close()
    if df.empty:
        return df
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp").reset_index(drop=True)


def load_latest_prediction(city):
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT p.*, w.city, w.timestamp AS weather_timestamp
        FROM predictions p
        JOIN weather_data w ON p.weather_data_id = w.id
        WHERE w.city = ?
        ORDER BY p.created_at DESC LIMIT 1
        """,
        conn,
        params=(city,),
    )
    conn.close()
    if not df.empty:
        df["weather_timestamp"] = pd.to_datetime(df["weather_timestamp"])
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def load_all_predictions():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT p.*, w.city, w.timestamp AS weather_timestamp
        FROM predictions p
        JOIN weather_data w ON p.weather_data_id = w.id
        ORDER BY p.created_at DESC
        """,
        conn,
    )
    conn.close()
    if not df.empty:
        df["weather_timestamp"] = pd.to_datetime(df["weather_timestamp"])
        df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def get_confidence_band(prob):
    if prob is None:
        return "Unavailable"
    if prob >= 75:
        return "High confidence"
    if prob >= 50:
        return "Moderate confidence"
    return "Low confidence"


def get_risk_level(rain_label, confidence):
    if rain_label == "Heavy rain":
        return "High"
    if rain_label == "Light rain" and confidence >= 60:
        return "Medium"
    if rain_label == "Light rain":
        return "Low-Medium"
    return "Low"


def get_outdoor_suitability(rain_label, confidence, wind_speed):
    if rain_label == "Heavy rain":
        return "Not Recommended"
    if rain_label == "Light rain" and confidence >= 60:
        return "Use Caution"
    if wind_speed >= 25:
        return "Use Caution"
    return "Good"


def get_recommendation_status(suitability, risk):
    if suitability == "Not Recommended" or risk == "High":
        return "Stay indoors"
    if suitability == "Use Caution" or risk in {"Medium", "Low-Medium"}:
        return "Use caution"
    return "Safe to go out"


def generate_decision_message(rain_label, confidence, temp, wind_speed):
    if rain_label == "Heavy rain":
        return "Rain risk is high. Outdoor plans are not recommended right now."
    if rain_label == "Light rain" and confidence >= 60:
        return "Light rain may affect short trips. Consider carrying an umbrella."
    if wind_speed >= 25:
        return "Wind is picking up. Outdoor plans are still possible, but conditions are less comfortable."
    if temp >= 30:
        return "Conditions are stable. Good time for outdoor activity, with extra care in the heat."
    return "Conditions are stable. Good time for outdoor activity."


def add_trend_columns(df):
    out = df.copy()
    out["temp_change_1h"] = out["temperature_2m"].diff()
    out["rain_change_1h"] = out["precipitation"].diff()
    return out


def summarize_trends(df):
    if len(df) < 2:
        return "Stable", "Stable", 0.0, 0.0

    temp_diff = df["temperature_2m"].iloc[-1] - df["temperature_2m"].iloc[0]
    rain_diff = df["precipitation"].iloc[-1] - df["precipitation"].iloc[0]

    if temp_diff > 0.5:
        temp_text = f"Rising by {temp_diff:.1f}°C"
    elif temp_diff < -0.5:
        temp_text = f"Falling by {abs(temp_diff):.1f}°C"
    else:
        temp_text = "Holding steady"

    if rain_diff > 0.1:
        rain_text = f"Increasing by {rain_diff:.1f} mm"
    elif rain_diff < -0.1:
        rain_text = f"Easing by {abs(rain_diff):.1f} mm"
    else:
        rain_text = "Remaining stable"

    return temp_text, rain_text, temp_diff, rain_diff


def get_temp_trend_note(diff):
    if diff > 0.5:
        return "Temperature is rising over the selected period."
    if diff < -0.5:
        return "Temperature is easing down over the selected period."
    return "Temperature has stayed relatively stable."


def get_rain_trend_note(diff):
    if diff > 0.1:
        return "Precipitation risk is increasing slightly."
    if diff < -0.1:
        return "Rain intensity is easing over the selected period."
    return "Rain signal remains stable."


def build_city_ranking_table(all_predictions_df):
    if all_predictions_df.empty:
        return all_predictions_df

    latest = (
        all_predictions_df.sort_values("created_at", ascending=False)
        .groupby("city", as_index=False)
        .head(1)
        .copy()
    )

    latest["Rain"] = latest["rain_prediction"].map(RAIN_LABELS)
    latest["Confidence"] = latest["rain_probability"].round(0).astype(int)
    latest["Temp"] = latest["predicted_temperature"].round(1)
    latest["Suitability"] = latest.apply(
        lambda row: get_outdoor_suitability(row["Rain"], row["rain_probability"], 0),
        axis=1,
    )

    def score(row):
        penalty = {0: 0, 1: 1, 2: 2}.get(int(row["rain_prediction"]), 2)
        return penalty + row["rain_probability"] / 100.0

    latest["_score"] = latest.apply(score, axis=1)
    latest = latest.sort_values(["_score", "city"]).reset_index(drop=True)
    latest["Rank"] = range(1, len(latest) + 1)
    latest["Confidence Band"] = latest["rain_probability"].apply(get_confidence_band)
    latest["Recommendation"] = latest["Suitability"].map({
        "Good": "Best choice",
        "Use Caution": "Use caution",
        "Not Recommended": "Least favorable now",
    }).fillna("Review conditions")
    return latest


def get_weather_icon(rain_label):
    return {
        "Clear": "☀️",
        "Light rain": "🌦️",
        "Heavy rain": "🌧️",
    }.get(rain_label, "☁️")


def get_city_takeaway(row, best_city, worst_city):
    if row["city"] == best_city:
        return "Strongest outdoor conditions right now."
    if row["city"] == worst_city:
        return "Less favorable at the moment."
    if row["Rain"] == "Light rain":
        return "Light rain may affect short trips."
    if row["Rain"] == "Heavy rain":
        return "Conditions are unsettled right now."
    return "Conditions look relatively steady."


def get_confidence_color(confidence_value):
    if confidence_value >= 75:
        return "var(--good)"
    if confidence_value >= 50:
        return "var(--caution)"
    return "var(--risk)"


def metric_card(label, value, copy_text, emoji):
    return f"""
    <div class="wg-card wg-summary-card">
        <div class="wg-label">{emoji} {label}</div>
        <div class="wg-summary-value">{value}</div>
        <div class="wg-summary-copy">{copy_text}</div>
    </div>
    """


def mini_condition_card(label, value, copy_text, emoji):
    return f"""
    <div class="wg-mini-card">
        <div class="wg-label">{emoji} {label}</div>
        <div class="wg-mini-value">{value}</div>
        <div class="wg-mini-copy">{copy_text}</div>
    </div>
    """


def city_row(row, best_city, worst_city):
    tag = ""
    row_class = "wg-city-row"
    if row["city"] == best_city:
        tag = '<div class="wg-tag best">Best city right now</div>'
        row_class += " featured"
    elif row["city"] == worst_city:
        tag = '<div class="wg-tag risk">Highest risk</div>'
        row_class += " warn"
    elif row["Suitability"] == "Use Caution":
        tag = '<div class="wg-tag caution">Use caution</div>'

    suitability_color = SUITABILITY_COLOR.get(row["Suitability"], "var(--muted)")
    weather_icon = get_weather_icon(row["Rain"])
    takeaway = get_city_takeaway(row, best_city, worst_city)
    confidence_color = get_confidence_color(row["Confidence"])

    return f"""
    <div class="{row_class}">
        <div class="wg-city-main">
            <div class="wg-rank">{row["Rank"]}</div>
            <div class="wg-city-icon">{weather_icon}</div>
            <div>
                <div class="wg-city-name">{row["city"]}</div>
                {tag}
                <div class="wg-city-takeaway">{takeaway}</div>
            </div>
        </div>
        <div>
            <div class="wg-city-metric-label">Predicted temperature</div>
            <div class="wg-city-metric-value">{row["Temp"]:.1f}°C</div>
        </div>
        <div>
            <div class="wg-city-metric-label">Rain outlook</div>
            <div class="wg-city-metric-value">{row["Rain"]}</div>
        </div>
        <div>
            <div class="wg-city-metric-label">Confidence</div>
            <div class="wg-city-confidence">
                <div class="wg-confidence-track">
                    <div class="wg-confidence-fill" style="width:{row["Confidence"]}%; background:{confidence_color};"></div>
                </div>
                <div class="wg-city-metric-value">{row["Confidence"]}%</div>
            </div>
            <div class="wg-confidence-copy">{row["Confidence Band"]}</div>
        </div>
        <div>
            <div class="wg-city-metric-label">Suitability</div>
            <div class="wg-city-metric-value" style="color:{suitability_color};">{row["Recommendation"]}</div>
            <div class="wg-confidence-copy">{row["Rain"]}</div>
        </div>
    </div>
    """


if not DB_PATH.exists():
    st.error(f"Database not found at: {DB_PATH}")
    st.stop()

cities = load_cities()
if not cities:
    st.error("No weather data found. Run the data collector first.")
    st.stop()

all_predictions_df = load_all_predictions()
ranking_df = build_city_ranking_table(all_predictions_df)
best_city = ranking_df.iloc[0]["city"] if not ranking_df.empty else None
worst_city = ranking_df.iloc[-1]["city"] if not ranking_df.empty else None

render_html(
    """
    <div class="wg-control-shell">
        <div class="wg-selector-card">
            <div class="wg-label">📍 City selection</div>
            <div class="wg-selector-copy">Choose a city to view its current recommendation and short-term outlook.</div>
        </div>
    </div>
    """
)

control_col_1, control_col_2 = st.columns([1.5, 1])
with control_col_1:
    render_html('<div class="wg-control-label">Choose city</div>')
    city = st.selectbox(
        "Choose city",
        cities,
        key="city_selector",
        label_visibility="collapsed",
        help="Choose a Cyprus city to view its current recommendation and short-term outlook.",
    )
    render_html('<div class="wg-control-helper">Choose a city to view its current recommendation and short-term outlook.</div>')
with control_col_2:
    render_html('<div class="wg-control-label">Selected period</div>')
    time_window = st.radio(
        "Selected period",
        ["12 Hours", "24 Hours"],
        horizontal=True,
        label_visibility="collapsed",
        help="Switch between the latest 12 hours and 24 hours of recent conditions.",
    )
    render_html('<div class="wg-control-helper">Adjust the recent time window used for the condition and trend view.</div>')

hours_to_load = 12 if time_window == "12 Hours" else 24
selected_city_summary = None
if not ranking_df.empty:
    selected_match = ranking_df[ranking_df["city"] == city]
    if not selected_match.empty:
        selected_city_summary = selected_match.iloc[0]

if selected_city_summary is not None:
    render_html(
        f"""
        <div class="wg-control-shell">
            <div class="wg-selector-card">
                <div class="wg-label">Current city snapshot</div>
                <div class="wg-selector-status {'good' if selected_city_summary['Recommendation'] == 'Best choice' else 'risk' if selected_city_summary['Recommendation'] == 'Least favorable now' else 'caution'}">
                    {'🌤️' if selected_city_summary['Recommendation'] == 'Best choice' else '🌧️' if selected_city_summary['Recommendation'] == 'Least favorable now' else '🌦️'} {selected_city_summary["Recommendation"]}
                </div>
                <div class="wg-selector-copy">{city} currently shows {selected_city_summary["Rain"].lower()} with {selected_city_summary["Confidence Band"].lower()} and {selected_city_summary["Temp"]:.1f}°C expected.</div>
            </div>
        </div>
        """
    )

weather_df = load_weather_data(city, hours=hours_to_load)
prediction_df = load_latest_prediction(city)

if weather_df.empty:
    st.error(f"No data for {city}.")
    st.stop()

weather_df = add_trend_columns(weather_df)
latest = weather_df.iloc[-1]
last_update = latest["timestamp"]

predicted_temp = None
predicted_prob = None
predicted_rain_label = "Unavailable"
prediction_time = None

if not prediction_df.empty:
    prediction = prediction_df.iloc[0]
    predicted_temp = float(prediction["predicted_temperature"])
    predicted_prob = float(prediction["rain_probability"])
    predicted_rain_label = RAIN_LABELS.get(int(prediction["rain_prediction"]), "Unavailable")
    prediction_time = prediction["created_at"]

confidence_band = get_confidence_band(predicted_prob)
risk = get_risk_level(predicted_rain_label, predicted_prob) if predicted_prob is not None else "Unknown"
suitability = (
    get_outdoor_suitability(predicted_rain_label, predicted_prob, float(latest["wind_speed_10m"]))
    if predicted_prob is not None
    else "Unknown"
)
decision_status = get_recommendation_status(suitability, risk) if predicted_prob is not None else "Use caution"
decision_message = (
    generate_decision_message(
        predicted_rain_label,
        predicted_prob,
        float(latest["temperature_2m"]),
        float(latest["wind_speed_10m"]),
    )
    if predicted_prob is not None
    else "Current readings are available, but the short-term recommendation has not been generated yet."
)

temp_trend_text, rain_trend_text, temp_diff, rain_diff = summarize_trends(weather_df)
temp_trend_note = get_temp_trend_note(temp_diff)
rain_trend_note = get_rain_trend_note(rain_diff)
last_update_text = last_update.strftime("%d %b %Y, %H:%M")
prediction_time_text = prediction_time.strftime("%H:%M") if prediction_time is not None else "Pending"
status_tone = STATUS_META[decision_status]["tone"]

tab_main, tab_compare, tab_about = st.tabs(["Overview", "Across Cyprus", "About"])

with tab_main:
    render_html(
        f"""
        <div class="wg-shell">
            <div class="wg-topbar">
                <div>
                    <div class="wg-kicker">Selected city</div>
                    <div class="wg-meta"><strong>{city}</strong> &nbsp;·&nbsp; Last update {last_update_text} &nbsp;·&nbsp; Short-term outlook {prediction_time_text}</div>
                </div>
                <div class="wg-badge {status_tone}">{STATUS_META[decision_status]["emoji"]} {decision_status}</div>
            </div>

            <div class="wg-hero">
                <div class="wg-card wg-hero-main">
                    <div class="wg-kicker">🌍 WeatherGo Cyprus</div>
                    <h1>Short-term weather decisions for real life</h1>
                    <div class="subtitle">Clear recommendations for outdoor planning across Cyprus.</div>
                </div>
                <div class="wg-card wg-hero-side">
                    <div>
                        <div class="wg-label">📍 Current focus</div>
                        <div class="wg-side-city">{city}</div>
                        <div class="wg-side-time">Use the recommendation below to decide whether now is a good time to head out.</div>
                    </div>
                    <div class="wg-badge {status_tone}">{STATUS_META[decision_status]["emoji"]} {decision_status}</div>
                </div>
            </div>

            <div class="wg-section-label">✨ Decision</div>
            <div class="wg-card wg-decision">
                <div class="wg-decision-grid">
                    <div>
                        <div class="wg-label">🧭 Main recommendation</div>
                        <div class="wg-decision-title">{decision_status}</div>
                        <div class="wg-decision-copy">{decision_message}</div>
                        <div class="wg-pill-row">
                            <div class="wg-pill">Risk level: <strong>{risk}</strong></div>
                            <div class="wg-pill">Outdoor suitability: <strong>{suitability}</strong></div>
                            <div class="wg-pill">City checked: <strong>{city}</strong></div>
                        </div>
                    </div>
                    <div class="wg-scorebox">
                        <div class="wg-label">☁️ Why this recommendation</div>
                        <div class="big">{predicted_rain_label if predicted_prob is not None else "Awaiting short-term outlook"}</div>
                        <div class="small">{CONFIDENCE_COPY[confidence_band]}</div>
                    </div>
                </div>
            </div>
        </div>
        """
    )

    render_html('<div class="wg-section-label">📌 Prediction summary</div>')
    render_html(
        f"""
        <div class="wg-summary-grid">
            {metric_card("Predicted temperature", f"{predicted_temp:.1f}°C" if predicted_temp is not None else "—", "Expected temperature over the next short period.", "🌡️")}
            {metric_card("Rain category", predicted_rain_label if predicted_prob is not None else "Unavailable", "A simple view of what conditions may feel like outside.", "🌦️")}
            {metric_card("Confidence level", confidence_band, CONFIDENCE_COPY[confidence_band], "🎯")}
        </div>
        """
    )

    render_html('<div class="wg-section-label">🌤️ Current conditions</div>')
    render_html(
        f"""
        <div class="wg-strip">
            {mini_condition_card("Temperature", f"{latest['temperature_2m']:.1f}°C", "Current reading", "🌡️")}
            {mini_condition_card("Humidity", f"{int(latest['relative_humidity_2m'])}%", "Air moisture", "💧")}
            {mini_condition_card("Wind", f"{latest['wind_speed_10m']:.1f} km/h", "Surface wind", "💨")}
            {mini_condition_card("Rain", f"{latest['precipitation']:.1f} mm", "Recent precipitation", "🌧️")}
            {mini_condition_card("Cloud cover", f"{int(latest['cloud_cover'])}%", "Sky coverage", "☁️")}
            {mini_condition_card("Pressure", f"{latest['pressure_msl']:.0f} hPa", "Atmospheric pressure", "📈")}
        </div>
        """
    )

    render_html('<div class="wg-section-label">📈 Trend insight</div>')
    render_html(
        f"""
        <div class="wg-trend-grid">
            <div class="wg-card wg-trend-card">
                <div class="wg-label">🌡️ Temperature trend</div>
                <div class="wg-trend-title">{temp_trend_text}</div>
                <div class="wg-trend-copy">{temp_trend_note}</div>
            </div>
            <div class="wg-card wg-trend-card">
                <div class="wg-label">🌧️ Rain trend</div>
                <div class="wg-trend-title">{rain_trend_text}</div>
                <div class="wg-trend-copy">{rain_trend_note}</div>
            </div>
        </div>
        """
    )

    chart_col_1, chart_col_2 = st.columns(2)
    indexed_df = weather_df.set_index("timestamp")

    with chart_col_1:
        st.caption("🌡️ Temperature over the selected period")
        st.area_chart(
            indexed_df[["temperature_2m"]],
            color=["#6c8fb4"],
            height=220,
            use_container_width=True,
        )

    with chart_col_2:
        st.caption("🌧️ Rain signal over the selected period")
        st.area_chart(
            indexed_df[["precipitation"]],
            color=["#8fb7aa"],
            height=220,
            use_container_width=True,
        )

with tab_compare:
    render_html(
        f"""
        <div class="wg-shell">
            <div class="wg-section-label">🏛️ Best conditions across Cyprus</div>
            <div class="wg-compare-hero">
                <div class="wg-card wg-compare-panel">
                    <div class="wg-label">📍 City comparison</div>
                    <div class="headline">Compare conditions across Cyprus before deciding where to go.</div>
                    <div class="subcopy">Review every supported city in one ranked view, then choose the location with the strongest outdoor conditions right now.</div>
                </div>
                <div class="wg-card wg-compare-panel">
                    <div class="wg-label">✨ Current takeaway</div>
                    <div class="headline">{best_city if best_city else "No city available"}</div>
                    <div class="subcopy">{f"Right now, {best_city} offers the strongest outdoor conditions." if best_city else "A ranked comparison will appear here once city outlooks are available."}</div>
                </div>
            </div>
        </div>
        """
    )

    if ranking_df.empty:
        st.info("No cross-city outlook is available yet.")
    else:
        city_rows = "".join(
            city_row(row, best_city, worst_city)
            for _, row in ranking_df.iterrows()
        )
        render_html(f'<div class="wg-city-list">{city_rows}</div>')
        render_html(
            f"""
            <div class="wg-card wg-about" style="margin-top:1rem;">
                <div class="wg-label">Short takeaway</div>
                <p>{f"Right now, {best_city} looks like the best choice for outdoor plans, while {worst_city} appears least favorable." if best_city and worst_city else "City takeaways will appear here when ranked outlooks are available."}</p>
            </div>
            """
        )

        render_html(
            f"""
            <div class="wg-section-label">✅ Why this is useful</div>
            <div class="wg-utility-grid">
                <div class="wg-card wg-note-card">
                    <div class="wg-label">🧭 Clear decisions</div>
                    <div class="wg-note-title">More than raw readings</div>
                    <div class="wg-note-copy">See a practical recommendation first, so you can decide quickly without interpreting every weather variable yourself.</div>
                </div>
                <div class="wg-card wg-note-card">
                    <div class="wg-label">🎯 Confidence-aware</div>
                    <div class="wg-note-title">Useful when conditions are mixed</div>
                    <div class="wg-note-copy">Confidence levels help you judge whether the outlook looks settled or whether plans should stay flexible.</div>
                </div>
                <div class="wg-card wg-note-card">
                    <div class="wg-label">📍 City comparison</div>
                    <div class="wg-note-title">Choose the better option</div>
                    <div class="wg-note-copy">When one city looks less favorable, you can immediately compare it with {best_city} and the rest of Cyprus.</div>
                </div>
                <div class="wg-card wg-note-card">
                    <div class="wg-label">🇨🇾 Built for Cyprus</div>
                    <div class="wg-note-title">Useful for daily outdoor choices</div>
                    <div class="wg-note-copy">The product is organized around the question people actually ask: where are conditions best right now?</div>
                </div>
            </div>
            """
        )

with tab_about:
    render_html(
        """
        <div class="wg-shell">
            <div class="wg-section-label">ℹ️ About</div>
            <div class="wg-card wg-about">
                <div class="wg-label">🔎 How it works</div>
                <p>WeatherGo Cyprus combines recent weather readings with a short-term outlook to turn conditions into a simple outdoor recommendation.</p>
                <p>The experience is designed for quick planning: one city view for immediate decisions, plus a Cyprus-wide comparison when you want the best available option.</p>
                <p>Main page clutter has been removed so the most important signals stay easy to read and compare.</p>
            </div>
        </div>
        """
    )

render_html(
    """
    <div class="wg-footer">WeatherGo Cyprus</div>
    """
)
