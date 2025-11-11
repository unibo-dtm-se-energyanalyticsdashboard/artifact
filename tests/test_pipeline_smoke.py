import unittest
from unittest.mock import patch, MagicMock
import pandas as pd


def _df(n=3):
    return pd.DataFrame({
        "ts": pd.date_range("2025-01-01", periods=n, freq="h"),
        "value": range(n),
    })


class TestPipelineSmoke(unittest.TestCase):
    @patch("edas.pipeline.upsert_energy_production")
    @patch("edas.pipeline.upsert_energy_consumption")
    @patch("edas.pipeline.fetch_production")
    @patch("edas.pipeline.fetch_consumption")
    @patch("edas.pipeline._load_countries")
    @patch("edas.pipeline.get_engine")
    def test_run_pipeline_minimal(
        self,
        mock_get_engine,
        mock_load_countries,
        mock_fetch_consumption,
        mock_fetch_production,
        mock_upsert_cons,
        mock_upsert_prod,
    ):
   
        class _FakeConn:
            def __init__(self):
                self.connection = MagicMock()
                self.connection.driver_connection = object()
            def __enter__(self): return self
            def __exit__(self, *args): return False

        class _FakeEngine:
            def begin(self): return _FakeConn()

        mock_get_engine.return_value = _FakeEngine()

  
        mock_load_countries.return_value = {
            "FR": {"name": "France", "zone": "10YFR-RTE------C"},
        }

        mock_fetch_consumption.return_value = _df(4)
        mock_fetch_production.return_value  = _df(5)
        mock_upsert_cons.side_effect = lambda _raw, df: len(df)
        mock_upsert_prod.side_effect = lambda _raw, df: len(df)

        from edas.pipeline import run_pipeline

    
        run_pipeline(countries=["FR"], include_flows=False, mode="last_10_days")

        mock_fetch_consumption.assert_called_once()
        mock_fetch_production.assert_called_once()
        mock_upsert_cons.assert_called_once()
        mock_upsert_prod.assert_called_once()
