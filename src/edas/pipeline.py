import logging
import time
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

# --- Logging setup (non-invasive; won’t override if already configured)
log = logging.getLogger(__name__)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

NEIGHBORS: Dict[str, List[str]] = {
    "FR": ["BE", "DE", "ES", "CH"],
    "DE": ["NL", "BE", "FR", "CH", "AT", "CZ", "PL"],
}


def _load_countries(engine) -> Dict[str, Dict[str, str]]:
    sql = "SELECT country_code, country_name, zone_key FROM countries;"
    log.debug("Loading countries metadata with SQL: %s", sql)
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).mappings().all()
    meta = {r["country_code"]: {"name": r["country_name"], "zone": r["zone_key"]} for r in rows}
    log.info("Loaded %d countries from DB: %s", len(meta), list(meta.keys()))
    return meta


def _compute_range(mode: str):
    """
    Compute [start, end] in Europe/Brussels time (hourly aligned, minus 1h to avoid partial hour).
    """
    # utcnow() is tz-aware (UTC) in recent pandas; tz_convert is correct here
    now_bxl = pd.Timestamp.utcnow().tz_convert("Europe/Brussels")
    end = now_bxl.floor("h") - pd.Timedelta(hours=1)

    if mode == "last_10_days":
        start = end - pd.Timedelta(days=10)
    elif mode == "full_2025":
        start = pd.Timestamp("2025-01-01 00:00", tz="Europe/Brussels")
        end = pd.Timestamp("2025-12-31 23:00", tz="Europe/Brussels")
    else:
        raise ValueError(f"Unknown mode: {mode}")

    log.debug("Computed range for mode=%s -> start=%s, end=%s", mode, start, end)
    return start, end


def run_pipeline(
    countries: Optional[List[str]] = None,
    include_flows: bool = True,
    mode: str = "last_10_days",
):
    t0 = time.perf_counter()
    log.info(
        "Pipeline start | mode=%s | include_flows=%s | requested_countries=%s",
        mode, include_flows, countries
    )

    try:
        engine = get_engine()
        log.info("DB engine created successfully")

        meta = _load_countries(engine)

        if not countries:
            countries = ["FR", "DE"]
            log.info("No countries provided; defaulting to %s", countries)

        # Validate countries exist in metadata
        missing = [c for c in countries if c not in meta]
        if missing:
            log.warning("Some requested countries are missing in metadata: %s", missing)
            countries = [c for c in countries if c in meta]
        if not countries:
            log.error("No valid countries to process after metadata check. Aborting.")
            return

        start, end = _compute_range(mode)
        log.info("Range resolved | mode=%s :: %s → %s", mode, start, end)

        with engine.begin() as sa_conn:
            # Get raw psycopg connection for fast execute_values
            raw = sa_conn.connection.driver_connection
            log.debug("Opened transaction and acquired raw DB connection")

            # Ingestion: consumption + production
            for cc in countries:
                zone = meta[cc]["zone"]
                log.info("Fetching consumption | country=%s | zone=%s", cc, zone)
                cons = fetch_consumption(cc, zone, start, end)
                n_cons = upsert_energy_consumption(raw, cons)
                log.info("Upsert consumption | country=%s | rows=%d", cc, n_cons)

                log.info("Fetching production | country=%s | zone=%s", cc, zone)
                prod = fetch_production(cc, zone, start, end)
                n_prod = upsert_energy_production(raw, prod)
                log.info("Upsert production | country=%s | rows=%d", cc, n_prod)

            # Ingestion: cross-border flows
            if include_flows:
                for cc in countries:
                    from_zone = meta[cc]["zone"]
                    neighbors = NEIGHBORS.get(cc, [])
                    if not neighbors:
                        log.debug("No neighbors configured for %s; skipping flows", cc)
                        continue

                    for nb in neighbors:
                        if nb not in meta:
                            log.debug("Neighbor %s not present in metadata; skipping %s -> %s", nb, cc, nb)
                            continue

                        to_zone = meta[nb]["zone"]
                        log.info("Fetching flow | %s -> %s | zones: %s -> %s", cc, nb, from_zone, to_zone)
                        flow = fetch_flow(cc, nb, from_zone, to_zone, start, end)
                        n_flow = upsert_cross_border_flow(raw, flow)
                        if n_flow > 0:
                            log.info("Upsert flow | %s -> %s | rows=%d", cc, nb, n_flow)
                        else:
                            log.debug("No flow rows upserted for %s -> %s", cc, nb)

        dt = time.perf_counter() - t0
        log.info("Pipeline finished successfully in %.2fs", dt)

    except Exception as e:
        dt = time.perf_counter() - t0
        log.exception("Pipeline failed after %.2fs: %s", dt, e)
        # Re-raise so callers/CI can fail properly
        raise
