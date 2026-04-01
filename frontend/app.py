import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Short-term Weather Prediction Dashboard",
    layout="wide",
)

# Absolute path to project database
DB_PATH = Path(__file__).resolve().parent.parent / "database" / "weather.db"

RAIN_LABELS = {
    0: "No Rain",
    1: "Light Rain",
    2: "Moderate/Heavy Rain",
}


# ==========================================
# DATABASE HELPERS
# ==========================================
def get_connection() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)


def load_cities() -> list[str]:
    conn = get_connection()
    query = """
        SELECT DISTINCT city
        FROM weather_data
        ORDER BY city
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df["city"].tolist()


def load_weather_data(city: str, hours: int = 24) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT *
        FROM weather_data
        WHERE city = ?
        ORDER BY timestamp DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(city, hours))
    conn.close()

    if df.empty:
        return df

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df.sort_values("timestamp").reset_index(drop=True)


def load_latest_prediction(city: str) -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT
            p.id,
            p.weather_data_id,
            p.predicted_temperature,
            p.rain_probability,
            p.rain_prediction,
            p.created_at,
            w.city,
            w.timestamp AS weather_timestamp
        FROM predictions p
        JOIN weather_data w
            ON p.weather_data_id = w.id
        WHERE w.city = ?
        ORDER BY p.created_at DESC
        LIMIT 1
    """
    df = pd.read_sql_query(query, conn, params=(city,))
    conn.close()

    if not df.empty:
        df["weather_timestamp"] = pd.to_datetime(df["weather_timestamp"])
        df["created_at"] = pd.to_datetime(df["created_at"])

    return df


