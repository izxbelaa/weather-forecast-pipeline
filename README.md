# CSE525 End-to-End Data Science

## Project Overview

This project is a real-time weather monitoring and short-term prediction
system developed for the **CSE525 Data Science** course.

The system collects weather data from the **Open-Meteo API**, stores it
in a **SQLite** database, and uses machine learning models to predict:

-   next-hour temperature
-   next-hour rain probability

An interactive dashboard is built using **Streamlit**.

------------------------------------------------------------------------

## Tech Stack

-   Python 3
-   Streamlit
-   pandas
-   SQLite
-   scikit-learn
-   Open-Meteo API

------------------------------------------------------------------------

## Project Structure

    cse525-end-to-end-data-science/
    │
    ├── backend/         # API collection scripts
    ├── database/        # SQLite schema and DB logic
    ├── frontend/        # Streamlit dashboard
    ├── models/          # ML scripts
    ├── monitoring/      # drift / performance checks
    ├── data/            # raw / processed data if needed
    │
    ├── requirements.txt
    ├── README.md
    └── .gitignore

------------------------------------------------------------------------

## Setup Instructions

### 1. Clone the repository

``` bash
git clone https://github.com/YOUR-USERNAME/weather-forecast-pipeline.git
cd weather-forecast-pipeline
```

------------------------------------------------------------------------

### 2. Create a virtual environment

``` bash
python3 -m venv venv
```

------------------------------------------------------------------------

### 3. Activate the virtual environment

#### macOS / Linux

``` bash
source venv/bin/activate
```

#### Windows

``` bash
venv\Scripts\activate
```

------------------------------------------------------------------------

### 4. Install dependencies

``` bash
pip install -r requirements.txt
```


------------------------------------------------------------------------

## Running the Streamlit UI

``` bash
streamlit run frontend/app.py
```

The dashboard will open in your browser:

http://localhost:8501

------------------------------------------------------------------------

## Phase A Goal

For Phase A the team will complete:

-   problem definition
-   research questions and hypotheses
-   API selection
-   initial database design
-   early prototype dashboard
-   baseline ML model planning

------------------------------------------------------------------------

## Important Notes

-   Use the project virtual environment
-   Do not commit the `venv/` folder
-   Keep `requirements.txt` updated
-   Push code regularly so commit history shows team contributions
-   Do not change database schema without informing the team

------------------------------------------------------------------------

## Data Source

Open-Meteo Weather API

Initial location: Limassol, Cyprus

------------------------------------------------------------------------


