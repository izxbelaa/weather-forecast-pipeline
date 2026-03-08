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

hours = [now - timedelta(hours=i) for i in range(11, -1, -1)]
temperature = [18.2, 18.5, 18.9, 19.3, 19.8, 20.1, 20.4, 20.0, 19.7, 19.4, 19.1, 18.8]
humidity = [72, 70, 68, 66, 63, 61, 59, 60, 62, 65, 67, 69]
wind_speed = [9.0, 9.5, 10.0, 10.2, 11.0, 11.5, 12.0, 11.6, 10.8, 10.2, 9.8, 9.4]
precipitation = [0.0, 0.0, 0.0, 0.0, 0.1, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cloud_cover = [20, 25, 30, 35, 45, 55, 50, 40, 35, 30, 25, 20]
pressure = [1014, 1014, 1013, 1013, 1012, 1012, 1011, 1011, 1012, 1012, 1013, 1013]

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

# Mock predictions
predicted_temperature_next_hour = 18.5
predicted_rain_probability = 0.22
predicted_rain_label = "No Rain"

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
st.sidebar.title("Settings")
city = st.sidebar.selectbox("Select City", ["Limassol"])
view_option = st.sidebar.radio(
    "Select View",
    ["Dashboard", "Raw Data", "Model Info"],
)

# -------------------------------------------------
# Main title
# -------------------------------------------------
st.title("🌤️ Real-Time Weather Monitoring and Prediction Dashboard")
st.caption("Phase A prototype using mock data for UI development")

st.subheader(f"City: {city}")

# -------------------------------------------------
# Current weather cards
# -------------------------------------------------
latest = df.iloc[-1]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Temperature", f"{latest['temperature_2m']:.1f} °C")
col2.metric("Humidity", f"{int(latest['relative_humidity_2m'])}%")
col3.metric("Wind Speed", f"{latest['wind_speed_10m']:.1f} km/h")
col4.metric("Precipitation", f"{latest['precipitation']:.1f} mm")

st.markdown("---")


if view_option == "Dashboard":
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("Temperature Trend (Last 12 Hours)")
        temp_chart_df = df.set_index("timestamp")[["temperature_2m"]]
        st.line_chart(temp_chart_df)

        st.subheader("Humidity Trend (Last 12 Hours)")
        humidity_chart_df = df.set_index("timestamp")[["relative_humidity_2m"]]
        st.line_chart(humidity_chart_df)

    with right_col:
        st.subheader("Next-Hour Predictions")
        st.metric(
            "Predicted Temperature",
            f"{predicted_temperature_next_hour:.1f} °C",
        )
        st.metric(
            "Rain Probability",
            f"{predicted_rain_probability * 100:.0f}%",
        )
        st.write(f"**Rain Prediction:** {predicted_rain_label}")

        st.subheader("Current Conditions")
        st.write(f"**Cloud Cover:** {int(latest['cloud_cover'])}%")
        st.write(f"**Pressure:** {latest['pressure_msl']:.0f} hPa")
        st.write(f"**Last Update:** {latest['timestamp']}")

    st.subheader("Recent Weather Observations")
    display_df = df.copy()
    display_df["timestamp"] = display_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(display_df, use_container_width=True)

elif view_option == "Raw Data":
    st.subheader("Raw Weather Data")
    raw_df = df.copy()
    raw_df["timestamp"] = raw_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(raw_df, use_container_width=True)

elif view_option == "Model Info":
    st.subheader("Model Information")
    st.write("**Target Variables**")
    st.write("- Next-hour temperature")
    st.write("- Next-hour rain / no rain")

    st.write("**Planned Features**")
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
    st.write("- MAE / RMSE for temperature prediction")
    st.write("- Accuracy / Precision / Recall for rain prediction")

st.markdown("---")
st.info("Phase A prototype")