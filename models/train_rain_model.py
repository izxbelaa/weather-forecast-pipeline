import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from models.evaluate_model import evaluate_rain_model

# --- Load data ---
conn = sqlite3.connect("database/weather.db")
df = pd.read_sql_query("SELECT * FROM weather_data ORDER BY timestamp ASC", conn)
conn.close()
df = df.dropna().copy()

# --- Convert timestamp to time features ---
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek

# --- Create binary target: rain next hour (0 = no, 1 = yes) ---
df["rain_next_hour"] = (df["precipitation"].shift(-1) > 0).astype(int)

# remove last row because it has no next-hour target
df = df.dropna().copy()

# --- Features ---
feature_cols = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "pressure_msl",
    "cloud_cover",
    "precipitation",
    "hour",
    "day_of_week",
]

X = df[feature_cols]
y = df["rain_next_hour"]

# --- Time-based split ---
split_index = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# --- Train classifier ---
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight="balanced"
)

model.fit(X_train, y_train)

# --- Predict on test set ---
pred = model.predict(X_test)
pred_proba = model.predict_proba(X_test)[:, 1]

# --- Evaluate ---
evaluate_rain_model(y_test, pred)

# --- Sample predictions ---
results = pd.DataFrame({
    "actual": y_test,
    "predicted": pred,
    "rain_probability_percent": (pred_proba * 100).round(2)
})

print("\nSample predictions vs actual:")
print(results.head(10))

# --- Predict next hour from latest row ---
latest_features = X.iloc[[-1]]

next_rain_pred = model.predict(latest_features)[0]
next_rain_proba = model.predict_proba(latest_features)[0][1] * 100

rain_label = "Yes" if next_rain_pred == 1 else "No"

print(f"\nPredicted next hour rain: {rain_label}")
print(f"Rain probability: {next_rain_proba:.2f}%")