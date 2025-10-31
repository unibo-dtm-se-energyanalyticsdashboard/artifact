from typing import List, Dict, Any
import pandas as pd
from sqlalchemy import text
from edas.db.connection import get_engine

# ── Shared engine (reused by all query helpers)
_engine = None
def _engine():
    global _engine
    if _engine is None:
        _engine = get_engine()
    return _engine

# ── Helpers
def _params(countries: List[str], start: str, end: str) -> Dict[str, Any]:
    return {"countries": countries, "start": start, "end": end}

def consumption_vs_production(countries: List[str], start: str, end: str) -> pd.DataFrame:
    with _engine().connect() as conn:
        cons = pd.read_sql(
            text("""
                SELECT time_stamp, SUM(consumption_mw) AS consumption_mw
                FROM energy_consumption
                WHERE country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                GROUP BY time_stamp
                ORDER BY time_stamp
            """), conn, params=_params(countries, start, end)
        )
        prod = pd.read_sql(
            text("""
                SELECT time_stamp, SUM(production_mw) AS production_mw
                FROM energy_production
                WHERE country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                GROUP BY time_stamp
                ORDER BY time_stamp
            """), conn, params=_params(countries, start, end)
        )
    return pd.merge(cons, prod, on="time_stamp", how="outer").sort_values("time_stamp")

def kpis(countries: List[str], start: str, end: str) -> Dict[str, Any]:
    with _engine().connect() as conn:
        cons = pd.read_sql(
            text("""
                SELECT time_stamp, SUM(consumption_mw) AS consumption_mw
                FROM energy_consumption
                WHERE country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                GROUP BY time_stamp
            """), conn, params=_params(countries, start, end)
        )
        prod = pd.read_sql(
            text("""
                SELECT time_stamp, SUM(production_mw) AS production_mw
                FROM energy_production
                WHERE country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                GROUP BY time_stamp
            """), conn, params=_params(countries, start, end)
        )
        mix = pd.read_sql(
            text("""
                SELECT source_type, SUM(production_mw) AS production_mw
                FROM energy_production
                WHERE country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                GROUP BY source_type
                ORDER BY source_type
            """), conn, params=_params(countries, start, end)
        )

    total_cons = cons["consumption_mw"].sum()
    total_prod = prod["production_mw"].sum()

    cons["day"] = pd.to_datetime(cons["time_stamp"]).dt.to_period("D")
    cons["week"] = pd.to_datetime(cons["time_stamp"]).dt.to_period("W")
    cons["month"] = pd.to_datetime(cons["time_stamp"]).dt.to_period("M")

    avg_daily  = cons.groupby("day")["consumption_mw"].sum().mean() if not cons.empty else 0.0
    avg_weekly = cons.groupby("week")["consumption_mw"].sum().mean() if not cons.empty else 0.0
    avg_monthly= cons.groupby("month")["consumption_mw"].sum().mean() if not cons.empty else 0.0

    if not mix.empty:
        mix["percent"] = (mix["production_mw"] / mix["production_mw"].sum()) * 100
    else:
        mix["percent"] = []

    return {
        "total_consumption": float(total_cons or 0),
        "total_production": float(total_prod or 0),
        "avg_daily_consumption": float(avg_daily or 0),
        "avg_weekly_consumption": float(avg_weekly or 0),
        "avg_monthly_consumption": float(avg_monthly or 0),
        "energy_mix": mix,
    }

def production_mix(countries: List[str], start: str, end: str) -> pd.DataFrame:
    with _engine().connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT time_stamp, source_type, SUM(production_mw) AS production_mw
                FROM energy_production
                WHERE country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                GROUP BY time_stamp, source_type
                ORDER BY time_stamp
            """), conn, params=_params(countries, start, end)
        )
    return df

def crossborder_flows(countries: List[str], start: str, end: str) -> pd.DataFrame:
    with _engine().connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT from_country_code, to_country_code, time_stamp, SUM(flow_mw) AS flow_mw
                FROM cross_border_flow
                WHERE from_country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                GROUP BY from_country_code, to_country_code, time_stamp
                ORDER BY time_stamp
            """), conn, params=_params(countries, start, end)
        )
    return df

def hourly_consumption(countries: List[str], start: str, end: str) -> pd.DataFrame:
    with _engine().connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT time_stamp, SUM(consumption_mw) AS consumption_mw
                FROM energy_consumption
                WHERE country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                GROUP BY time_stamp
                ORDER BY time_stamp
            """), conn, params=_params(countries, start, end)
        )
    df["hour"] = pd.to_datetime(df["time_stamp"]).dt.hour
    df["day"]  = pd.to_datetime(df["time_stamp"]).dt.day_name()
    return df

def daily_summary(countries: List[str], start: str, end: str) -> pd.DataFrame:
    with _engine().connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT date_trunc('day', c.time_stamp) AS day,
                       SUM(c.consumption_mw) AS total_consumption,
                       SUM(p.production_mw) AS total_production,
                       SUM(p.production_mw) - SUM(c.consumption_mw) AS net_balance
                FROM energy_consumption c
                JOIN energy_production p
                  ON c.time_stamp = p.time_stamp AND c.country_code = p.country_code
                WHERE c.country_code = ANY(:countries)
                  AND c.time_stamp BETWEEN :start AND :end
                GROUP BY day
                ORDER BY day
            """), conn, params=_params(countries, start, end)
        )
    return df

def flow_table(countries: List[str], start: str, end: str) -> pd.DataFrame:
    with _engine().connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT from_country_code, to_country_code, time_stamp, flow_mw
                FROM cross_border_flow
                WHERE from_country_code = ANY(:countries)
                  AND time_stamp BETWEEN :start AND :end
                ORDER BY time_stamp
            """), conn, params=_params(countries, start, end)
        )
    return df
