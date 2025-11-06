# src/edas/dashboard/queries.py

import pandas as pd
from typing import Iterable, Tuple, Callable
from sqlalchemy.engine import Engine


EngineFactory = Callable[[], Engine]


def _as_tuple(countries: Iterable[str]) -> Tuple[str, ...]:
    return tuple(countries) if not isinstance(countries, tuple) else countries


def consumption_vs_production(
    engine_factory: EngineFactory,
    countries: Iterable[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    countries_t = _as_tuple(countries)
    with engine_factory().connect() as conn:
        cons = pd.read_sql(
            """
            SELECT time_stamp, SUM(consumption_mw) AS consumption_mw
            FROM energy_consumption
            WHERE country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY time_stamp
            ORDER BY time_stamp
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
        prod = pd.read_sql(
            """
            SELECT time_stamp, SUM(production_mw) AS production_mw
            FROM energy_production
            WHERE country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY time_stamp
            ORDER BY time_stamp
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
    df = pd.merge(cons, prod, on="time_stamp", how="outer").sort_values("time_stamp")
    return df


def kpis(
    engine_factory: EngineFactory,
    countries: Iterable[str],
    start: str,
    end: str,
) -> dict:
    countries_t = _as_tuple(countries)
    with engine_factory().connect() as conn:
        cons = pd.read_sql(
            """
            SELECT time_stamp, SUM(consumption_mw) AS consumption_mw
            FROM energy_consumption
            WHERE country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY time_stamp
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
        prod = pd.read_sql(
            """
            SELECT time_stamp, SUM(production_mw) AS production_mw
            FROM energy_production
            WHERE country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY time_stamp
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
        mix = pd.read_sql(
            """
            SELECT source_type, SUM(production_mw) AS production_mw
            FROM energy_production
            WHERE country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY source_type
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
        flows = pd.read_sql(
            """
            SELECT SUM(flow_mw) AS flow_mw
            FROM cross_border_flow
            WHERE from_country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )

    total_cons = cons["consumption_mw"].sum() if not cons.empty else 0.0
    total_prod = prod["production_mw"].sum() if not prod.empty else 0.0

    if not cons.empty:
        cons["day"] = pd.to_datetime(cons["time_stamp"]).dt.to_period("D")
        cons["week"] = pd.to_datetime(cons["time_stamp"]).dt.to_period("W")
        cons["month"] = pd.to_datetime(cons["time_stamp"]).dt.to_period("M")
        avg_daily = cons.groupby("day")["consumption_mw"].sum().mean()
        avg_weekly = cons.groupby("week")["consumption_mw"].sum().mean()
        avg_monthly = cons.groupby("month")["consumption_mw"].sum().mean()
    else:
        avg_daily = avg_weekly = avg_monthly = 0.0

    if not mix.empty and mix["production_mw"].sum() > 0:
        mix["percent"] = mix["production_mw"] / mix["production_mw"].sum() * 100.0
    else:
        mix["percent"] = 0.0

    net_balance = float(flows.iloc[0, 0]) if not flows.empty else 0.0

    return {
        "total_consumption": float(total_cons),
        "avg_daily_consumption": float(avg_daily),
        "avg_weekly_consumption": float(avg_weekly),
        "avg_monthly_consumption": float(avg_monthly),
        "total_production": float(total_prod),
        "energy_mix": mix,
        "net_balance": float(net_balance),
    }


def production_mix(
    engine_factory: EngineFactory,
    countries: Iterable[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    countries_t = _as_tuple(countries)
    with engine_factory().connect() as conn:
        df = pd.read_sql(
            """
            SELECT time_stamp, source_type, SUM(production_mw) AS production_mw
            FROM energy_production
            WHERE country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY time_stamp, source_type
            ORDER BY time_stamp
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
    return df


def crossborder_flows(
    engine_factory: EngineFactory,
    countries: Iterable[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    countries_t = _as_tuple(countries)
    with engine_factory().connect() as conn:
        df = pd.read_sql(
            """
            SELECT from_country_code, to_country_code, time_stamp, SUM(flow_mw) AS flow_mw
            FROM cross_border_flow
            WHERE from_country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY from_country_code, to_country_code, time_stamp
            ORDER BY time_stamp
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
    return df


def hourly_consumption(
    engine_factory: EngineFactory,
    countries: Iterable[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    countries_t = _as_tuple(countries)
    with engine_factory().connect() as conn:
        df = pd.read_sql(
            """
            SELECT time_stamp, SUM(consumption_mw) AS consumption_mw
            FROM energy_consumption
            WHERE country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY time_stamp
            ORDER BY time_stamp
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
    df["hour"] = pd.to_datetime(df["time_stamp"]).dt.hour
    df["day"] = pd.to_datetime(df["time_stamp"]).dt.day_name()
    return df


def daily_summary(
    engine_factory: EngineFactory,
    countries: Iterable[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    countries_t = _as_tuple(countries)
    with engine_factory().connect() as conn:
        df = pd.read_sql(
            """
            SELECT date_trunc('day', c.time_stamp) AS day,
                   SUM(c.consumption_mw) AS total_consumption,
                   SUM(p.production_mw) AS total_production,
                   SUM(p.production_mw) - SUM(c.consumption_mw) AS net_balance
            FROM energy_consumption c
            JOIN energy_production p
              ON c.time_stamp = p.time_stamp AND c.country_code = p.country_code
            WHERE c.country_code = ANY(%(countries)s)
              AND c.time_stamp BETWEEN %(start)s AND %(end)s
            GROUP BY day
            ORDER BY day
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
    return df


def flow_table(
    engine_factory: EngineFactory,
    countries: Iterable[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    countries_t = _as_tuple(countries)
    with engine_factory().connect() as conn:
        df = pd.read_sql(
            """
            SELECT from_country_code, to_country_code, time_stamp, flow_mw
            FROM cross_border_flow
            WHERE from_country_code = ANY(%(countries)s)
              AND time_stamp BETWEEN %(start)s AND %(end)s
            ORDER BY time_stamp
            """,
            conn,
            params={"countries": list(countries_t), "start": start, "end": end},
        )
    return df
