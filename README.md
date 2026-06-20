# 🌍 EAWeather BI Pipeline
### East Africa Urban Climate Intelligence — End-to-End ETL/BI System

> A complete Business Intelligence pipeline collecting real-time weather and air quality data across East African cities, cleaning and storing it in PostgreSQL, orchestrating automated refresh cycles via Apache Airflow, and delivering actionable insights through interactive Jupyter/Plotly dashboards.

---

## 📌 Business Case

East African cities — **Nairobi, Mombasa, Kampala, and Dar es Salaam** — face growing challenges from urban air pollution and unpredictable weather variability. Public health officials, city planners, logistics companies, and agricultural stakeholders lack a centralized, real-time intelligence platform to inform time-sensitive decisions based on environmental conditions.

**This pipeline solves that.**

| Stakeholder | Value Delivered |
|---|---|
| Public health officials | Track AQI spikes and issue timely warnings |
| Urban planners | Correlate weather patterns with infrastructure needs |
| Logistics companies | Plan routes around weather disruptions |
| Agricultural stakeholders | Monitor humidity/temperature for crop decisions |
| Researchers | Access clean historical climate datasets for East African cities |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          DATA SOURCES                           │
│  OpenWeatherMap API          IQAir / AirVisual API              │
│  (weather: temp, humidity,   (air quality: AQI, PM2.5,          │
│   wind, description)          PM10, CO, O3)                     │
└────────────────┬────────────────────────────┬───────────────────┘
                 │                            │
                 ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     COLLECTION LAYER                            │
