import logging
from typing import List
import pandas as pd
from entsoe import EntsoePandasClient

from edas.config import ENTSOE_API_KEY, TZ_EUROPE

log = logging.getLogger(__name__)
client = EntsoePandasClient(api_key=ENTSOE_API_KEY)

def to_utc_naive(series: pd.Series, tz: str = TZ_EUROPE) -> pd.Series:
    s = pd.to_datetime(series, errors="coerce")
    # اگر tz-aware بود → مستقیم به UTC و سپس naive
    if getattr(s.dtype, "tz", None) is not None:
        return s.dt.tz_convert("UTC").dt.tz_localize(None)
    # اگر naive بود → اول Europe/Brussels، بعد UTC و naive
    return s.dt.tz_localize(tz).dt.tz_convert("UTC").dt.tz_localize(None)

def _flatten_columns(cols) -> List[str]:
    if isinstance(cols, pd.MultiIndex):
        out = []
        for tup in cols.tolist():
            parts = [str(x) for x in tup if (x is not None and str(x) != "")]
            out.append(" | ".join(parts) if parts else "UNKNOWN")
        return out
    return [str(c) for c in cols]

def fetch_consumption(country_code: str, zone_key: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    log.info("Load consumption %s (%s) %s → %s", country_code, zone_key, start, end)
    s = client.query_load(zone_key, start=start, end=end)
    if s is None or s.empty:
        return pd.DataFrame(columns=["country_code","time_stamp","consumption_mw"])
    df = s.reset_index()
    df.columns = ["time_stamp", "consumption_mw"]
    df["time_stamp"] = to_utc_naive(df["time_stamp"])
    df["country_code"] = country_code
    return df[["country_code","time_stamp","consumption_mw"]]

def fetch_production(country_code: str, zone_key: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    log.info("Load generation %s (%s) %s → %s", country_code, zone_key, start, end)
    df = client.query_generation(zone_key, start=start, end=end, psr_type=None)
    if df is None or len(df) == 0:
        return pd.DataFrame(columns=["country_code","time_stamp","source_type","production_mw"])

    # اگر فقط یک سری باشه
    if isinstance(df, pd.Series):
        out = pd.DataFrame({
            "country_code": country_code,
            "time_stamp": to_utc_naive(df.index),
            "source_type": "TOTAL",
            "production_mw": df.values,
        })
        return out

    # اگر DataFrame با چند ستون (منابع مختلف)
    df = df.copy()
    df.index = pd.to_datetime(df.index, errors="coerce")
    df.index.name = "time_stamp"
    df.columns = _flatten_columns(df.columns)
    df = df.reset_index()

    value_cols = [c for c in df.columns if c != "time_stamp"]
    df_long = pd.melt(df, id_vars=["time_stamp"], value_vars=value_cols,
                      var_name="source_type", value_name="production_mw")
    df_long["time_stamp"] = to_utc_naive(df_long["time_stamp"])
    df_long["country_code"] = country_code
    df_long = df_long.dropna(subset=["production_mw"])
    return df_long[["country_code","time_stamp","source_type","production_mw"]]

def fetch_flow(from_cc: str, to_cc: str, from_zone: str, to_zone: str,
               start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    log.info("Load flow %s(%s) -> %s(%s) %s → %s", from_cc, from_zone, to_cc, to_zone, start, end)
    try:
        s = client.query_crossborder_flows(from_zone, to_zone, start=start, end=end)
    except Exception as e:
        log.warning("Flow API error %s->%s: %s", from_cc, to_cc, str(e))
        return pd.DataFrame(columns=["from_country_code","to_country_code","time_stamp","flow_mw"])
    if s is None or s.empty:
        return pd.DataFrame(columns=["from_country_code","to_country_code","time_stamp","flow_mw"])
    df = s.reset_index()
    df.columns = ["time_stamp", "flow_mw"]
    df["time_stamp"] = to_utc_naive(df["time_stamp"])
    df["from_country_code"] = from_cc
    df["to_country_code"] = to_cc
    return df.dropna(subset=["flow_mw"])[["from_country_code","to_country_code","time_stamp","flow_mw"]]
