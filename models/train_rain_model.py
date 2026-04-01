import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from models.evaluate_model import evaluate_rain_model


def categorize_rain(precip):
    if precip == 0:
        return 0  # No Rain
    elif precip <= 2.5:
        return 1  # Light Rain
    else:
        return 2  # Moderate/Heavy Rain


RAIN_LABELS = {
    0: "No Rain",
    1: "Light Rain",
    2: "Moderate/Heavy Rain",
}

# --- Load data ---
conn = sqlite3.connect("database/weather.db")
df = pd.read_sql_query("SELECT * FROM weather_data ORDER BY city, timestamp ASC", conn)
conn.close()
df = df.dropna().copy()

# --- Convert timestamp to time features ---
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek

# --- Create target per city ---
df["precipitation_next_hour"] = df.groupby("city")["precipitation"].shift(-1)
df = df.dropna().copy()
df["rain_category_next_hour"] = df["precipitation_next_hour"].apply(categorize_rain)

print("\nRain category distribution:")
counts = df["rain_category_next_hour"].value_counts().sort_index()
for class_id, count in counts.items():
    print(f"{RAIN_LABELS[class_id]}: {count}")

# --- Features ---
feature_cols = [
    "latitude",
    "longitude",
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
y = df["rain_category_next_hour"]

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
pred_proba = model.predict_proba(X_test)

# --- Evaluate ---
evaluate_rain_model(y_test, pred)

# --- Sample predictions ---
results = pd.DataFrame({
    "city": df.iloc[split_index:]["city"].values,
    "actual": y_test.map(RAIN_LABELS).values,
    "predicted": pd.Series(pred, index=y_test.index).map(RAIN_LABELS).values,
})

print("\nSample predictions vs actual:")
print(results.head(10))

# --- Predict next hour for latest overall row ---
latest_row = df.sort_values("timestamp").iloc[-1]
latest_features = X.loc[[latest_row.name]]

next_rain_pred = model.predict(latest_features)[0]
next_rain_proba = model.predict_proba(latest_features)[0]

print(f"\nPredicted next hour rain category for {latest_row['city']}: {RAIN_LABELS[next_rain_pred]}")
print("Class probabilities:")
for class_idx, probability in zip(model.classes_, next_rain_proba):
    print(f"  {RAIN_LABELS[class_idx]}: {probability * 100:.2f}%")