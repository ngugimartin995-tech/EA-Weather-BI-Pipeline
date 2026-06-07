"""
collectors/config.py
Shared configuration: target cities, API base URL, output paths.
"""

from pathlib import Path

# ── Target cities ──────────────────────────────────────────────────────────
CITIES = [
    {"name": "Nairobi",        "country": "KE", "lat": -1.2864, "lon": 36.8172},
    {"name": "Mombasa",        "country": "KE", "lat": -4.0435, "lon": 39.6682},
    {"name": "Kampala",        "country": "UG", "lat":  0.3476, "lon": 32.5825},
    {"name": "Dar es Salaam",  "country": "TZ", "lat": -6.7924, "lon": 39.2083},
]

# ── API ────────────────────────────────────────────────────────────────────
OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Seconds to wait between city requests to stay well under rate limits
REQUEST_DELAY = 1.0

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR      = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
