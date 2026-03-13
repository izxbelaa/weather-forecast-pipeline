import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Weather Prediction Dashboard",
    page_icon="🌤️",
    layout="wide",
)


# Mock data for Phase A UI prototype
# will be replaced later with SQLite / real API data
now = datetime.now().replace(minute=0, second=0, microsecond=0)

hours = [now - timedelta(hours=i) for i in range(23, -1, -1)]

temperature = [
    18.2, 18.4, 18.7, 19.0, 19.2, 19.5, 19.8, 20.1,
    20.3, 20.5, 20.2, 19.9, 19.7, 19.4, 19.1, 18.9,
    18.8, 18.7, 18.6, 18.5, 18.4, 18.3, 18.2, 18.1
]

humidity = [
    72, 71, 70, 68, 66, 64, 62, 60,
    58, 57, 59, 61, 63, 65, 67, 68,
    69, 70, 71, 72, 73, 73, 74, 75
]

wind_speed = [
    8.0, 8.3, 8.7, 9.1, 9.5, 10.0, 10.5, 11.0,
    11.2, 11.5, 11.0, 10.8, 10.3, 9.9, 9.5, 9.2,
    9.0, 8.8, 8.6, 8.4, 8.2, 8.1, 8.0, 7.8
]

precipitation = [
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1, 0.2,
    0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.1,
    0.3, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
]

cloud_cover = [
    20, 22, 25, 28, 35, 42, 50, 58,
    60, 55, 48, 40, 35, 30, 28, 32,
    45, 52, 48, 40, 35, 30, 25, 22
]

pressure = [
    1014, 1014, 1013, 1013, 1012, 1012, 1011, 1011,
    1010, 1010, 1011, 1011, 1012, 1012, 1013, 1013,
    1012, 1011, 1011, 1012, 1013, 1013, 1014, 1014
]

df = pd.DataFrame(
    {
        "timestamp": hours,
        "temperature_2m": temperature,
        "relative_humidity_2m": humidity,
        "wind_speed_10m": wind_speed,
        "precipitation": precipitation,
        "cloud_cover": cloud_cover,
        "pressure_msl": pressure,
    }
)

# Mock ML outputs
df["predicted_temperature"] = [
    18.3, 18.5, 18.6, 18.9, 19.1, 19.4, 19.7, 20.0,
    20.2, 20.4, 20.1, 19.8, 19.6, 19.3, 19.0, 18.8,
    18.7, 18.6, 18.5, 18.4, 18.3, 18.2, 18.1, 18.0
]

predicted_temperature_next_hour = 18.4
predicted_rain_probability = 0.28
predicted_rain_label = "No Rain"

# Mock model metrics
mae = 0.65
rmse = 0.89
rain_accuracy = 0.84

last_update = df["timestamp"].iloc[-1]
latest = df.iloc[-1]

# =================================================
# SIDEBAR
# =================================================
st.sidebar.title("Dashboard Settings")
city = st.sidebar.selectbox("Select City", ["Limassol"])
time_window = st.sidebar.selectbox("Time Window", ["Last 12 Hours", "Last 24 Hours"])
view_option = st.sidebar.radio(
    "Select View",
    ["Dashboard", "Model Info", "Raw Data"]
)

if time_window == "Last 12 Hours":
    filtered_df = df.tail(12).copy()
else:
    filtered_df = df.copy()

# =================================================
# HEADER
# =================================================
st.title("🌤️ Real-Time Weather Monitoring and Prediction Dashboard")
st.caption(
    "Phase A prototype for an end-to-end weather data science system "
    "(Open-Meteo API → SQLite → ML Models → Streamlit Dashboard)"
)

header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.subheader(f"City: {city}")
with header_col2:
    st.metric("Last Update", last_update.strftime("%H:%M"))

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
    pred1.metric("Predicted Temperature", f"{predicted_temperature_next_hour:.1f} °C")
    pred2.metric("Rain Probability", f"{predicted_rain_probability * 100:.0f}%")
    pred3.metric("Rain Prediction", predicted_rain_label)

    st.markdown("---")

    st.subheader("Model Performance Snapshot")
    perf1, perf2, perf3 = st.columns(3)
    perf1.metric("MAE", f"{mae:.2f}")
    perf2.metric("RMSE", f"{rmse:.2f}")
    perf3.metric("Rain Accuracy", f"{rain_accuracy * 100:.0f}%")

    st.markdown("---")

    st.subheader("Weather Trends")
    indexed_df = filtered_df.set_index("timestamp")
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

    st.subheader("Actual vs Predicted Temperature")
    compare_df = filtered_df[["timestamp", "temperature_2m", "predicted_temperature"]].copy()
    compare_df = compare_df.set_index("timestamp")
    st.line_chart(compare_df)

    st.markdown("---")

    st.subheader("Recent Weather Observations")
    display_df = filtered_df.copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(display_df.tail(10), use_container_width=True)

    st.markdown("---")


# =================================================
# MODEL INFO VIEW
# =================================================
elif view_option == "Model Info":
    st.subheader("Model Information")

    st.write("**Target Variables**")
    st.write("- Next-hour temperature")
    st.write("- Next-hour rain / no rain")

    st.write("**Input Features**")
    st.write("- temperature_2m")
    st.write("- relative_humidity_2m")
    st.write("- precipitation")
    st.write("- wind_speed_10m")
    st.write("- cloud_cover")
    st.write("- pressure_msl")
    st.write("- hour of day")

    st.write("**Planned Models**")
    st.write("- Linear Regression")
    st.write("- Logistic Regression")
    st.write("- Random Forest")

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
    raw_df = filtered_df.copy()
    raw_df["timestamp"] = raw_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(raw_df, use_container_width=True)

st.markdown("---")
st.info("Phase A prototype")