│  collectors/weather.py          collectors/airquality.py        │
│  → raw JSON → /data/raw/        → raw JSON → /data/raw/         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CLEANING & TRANSFORM                          │
│  cleaning/clean_weather.py    cleaning/clean_airquality.py      │
│  Pandas: flatten, normalize, validate, deduplicate              │
│  → /data/processed/*.csv                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE                           │
│  cities | weather_readings | air_quality_readings | daily_summaries │
│  SQLAlchemy ORM + upsert logic (ON CONFLICT DO NOTHING)         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│               APACHE AIRFLOW ORCHESTRATION                      │
│  weather_dag.py (hourly)    airquality_dag.py (every 3h)        │
│  daily_summary_dag.py (daily aggregate)                         │
│  Email alerts on failure | Retry: 3x with 5min backoff          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              ANALYSIS & VISUALIZATION                           │
│  notebooks/01_eda.ipynb         notebooks/02_dashboard.ipynb    │
│  Plotly interactive charts | City comparisons | AQI trends      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Data Collection | Python `requests` | Call OpenWeatherMap + IQAir APIs |
| Data Cleaning | `pandas`, `numpy` | Flatten JSON, normalize, validate |
| Data Storage | **PostgreSQL** | Structured relational storage |
| ORM / DB | `SQLAlchemy`, `psycopg2` | Connection pooling, upsert logic |
| Orchestration | **Apache Airflow** | Scheduled DAGs, alerts on failure |
| Visualization | `Jupyter`, `plotly` | Interactive dashboards |
| Containerization | **Docker** + `docker-compose` | Reproducible environments |
| ML (Bonus) | `scikit-learn` | AQI regression predictor |
| Notifications | `smtplib` / Airflow SMTP | Alert when AQI > 150 |
| Env Management | `venv` + `python-dotenv` | Secrets management |

---

## 📂 Project Structure

```
eaweather-bi-pipeline/
├── collectors/                 # API fetch scripts
│   ├── weather.py              # OpenWeatherMap collector (4 cities)
│   └── airquality.py           # IQAir/AirVisual collector (4 cities)
├── cleaning/                   # Pandas transformation layer
│   ├── clean_weather.py
│   └── clean_airquality.py
├── db/                         # Database layer
│   ├── schema.sql              # PostgreSQL DDL
│   ├── models.py               # SQLAlchemy ORM models
│   └── ingest.py               # Upsert & loading logic
├── pipeline/
│   └── run_pipeline.py         # Single entry point: collect → clean → ingest
├── airflow/
│   └── dags/
│       ├── weather_dag.py
│       ├── airquality_dag.py
│       └── daily_summary_dag.py
├── notebooks/
│   ├── 01_eda.ipynb            # Exploratory data analysis
│   └── 02_dashboard.ipynb      # Interactive Plotly dashboard
├── ml/
│   └── aqi_model.py            # [BONUS] RandomForest AQI predictor
├── data/
│   ├── raw/                    # Raw API JSON (gitignored)
│   └── processed/              # Cleaned CSVs (gitignored)
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚡ Quickstart

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 15+ (local or [Supabase](https://supabase.com) free tier)
- Apache Airflow 2.8+
- Docker & docker-compose (optional, for containerized run)

### 2. Clone & Set Up Environment

```bash
git clone https://github.com/<your-username>/eaweather-bi-pipeline.git
cd eaweather-bi-pipeline

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure Secrets

```bash
cp .env.example .env
# Edit .env with your actual values:
nano .env
```

Required variables (see `.env.example` for descriptions):

```env
OWM_API_KEY=your_openweathermap_key
IQAIR_API_KEY=your_iqair_key
DB_HOST=localhost
DB_PORT=5432
DB_NAME=eaweather
DB_USER=your_db_user
DB_PASSWORD=your_db_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=alerts@yourdomain.com
```

### 4. Initialize Database

```bash
psql -U $DB_USER -c "CREATE DATABASE eaweather;"
psql -U $DB_USER -d eaweather -f db/schema.sql
```

### 5. Run the Pipeline (Manual)

```bash
python pipeline/run_pipeline.py
# With options:
python pipeline/run_pipeline.py --city nairobi --mode full
```

### 6. Start Airflow

```bash
export AIRFLOW_HOME=$(pwd)/airflow
airflow db init
airflow users create --username admin --password admin \
    --firstname Admin --lastname User --role Admin --email admin@example.com

# Copy DAGs
cp airflow/dags/*.py $AIRFLOW_HOME/dags/

# Start scheduler + webserver
airflow scheduler &
airflow webserver --port 8080
```

Access the Airflow UI at `http://localhost:8080` and trigger the DAGs.

### 7. Open Dashboards

```bash
jupyter notebook notebooks/
```

Open `01_eda.ipynb` for exploratory analysis and `02_dashboard.ipynb` for interactive Plotly charts.

---

## 🐳 Docker (Bonus)

```bash
docker-compose up --build
```

This spins up:
- `pipeline` service — runs the ETL on startup
- `postgres` service — PostgreSQL 15 with initialized schema

---

## 🗄️ Database Schema

```sql
-- Target cities registry
CREATE TABLE cities (
    city_id   SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    country   VARCHAR(100) NOT NULL,
    latitude  FLOAT NOT NULL,
    longitude FLOAT NOT NULL
);

-- Hourly weather readings
CREATE TABLE weather_readings (
    reading_id      SERIAL PRIMARY KEY,
    city_id         INT REFERENCES cities(city_id),
    recorded_at     TIMESTAMPTZ NOT NULL,
    temperature_c   FLOAT,
    humidity_pct    FLOAT,
    wind_speed_ms   FLOAT,
    weather_desc    VARCHAR(200),
    UNIQUE (city_id, recorded_at)
);

-- 3-hourly air quality readings
CREATE TABLE air_quality_readings (
    reading_id  SERIAL PRIMARY KEY,
    city_id     INT REFERENCES cities(city_id),
    recorded_at TIMESTAMPTZ NOT NULL,
    aqi         INT,
    pm25        FLOAT,
    pm10        FLOAT,
    co          FLOAT,
    o3          FLOAT,
    UNIQUE (city_id, recorded_at)
);

-- Daily aggregated summaries (populated by Airflow)
CREATE TABLE daily_summaries (
    summary_id  SERIAL PRIMARY KEY,
    city_id     INT REFERENCES cities(city_id),
    summary_date DATE NOT NULL,
    avg_temp_c  FLOAT,
    avg_aqi     FLOAT,
    max_aqi     INT,
    min_temp_c  FLOAT,
    UNIQUE (city_id, summary_date)
);
```

---

## 📡 API Notes

### OpenWeatherMap
- **Signup:** [openweathermap.org/api](https://openweathermap.org/api) — free tier, 1,000 calls/day
- **Endpoint:** `GET api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={key}`
- **Tip:** Always use `&units=metric` to get Celsius directly

### IQAir / AirVisual
- **Signup:** [iqair.com/world-air-quality](https://www.iqair.com/world-air-quality) — free Community tier, 10,000 calls/month
- **Endpoint:** `GET api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={key}`
- **Tip:** City/state/country must match IQAir's naming — use `/countries` → `/states` → `/cities` endpoints to discover valid names

---

## 🤖 ML Model (Bonus)

Located in `ml/aqi_model.py`. Trains a `RandomForestRegressor` to predict AQI from weather variables:

- **Features:** `temperature_c`, `humidity_pct`, `wind_speed_ms`
- **Target:** `aqi`
- **Evaluation:** MAE, R² score
- **Output:** `ml/model.pkl` (saved via joblib)

```bash
python ml/aqi_model.py
```

---

## 🔔 Alerts

A notification fires via SMTP when `MAX(aqi)` for any city exceeds **150** (EPA "Unhealthy" threshold). Configured in `airflow/dags/airquality_dag.py` and via `SMTP_*` env variables.

---

## 📊 Visualizations

The `notebooks/02_dashboard.ipynb` produces:

1. **AQI Time Series** — all 4 cities on one interactive Plotly chart (last 30 days)
2. **City AQI Map** — Plotly scatter_mapbox with AQI severity as marker size
3. **Temperature Comparison** — daily average bar chart by city
4. **AQI Health Breakdown** — pie chart: Good / Moderate / Unhealthy / Hazardous
5. **Correlation Heatmap** — temp vs humidity vs AQI vs wind speed

---

## 📦 Requirements

```
requests>=2.31
pandas>=2.1
numpy>=1.26
sqlalchemy>=2.0
psycopg2-binary>=2.9
python-dotenv>=1.0
apache-airflow>=2.8
plotly>=5.18
scikit-learn>=1.3
jupyter>=1.0
ipykernel>=6.26
joblib>=1.3
pytz>=2023.3
```

---

## 🗺️ Target Cities

25 cities across East and Central Africa. The original 4 (Nairobi, Mombasa,
Kampala, Dar es Salaam) are kept first in `collectors/config.py` and
`db/schema.sql` so existing data continuity is preserved.

| City | Country | Latitude | Longitude |
|---|---|---|---|
| Nairobi | Kenya | -1.2864 | 36.8172 |
| Mombasa | Kenya | -4.0435 | 39.6682 |
| Kisumu | Kenya | -0.0917 | 34.7680 |
| Kampala | Uganda | 0.3476 | 32.5825 |
| Dar es Salaam | Tanzania | -6.7924 | 39.2083 |
| Dodoma | Tanzania | -6.1630 | 35.7516 |
| Arusha | Tanzania | -3.3869 | 36.6830 |
| Kigali | Rwanda | -1.9441 | 30.0619 |
| Bujumbura | Burundi | -3.3614 | 29.3599 |
| Juba | South Sudan | 4.8594 | 31.5713 |
| Addis Ababa | Ethiopia | 9.0301 | 38.7400 |
| Dire Dawa | Ethiopia | 9.5931 | 41.8500 |
| Mogadishu | Somalia | 2.0469 | 45.3182 |
| Djibouti City | Djibouti | 11.5886 | 43.1456 |
| Asmara | Eritrea | 15.3229 | 38.9251 |
| Kinshasa | DR Congo | -4.4419 | 15.2663 |
| Lubumbashi | DR Congo | -11.6609 | 27.4794 |
| Goma | DR Congo | -1.6792 | 29.2228 |
| Brazzaville | Rep. of Congo | -4.2634 | 15.2429 |
| Yaoundé | Cameroon | 3.8480 | 11.5021 |
| Douala | Cameroon | 4.0511 | 9.7679 |
| Bangui | Central African Rep. | 4.3947 | 18.5582 |
| N'Djamena | Chad | 12.1348 | 15.0557 |
| Libreville | Gabon | 0.4162 | 9.4673 |
| Malabo | Equatorial Guinea | 3.7523 | 8.7741 |

**OWM free tier rate limit check:** 25 cities × 24 hourly weather calls/day
= 600 calls/day. 25 cities × 8 AQI calls/day (every 3h) = 200 calls/day.
**Total: ~800 calls/day**, under the 1,000/day free tier limit — but with
limited headroom for manual `workflow_dispatch` runs. Monitor usage at
[openweathermap.org/price](https://openweathermap.org/price) if adding more cities.

---

## 📋 Submission Checklist

- [ ] GitHub repository is public with clear commit history
- [ ] README renders correctly on GitHub
- [ ] All 4 PostgreSQL tables created and populated with real data
- [ ] Airflow DAGs run without errors (screenshots in README)
- [ ] Jupyter notebooks run top-to-bottom without errors
- [ ] Architecture slides (3 slides) prepared
- [ ] `requirements.txt` allows clean install from scratch
- [ ] `.env.example` documents all secrets (no actual keys committed)
- [ ] Docker `docker-compose up` builds and runs successfully
- [ ] ML model trained and `model.pkl` exists
- [ ] Demo script rehearsed (< 10 minutes)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for the ETL/BI Pipeline Project.*
