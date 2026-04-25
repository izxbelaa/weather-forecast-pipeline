from typing import Any
import requests
from requests.adapters import HTTPAdapter
from backend.config import HOURLY_VARS, API_URL, START_DATE, END_DATE
from urllib3.util.retry import Retry


REQUEST_TIMEOUT_SECONDS = 15
RETRY_TOTAL = 3


class WeatherApiError(RuntimeError):
    """Raised when the weather API cannot provide a valid response."""


def _build_session() -> requests.Session:
    retry_strategy = Retry(
        total=RETRY_TOTAL,
        connect=RETRY_TOTAL,
        read=RETRY_TOTAL,
        status=RETRY_TOTAL,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def _validate_weather_response(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise WeatherApiError("Weather API returned a non-object JSON response.")

    if data.get("error"):
        reason = data.get("reason", "No reason provided")
        raise WeatherApiError(f"Weather API returned an error: {reason}")

    hourly = data.get("hourly")
    if not isinstance(hourly, dict):
        raise WeatherApiError("Weather API response is missing the 'hourly' object.")

    required_fields = ["time", *HOURLY_VARS]
    missing_fields = [field for field in required_fields if field not in hourly]
    if missing_fields:
        raise WeatherApiError(
            f"Weather API response is missing hourly fields: {', '.join(missing_fields)}"
        )

    expected_length = len(hourly["time"])
    if expected_length == 0:
        raise WeatherApiError("Weather API returned no hourly records.")

    invalid_lengths = {
        field: len(hourly[field])
        for field in required_fields
        if len(hourly[field]) != expected_length
    }
    if invalid_lengths:
        raise WeatherApiError(
            "Weather API returned inconsistent hourly field lengths: "
            f"{invalid_lengths}"
        )


def fetch_weather(latitude, longitude):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "auto"
    }

    try:
        response = _build_session().get(
            API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.Timeout as exc:
        raise WeatherApiError(
            f"Weather API request has timed out for coordinates ({latitude}, {longitude})."
        ) from exc
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise WeatherApiError(
            f"Weather API returned HTTP status {status_code} for coordinates "
            f"({latitude}, {longitude})."
        ) from exc
    except requests.RequestException as exc:
        raise WeatherApiError(
            f"Weather API request failed for coordinates ({latitude}, {longitude}): {exc}"
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise WeatherApiError("Weather API returned invalid JSON.") from exc

    _validate_weather_response(data)
    return data
