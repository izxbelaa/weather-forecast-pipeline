import sqlite3
import pandas as pd
from datetime import timedelta
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

from database.db import insert_prediction

def categorize_rain(mm):
    if mm == 0:
        return 0          # No Rain
    elif mm <= 2.5:
        return 1          # Light Rain
    elif mm <= 7.6:
        return 2          # Moderate Rain
    else:
        return 3          # Heavy Rain


RAIN_LABELS = {
    0: "No Rain",
    1: "Light Rain",
    2: "Moderate Rain",
    3: "Heavy Rain",
}


# ---------------------------
# Load weather data
# ---------------------------
conn = sqlite3.connect("database/weather.db")

df = pd.read_sql_query(
    "SELECT * FROM weather_data ORDER BY timestamp ASC",
    conn
)

conn.close()

df = df.dropna().copy()

# convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# time features
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek

# ---------------------------
# TEMPERATURE MODEL
# ---------------------------
df["temperature_next_hour"] = df["temperature_2m"].shift(-1)
df_temp = df.dropna().copy()

temp_features = [
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "pressure_msl",
    "cloud_cover",
    "hour",
    "day_of_week",
]

X_temp = df_temp[temp_features]
y_temp = df_temp["temperature_next_hour"]

split_index = int(len(df_temp) * 0.8)

X_train_temp = X_temp.iloc[:split_index]
y_train_temp = y_temp.iloc[:split_index]

temp_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

temp_model.fit(X_train_temp, y_train_temp)

# ---------------------------
# RAIN MODEL
# ---------------------------
df["precipitation_next_hour"] = df["precipitation"].shift(-1)
df_rain = df.dropna().copy()
df_rain["rain_category_next_hour"] = df_rain["precipitation_next_hour"].apply(categorize_rain)

rain_features = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "pressure_msl",
    "cloud_cover",
    "precipitation",
    "hour",
    "day_of_week",
]

X_rain = df_rain[rain_features]
y_rain = df_rain["rain_category_next_hour"]

split_index = int(len(df_rain) * 0.8)

X_train_rain = X_rain.iloc[:split_index]
y_train_rain = y_rain.iloc[:split_index]

rain_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

rain_model.fit(X_train_rain, y_train_rain)

# ---------------------------
# Predict next hour
# ---------------------------
latest_row = df.iloc[-1]

latest_features_temp = pd.DataFrame([latest_row[temp_features]], columns=temp_features)
latest_features_rain = pd.DataFrame([latest_row[rain_features]], columns=rain_features)

predicted_temperature = temp_model.predict(latest_features_temp)[0]

rain_prediction = rain_model.predict(latest_features_rain)[0]
all_probabilities = rain_model.predict_proba(latest_features_rain)[0]
rain_probability = all_probabilities[rain_prediction] * 100

# next hour timestamp
prediction_timestamp = latest_row["timestamp"] + timedelta(hours=1)

# ---------------------------
# Store prediction
# ---------------------------
insert_prediction(
    weather_data_id=int(latest_row["id"]),
    predicted_temperature=float(predicted_temperature),
    rain_probability=float(rain_probability),
    rain_prediction=int(rain_prediction)
)

print("\nPrediction stored successfully")

print("\nPrediction summary:")
print("-------------------")
print(f"City: {latest_row['city']}")
print(f"Prediction time: {prediction_timestamp}")
print(f"Predicted temperature: {predicted_temperature:.2f} °C")
print(f"Rain category: {RAIN_LABELS[rain_prediction]}")
print(f"Model confidence: {rain_probability:.2f}%")

print("\nClass probabilities:")
for class_idx, probability in zip(rain_model.classes_, all_probabilities):
    print(f"  {RAIN_LABELS[class_idx]}: {probability * 100:.2f}%")