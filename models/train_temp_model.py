import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from models.evaluate_model import evaluate_temperature_model

# connect to database
conn = sqlite3.connect("database/weather.db")

# load data
df = pd.read_sql_query("SELECT * FROM weather_data ORDER BY city, timestamp ASC", conn)
conn.close()

print("Rows loaded:", len(df))
print(df.head())

# drop rows with missing values
df = df.dropna().copy()

# convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["hour"] = df["timestamp"].dt.hour
df["day_of_week"] = df["timestamp"].dt.dayofweek

# --- Create target per city ---
df["temperature_next_hour"] = df.groupby("city")["temperature_2m"].shift(-1)

# remove rows without next-hour target
df = df.dropna().copy()

# features
feature_cols = [
    "latitude",
    "longitude",
    "temperature_2m",
    "relative_humidity_2m",
    "precipitation",
    "wind_speed_10m",
    "pressure_msl",
    "cloud_cover",
    "hour",
    "day_of_week",
]

X = df[feature_cols]
y = df["temperature_next_hour"]

# time-based split (not random)
split_index = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# train model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

# evaluate
pred = model.predict(X_test)
evaluate_temperature_model(y_test, pred)
# show prediction vs real values
results = pd.DataFrame({
    "city": df.iloc[split_index:]["city"].values,
    "actual": y_test.values,
    "predicted": pred
})

print("\nSample predictions vs actual:")
print(results.head(10))

# predict next hour from latest row
latest_row = df.sort_values("timestamp").iloc[-1]
latest_features = X.loc[[latest_row.name]]
next_temp_pred = model.predict(latest_features)[0]

print(f"\nPredicted next hour temperature for {latest_row['city']}: {next_temp_pred:.2f} °C")