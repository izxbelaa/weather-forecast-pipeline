import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# === CONFIGURATION ===
CSV_FILE = "temperature_data.csv"  # Replace with your CSV file
HOURS_LOOKBACK = 23  # Look back 23 hours
TARGET_COLUMN = "temperature"  # Replace with your actual column name

# === LOAD DATA ===
data = pd.read_csv(CSV_FILE)

# Ensure we have enough rows
if len(data) < HOURS_LOOKBACK + 1:
    raise ValueError(f"Not enough data to create sliding windows. Require at least {HOURS_LOOKBACK + 1} rows, got {len(data)}.")

# === CREATE SLIDING WINDOWS ===
X, y = [], []
temps = data[TARGET_COLUMN].values

for i in range(HOURS_LOOKBACK, len(temps)):
    X.append(temps[i-HOURS_LOOKBACK:i])
    y.append(temps[i])

X = pd.DataFrame(X)
y = pd.Series(y)

# === SPLIT DATA ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === TRAIN MODEL ===
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === EVALUATE MODEL ===
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse:.3f}")

# === PREDICT NEXT HOUR ===
last_window = temps[-HOURS_LOOKBACK:].reshape(1, -1)
next_temp = model.predict(last_window)[0]
print(f"Predicted next hour temperature: {next_temp:.2f}")