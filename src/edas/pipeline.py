import logging
from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import text

from edas.db.connection import get_engine
from edas.ingestion.entsoe_client import (
    fetch_consumption, fetch_production, fetch_flow
)
from edas.ingestion.upsert import (
    upsert_energy_consumption, upsert_energy_production, upsert_cross_border_flow
)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# همسایه‌ها برای FR و DE
NEIGHBORS: Dict[str, List[str]] = {
    "FR": ["BE", "DE", "ES", "CH"],
    "DE": ["NL", "BE", "FR", "CH", "AT", "CZ", "PL"],
}

def _load_countries(engine) -> Dict[str, Dict[str, str]]:
    sql = "SELECT country_code, country_name, zone_key FROM countries;"
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).mappings().all()
    return {r["country_code"]: {"name": r["country_name"], "zone": r["zone_key"]} for r in rows}

def _compute_range(mode: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    if mode == "full_2025":
        start = pd.Timestamp("2025-01-01 00:00:00", tz="Europe/Brussels")
        end   = pd.Timestamp("2026-01-01 00:00:00", tz="Europe/Brussels")
    elif mode == "last_10_days":
        end = pd.Timestamp.utcnow().tz_localize("UTC").tz_convert("Europe/Brussels")
        start = end - pd.Timedelta(days=10)
    else:
        raise ValueError("mode must be one of: full_2025, last_10_days")
    return start, end

def run_pipeline(countries: Optional[List[str]] = None, include_flows: bool = True, mode: str = "last_10_days"):
    engine = get_engine()
    meta = _load_countries(engine)

    if not countries:
        countries = ["FR", "DE"]

    start, end = _compute_range(mode)
    log.info("Range mode=%s :: %s → %s", mode, start, end)

    with engine.begin() as sa_conn:
        raw = sa_conn.connection.driver_connection  # psycopg3 raw connection

        # consumption + production
        for cc in countries:
            zone = meta[cc]["zone"]
            cons = fetch_consumption(cc, zone, start, end)
            n = upsert_energy_consumption(raw, cons)
            log.info("cons %s rows=%d", cc, n)

            prod = fetch_production(cc, zone, start, end)
            n = upsert_energy_production(raw, prod)
            log.info("prod %s rows=%d", cc, n)

        # flows
        if include_flows:
            for cc in countries:
                from_zone = meta[cc]["zone"]
                for nb in NEIGHBORS.get(cc, []):
                    if nb not in meta:
                        continue
                    to_zone = meta[nb]["zone"]
                    flow = fetch_flow(cc, nb, from_zone, to_zone, start, end)
                    n = upsert_cross_border_flow(raw, flow)
                    if n > 0:
                        log.info("flow %s->%s rows=%d", cc, nb, n)

    log.info("Pipeline finished.")
