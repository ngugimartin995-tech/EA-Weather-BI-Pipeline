"""
pipeline/export_csv.py
Exports all 4 database tables to CSV files for Power BI's Web connector.

Why this exists: Power BI Service's PostgreSQL connector has a confirmed
incompatibility with Supabase's free tier — the pooler host fails strict
certificate validation during scheduled refresh, and the direct host is
unreachable because it's IPv6-only and Power BI's refresh engine can't
resolve it. Exporting to CSV and serving via plain HTTPS (GitHub raw URLs)
sidesteps both issues entirely — the Web connector has no such limitations.

Usage:
  python -m pipeline.export_csv
"""

import logging
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from db.ingest import get_engine

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger("export_csv")

EXPORT_DIR = Path(__file__).resolve().parent.parent / "powerbi_exports"
EXPORT_DIR.mkdir(exist_ok=True)

TABLES = ["cities", "weather_readings", "air_quality_readings", "daily_summaries"]


def export_all() -> None:
    """Pull each table in full from Supabase and write it to CSV."""
    engine = get_engine()

    for table in TABLES:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY 1", engine)
        out_path = EXPORT_DIR / f"{table}.csv"
        df.to_csv(out_path, index=False)
        log.info("Exported %s: %d rows → %s", table, len(df), out_path)

    log.info("Export complete: %d tables written to %s", len(TABLES), EXPORT_DIR)


if __name__ == "__main__":
    export_all()
