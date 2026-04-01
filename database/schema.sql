CREATE TABLE IF NOT EXISTS weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    temperature_2m REAL,
    relative_humidity_2m REAL,
    precipitation REAL,
    wind_speed_10m REAL,
    pressure_msl REAL,
    cloud_cover REAL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city, timestamp)
);
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    weather_data_id INTEGER,

    predicted_temperature REAL,
    rain_probability REAL,
    rain_prediction INTEGER,

    created_at TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (weather_data_id) REFERENCES weather_data(id)
);