def load_all_predictions() -> pd.DataFrame:
    conn = get_connection()
    query = """
        SELECT
            p.id,
            p.weather_data_id,
            p.predicted_temperature,
            p.rain_probability,
            p.rain_prediction,
            p.created_at,
            w.city,
            w.timestamp AS weather_timestamp
        FROM predictions p
        JOIN weather_data w
            ON p.weather_data_id = w.id
        ORDER BY p.created_at DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        df["weather_timestamp"] = pd.to_datetime(df["weather_timestamp"])
        df["created_at"] = pd.to_datetime(df["created_at"])

    return df


# ==========================================
# LOAD DATA
# ==========================================
if not DB_PATH.exists():
    st.error(f"Database file not found: {DB_PATH}")
    st.stop()

cities = load_cities()

if not cities:
    st.error("No weather data found in the database. Run the data collector first.")
    st.stop()

# =================================================
# SIDEBAR
# =================================================
st.sidebar.title("Dashboard Settings")
city = st.sidebar.selectbox("Select City", cities)
time_window = st.sidebar.selectbox("Time Window", ["Last 12 Hours", "Last 24 Hours"])
view_option = st.sidebar.radio(
    "Select View",
    ["Dashboard", "Model Info", "Raw Data"]
)

hours_to_load = 12 if time_window == "Last 12 Hours" else 24

weather_df = load_weather_data(city, hours=hours_to_load)
prediction_df = load_latest_prediction(city)

if weather_df.empty:
    st.error(f"No weather data found for {city}.")
    st.stop()

latest = weather_df.iloc[-1]
last_update = latest["timestamp"]

predicted_temperature_next_hour = None
predicted_rain_probability = None
predicted_rain_label = "No prediction available"
prediction_created_at = None

if not prediction_df.empty:
    latest_prediction = prediction_df.iloc[0]
    predicted_temperature_next_hour = float(latest_prediction["predicted_temperature"])
    predicted_rain_probability = float(latest_prediction["rain_probability"])
    predicted_rain_label = RAIN_LABELS.get(int(latest_prediction["rain_prediction"]), "Unknown")
    prediction_created_at = latest_prediction["created_at"]

# =================================================
# HEADER
# =================================================
st.title("Short-Term Weather Monitoring and Prediction Dashboard")


header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.subheader(f"City: {city}")
with header_col2:
    st.metric("Last Weather Update", last_update.strftime("%Y-%m-%d %H:%M"))

st.markdown("---")

# =================================================
# CURRENT WEATHER
# =================================================
st.subheader("Current Weather Summary")

row1 = st.columns(4)
row2 = st.columns(2)

row1[0].metric("Temperature", f"{latest['temperature_2m']:.1f} °C")
row1[1].metric("Humidity", f"{int(latest['relative_humidity_2m'])}%")
row1[2].metric("Wind Speed", f"{latest['wind_speed_10m']:.1f} km/h")
row1[3].metric("Precipitation", f"{latest['precipitation']:.1f} mm")

row2[0].metric("Cloud Cover", f"{int(latest['cloud_cover'])}%")
row2[1].metric("Pressure", f"{latest['pressure_msl']:.0f} hPa")

st.markdown("---")


if view_option == "Dashboard":
    st.subheader("Next-Hour Predictions")

    pred1, pred2, pred3 = st.columns(3)

    if predicted_temperature_next_hour is not None:
        pred1.metric("Predicted Temperature", f"{predicted_temperature_next_hour:.1f} °C")
    else:
        pred1.metric("Predicted Temperature", "N/A")

    if predicted_rain_probability is not None:
        pred2.metric("Model Confidence", f"{predicted_rain_probability:.0f}%")
    else:
        pred2.metric("Model Confidence", "N/A")

    pred3.metric("Rain Category", predicted_rain_label)

    if prediction_created_at is not None:
        st.caption(f"Latest prediction generated at: {prediction_created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    st.markdown("---")

    st.subheader("Model Performance Snapshot")
    st.info(
        "Evaluation metrics shown here can be connected dynamically later. "
        "For now, performance is validated through the training scripts."
    )

    perf1, perf2, perf3 = st.columns(3)
    perf1.metric("Temperature Metric", "RMSE")
    perf2.metric("Rain Metric", "Accuracy / F1")
    perf3.metric("Prediction Type", "Regression + Classification")

    st.markdown("---")

    st.subheader("Weather Trends")
    indexed_df = weather_df.set_index("timestamp")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Temperature Trend**")
        st.line_chart(indexed_df[["temperature_2m"]])

        st.markdown("**Wind Speed Trend**")
        st.line_chart(indexed_df[["wind_speed_10m"]])

    with c2:
        st.markdown("**Humidity Trend**")
        st.line_chart(indexed_df[["relative_humidity_2m"]])

        st.markdown("**Precipitation Trend**")
        st.line_chart(indexed_df[["precipitation"]])

    st.markdown("---")

    st.subheader("Recent Weather Observations")
    display_df = weather_df.copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(display_df, use_container_width=True)

    st.markdown("---")

    st.subheader("Prediction Overview for All Cities")
    all_predictions_df = load_all_predictions()

    if not all_predictions_df.empty:
        latest_per_city = (
            all_predictions_df.sort_values("created_at", ascending=False)
            .groupby("city", as_index=False)
            .head(1)
            .copy()
        )

        latest_per_city["rain_label"] = latest_per_city["rain_prediction"].map(RAIN_LABELS)
        latest_per_city["weather_timestamp"] = latest_per_city["weather_timestamp"].dt.strftime("%Y-%m-%d %H:%M")
        latest_per_city["created_at"] = latest_per_city["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")

        latest_per_city = latest_per_city[
            [
                "city",
                "weather_timestamp",
                "predicted_temperature",
                "rain_probability",
                "rain_label",
                "created_at",
            ]
        ].rename(
            columns={
                "city": "City",
                "weather_timestamp": "Weather Timestamp",
                "predicted_temperature": "Predicted Temperature (°C)",
                "rain_probability": "Model Confidence (%)",
                "rain_label": "Rain Category",
                "created_at": "Prediction Created At",
            }
        )

        st.dataframe(latest_per_city, use_container_width=True)
    else:
        st.warning("No predictions found yet.")

# =================================================
# MODEL INFO VIEW
# =================================================
elif view_option == "Model Info":
    st.subheader("Model Information")

    st.write("**Target Variables**")
    st.write("- Next-hour temperature")
    st.write("- Next-hour rain category")

    st.write("**Rain Categories**")
    st.write("- No Rain")
    st.write("- Light Rain")
    st.write("- Moderate/Heavy Rain")

    st.write("**Input Features**")
    st.write("- latitude")
    st.write("- longitude")
    st.write("- temperature_2m")
    st.write("- relative_humidity_2m")
    st.write("- precipitation")
    st.write("- wind_speed_10m")
    st.write("- cloud_cover")
    st.write("- pressure_msl")
    st.write("- hour of day")
    st.write("- day of week")

    st.write("**Models Used**")
    st.write("- Random Forest Regressor (temperature prediction)")
    st.write("- Random Forest Classifier (rain category prediction)")

    st.write("**Evaluation Metrics**")
    st.write("- MAE")
    st.write("- RMSE")
    st.write("- Accuracy")
    st.write("- Precision / Recall")

    st.write("**Data Source Plan**")
    st.write("- Open-Meteo API")
    st.write("- SQLite table: weather_data")

    st.write("**Machine Learning Goal**")
    st.write(
        "The system will use historical weather observations to predict "
        "short-term temperature and rainfall conditions for the next hour."
    )


elif view_option == "Raw Data":
    st.subheader("Raw Weather Data")
    raw_df = weather_df.copy()
    raw_df["timestamp"] = raw_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(raw_df, use_container_width=True)

st.markdown("---")
