import pandas as pd
import psycopg2.extras as pg_extras


BATCH_SIZE = 5000

def upsert_energy_consumption(raw_conn, df: pd.DataFrame) -> int:
    if df.empty: 
        return 0
    records = list(df.itertuples(index=False, name=None))
    sql = """
        INSERT INTO energy_consumption (country_code, time_stamp, consumption_mw)
        VALUES %s
        ON CONFLICT (country_code, time_stamp) DO UPDATE
        SET consumption_mw = EXCLUDED.consumption_mw;
    """
    with raw_conn.cursor() as cur:
        pg_extras.execute_values(cur, sql, records, page_size=BATCH_SIZE)
    return len(records)

def upsert_energy_production(raw_conn, df: pd.DataFrame) -> int:
    if df.empty: 
        return 0
    records = list(df.itertuples(index=False, name=None))
    sql = """
        INSERT INTO energy_production (country_code, time_stamp, source_type, production_mw)
        VALUES %s
        ON CONFLICT (country_code, time_stamp, source_type) DO UPDATE
        SET production_mw = EXCLUDED.production_mw;
    """
    with raw_conn.cursor() as cur:
        pg_extras.execute_values(cur, sql, records, page_size=BATCH_SIZE)
    return len(records)

def upsert_cross_border_flow(raw_conn, df: pd.DataFrame) -> int:
    if df.empty: 
        return 0
    records = list(df.itertuples(index=False, name=None))
    sql = """
        INSERT INTO cross_border_flow (from_country_code, to_country_code, time_stamp, flow_mw)
        VALUES %s
        ON CONFLICT (from_country_code, to_country_code, time_stamp) DO UPDATE
        SET flow_mw = EXCLUDED.flow_mw;
    """
    with raw_conn.cursor() as cur:
        pg_extras.execute_values(cur, sql, records, page_size=BATCH_SIZE)
    return len(records)
