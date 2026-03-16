import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from models.evaluate_model import evaluate_rain_model

# --- Load data ---
conn = sqlite3.connect("database/weather.db")
df = pd.read_sql_query("SELECT * FROM weather_data ORDER BY timestamp ASC", conn)
conn.close()
df = df.dropna().copy()

# --- Create binary target: rain or no rain next hour ---
df["rain_next_hour"] = (df["precipitation"].shift(-1) > 0).astype(int)
df["precipitation_next_hour"] = df["precipitation"].shift(-1)
df = df.dropna().copy()

# --- Features ---
feature_cols = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "pressure_msl",
    "cloud_cover",
    "precipitation"
]
X = df[feature_cols]

# --- Targets ---
y_reg = df["precipitation_next_hour"]   # regression target
y_clf = df["rain_next_hour"]            # classification target

# --- Time-based split ---
split_index = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train_reg, y_test_reg = y_reg.iloc[:split_index], y_reg.iloc[split_index:]
y_train_clf, y_test_clf = y_clf.iloc[:split_index], y_clf.iloc[split_index:]

# --- Train classifier to predict rain / no rain ---
clf_model = RandomForestClassifier(n_estimators=100, random_state=42)
clf_model.fit(X_train, y_train_clf)

# --- Train regressor on only hours where it rains ---
X_train_rain = X_train[y_train_clf == 1]
y_train_rain = y_train_reg[y_train_clf == 1]

reg_model = RandomForestRegressor(n_estimators=100, random_state=42)
reg_model.fit(X_train_rain, y_train_rain)

# --- Predict on test set ---
pred_rain = clf_model.predict(X_test)
pred_reg = reg_model.predict(X_test)  # regression predicts mm for rain only

# Combine: if classifier says no rain, set prediction to 0
pred_final = [reg if rain==1 else 0 for reg, rain in zip(pred_reg, pred_rain)]

# --- Evaluate ---
evaluate_rain_model(y_test_reg, pred_final)

# --- Sample predictions ---
results = pd.DataFrame({
    "actual": y_test_reg,
    "predicted": pred_final
})
print("\nSample predictions vs actual:")
print(results.head(10))

# --- Predict next hour from latest row ---
latest_features = X.iloc[[-1]]
next_rain_pred = clf_model.predict(latest_features)[0]
if next_rain_pred == 1:
    next_precip = reg_model.predict(latest_features)[0]
else:
    next_precip = 0.0

print(f"\nPredicted next hour precipitation: {next_precip:.2f} mm")

manual_test_data = [
    # Rainy morning, light rain
    {
        "temperature_2m": 16.0,
        "relative_humidity_2m": 92.0,
        "wind_speed_10m": 3.0,
        "pressure_msl": 1008.0,
        "cloud_cover": 95.0,
        "precipitation": 1.0
    },
    # Rainy afternoon, moderate rain
    {
        "temperature_2m": 18.0,
        "relative_humidity_2m": 95.0,
        "wind_speed_10m": 4.0,
        "pressure_msl": 1005.0,
        "cloud_cover": 100.0,
        "precipitation": 2.0
    },
    # Heavy rain with strong winds
    {
        "temperature_2m": 20.0,
        "relative_humidity_2m": 98.0,
        "wind_speed_10m": 6.0,
        "pressure_msl": 1002.0,
        "cloud_cover": 100.0,
        "precipitation": 5.0
    },
    # Steady rain with high humidity
    {
        "temperature_2m": 19.0,
        "relative_humidity_2m": 96.0,
        "wind_speed_10m": 3.0,
        "pressure_msl": 1004.0,
        "cloud_cover": 100.0,
        "precipitation": 3.0
    },
    # Rainstorm, very high humidity
    {
        "temperature_2m": 17.0,
        "relative_humidity_2m": 99.0,
        "wind_speed_10m": 5.0,
        "pressure_msl": 1001.0,
        "cloud_cover": 100.0,
        "precipitation": 6.0
    },
    # Drizzle, low temperature
    {
        "temperature_2m": 14.0,
        "relative_humidity_2m": 95.0,
        "wind_speed_10m": 2.0,
        "pressure_msl": 1007.0,
        "cloud_cover": 90.0,
        "precipitation": 0.5
    },
    # Evening storm
    {
        "temperature_2m": 15.0,
        "relative_humidity_2m": 97.0,
        "wind_speed_10m": 7.0,
        "pressure_msl": 1003.0,
        "cloud_cover": 100.0,
        "precipitation": 4.0
    }
]

print("\n--- Manual Test Predictions ---")
for i, row in enumerate(manual_test_data, 1):
    manual_row = pd.DataFrame([row])
    rain_pred = clf_model.predict(manual_row)[0]
    if rain_pred == 1:
        precip_pred = reg_model.predict(manual_row)[0]
    else:
        precip_pred = 0.0
    print(f"Test case {i}: Predicted precipitation = {precip_pred:.2f} mm")