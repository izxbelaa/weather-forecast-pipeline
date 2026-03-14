import sqlite3
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from models.evaluate_model import evaluate_temperature_model

# connect to database
conn = sqlite3.connect("database/weather.db")

# load data
df = pd.read_sql_query("SELECT * FROM weather_data ORDER BY timestamp ASC", conn)
conn.close()

print("Rows loaded:", len(df))
print(df.head())

# drop rows with missing values
df = df.dropna().copy()

# create target: next hour temperature
df["temperature_next_hour"] = df["temperature_2m"].shift(-1)

# remove last row because it has no next-hour target
df = df.dropna().copy()

# features
X = df[
    [
        "temperature_2m",
        "relative_humidity_2m",
        "precipitation",
        "wind_speed_10m",
        "pressure_msl",
        "cloud_cover",
    ]
]

# target
y = df["temperature_next_hour"]

# time-based split (not random)
split_index = int(len(df) * 0.8)
X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

# train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# evaluate
pred = model.predict(X_test)
evaluate_temperature_model(y_test, pred)
# show prediction vs real values
results = pd.DataFrame({
    "actual": y_test,
    "predicted": pred
})

print("\nSample predictions vs actual:")
print(results.head(10))

# predict next hour from latest row
latest_features = X.iloc[[-1]]
next_temp_pred = model.predict(latest_features)[0]
print(f"Predicted next hour temperature: {next_temp_pred:.2f} °C")