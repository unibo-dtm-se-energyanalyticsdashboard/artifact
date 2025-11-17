import logging
import time
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import text

# --- Import Adapters and Repository Logic ---
# Import the database connection factory (DB Adapter)
from edas.db.connection import get_engine
# Import the data fetching functions (External API Adapter)
from edas.ingestion.entsoe_client import (
    fetch_consumption, fetch_production, fetch_flow
)
# Import the database writing functions (Repository Pattern Logic)
from edas.ingestion.upsert import (
    upsert_energy_consumption, upsert_energy_production, upsert_cross_border_flow
)

# --- Logging setup ---
log = logging.getLogger(__name__)
# The fallback basicConfig was removed. 
# Logging is now expected to be configured by the entry point (e.g., cli.py or ingest.py).

# --- Domain-specific Configuration ---
# Defines the cross-border relationships to query
NEIGHBORS: Dict[str, List[str]] = {
    "FR": ["BE", "DE", "ES", "CH"],
    "DE": ["NL", "BE", "FR", "CH", "AT", "CZ", "PL"],
}


def _load_countries(engine) -> Dict[str, Dict[str, str]]:
    """Helper function to load country metadata (name, zone key) from the DB."""
    sql = "SELECT country_code, country_name, zone_key FROM countries;"
    log.debug("Loading countries metadata with SQL: %s", sql)
    with engine.connect() as conn:
        # Fetch all rows and convert them to a list of mapping (dict) objects
        rows = conn.execute(text(sql)).mappings().all()
    # Restructure the list of rows into a dictionary keyed by country_code
    meta = {r["country_code"]: {"name": r["country_name"], "zone": r["zone_key"]} for r in rows}
    log.info("Loaded %d countries from DB: %s", len(meta), list(meta.keys()))
    return meta


def _compute_range(mode: str):
    """
    Compute [start, end] in 'Europe/Brussels' time (hourly aligned).
    The 'end' timestamp is offset by 1 hour to avoid fetching partial (current) hour data.
    """
    # Get current time in UTC (timezone-aware)
    now_bxl = pd.Timestamp.utcnow().tz_convert("Europe/Brussels")
    # Floor to the current hour (e.g., 10:46 PM -> 10:00 PM) and subtract 1h
    end = now_bxl.floor("h") - pd.Timedelta(hours=1)

    if mode == "last_10_days":
        start = end - pd.Timedelta(days=10)
    elif mode == "full_2025":
        # Specific mode for fetching the required project data range
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
    """
    Main Application Service function to run the full ingestion pipeline.
    
    This function orchestrates the ETL process:
    1. Connects to the DB and loads metadata.
    2. Computes the time range.
    3. Loops through countries, fetching data from the ENTSO-E adapter.
    4. Saves data using the batch upsert (Repository) functions.
    5. All DB operations are performed within a single transaction.
    """
    t0 = time.perf_counter() # Start performance timer
    log.info(
        "Pipeline start | mode=%s | include_flows=%s | requested_countries=%s",
        mode, include_flows, countries
    )

    try:
        # 1. Initialize DB connection
        engine = get_engine()
        log.info("DB engine created successfully")

        # 2. Load country metadata (zone keys) from the DB
        meta = _load_countries(engine)

        # 3. Set and validate countries to process
        if not countries:
            countries = ["FR", "DE"] # Default to project requirements
            log.info("No countries provided; defaulting to %s", countries)

        # Validate that requested countries exist in our metadata table
        missing = [c for c in countries if c not in meta]
        if missing:
            log.warning("Some requested countries are missing in metadata: %s", missing)
            countries = [c for c in countries if c in meta]
        if not countries:
            log.error("No valid countries to process after metadata check. Aborting.")
            return

        # 4. Compute the query time range
        start, end = _compute_range(mode)
        log.info("Range resolved | mode=%s :: %s → %s", mode, start, end)

        # 5. Execute the ingestion within a single transaction
        with engine.begin() as sa_conn:
            # Get the raw psycopg2 connection for fast batch upserting
            raw = sa_conn.connection.driver_connection
            log.debug("Opened transaction and acquired raw DB connection")

            # --- Ingestion: Consumption + Production ---
            for cc in countries:
                zone = meta[cc]["zone"]
                
                # Fetch Consumption data
                log.info("Fetching consumption | country=%s | zone=%s", cc, zone)
                cons = fetch_consumption(cc, zone, start, end)
                # Upsert Consumption data
                n_cons = upsert_energy_consumption(raw, cons)
                log.info("Upsert consumption | country=%s | rows=%d", cc, n_cons)

                # Fetch Production data
                log.info("Fetching production | country=%s | zone=%s", cc, zone)
                prod = fetch_production(cc, zone, start, end)
                # Upsert Production data
                n_prod = upsert_energy_production(raw, prod)
                log.info("Upsert production | country=%s | rows=%d", cc, n_prod)

            # --- Ingestion: Cross-Border Flows (Optional) ---
            if include_flows:
                for cc in countries:
                    from_zone = meta[cc]["zone"]
                    neighbors = NEIGHBORS.get(cc, [])
                    if not neighbors:
                        log.debug("No neighbors configured for %s; skipping flows", cc)
                        continue

                    for nb in neighbors:
                        # Ensure the neighbor country is also in our metadata
                        if nb not in meta:
                            log.debug("Neighbor %s not present in metadata; skipping %s -> %s", nb, cc, nb)
                            continue
                        
                        to_zone = meta[nb]["zone"]
                        log.info("Fetching flow | %s -> %s | zones: %s -> %s", cc, nb, from_zone, to_zone)
                        # Fetch flow data
                        flow = fetch_flow(cc, nb, from_zone, to_zone, start, end)
                        # Upsert flow data
                        n_flow = upsert_cross_border_flow(raw, flow)
                        if n_flow > 0:
                            log.info("Upsert flow | %s -> %s | rows=%d", cc, nb, n_flow)
                        else:
                            log.debug("No flow rows upserted for %s -> %s", cc, nb)
        
        # Transaction commits automatically here if 'with' block succeeds
        dt = time.perf_counter() - t0
        log.info("Pipeline finished successfully in %.2fs", dt)

    except Exception as e:
        # Transaction automatically rolls back if an exception occurs
        dt = time.perf_counter() - t0
        log.exception("Pipeline failed after %.2fs: %s", dt, e)
        # Re-raise so callers (like CLI or CI) can fail properly
        raise