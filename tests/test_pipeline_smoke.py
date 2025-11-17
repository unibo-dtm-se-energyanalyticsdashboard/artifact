import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# Helper function to create dummy pandas DataFrames for mocking API responses.
def _df(n=3):
    """Creates a simple DataFrame for mock return values."""
    return pd.DataFrame({
        "ts": pd.date_range("2025-01-01", periods=n, freq="h"),
        "value": range(n),
    })


class TestPipelineSmoke(unittest.TestCase):
    """
    A smoke test for the main 'run_pipeline' orchestrator.

    This test isolates the pipeline.py module by mocking (patching) all
    its external dependencies (adapters and repository logic).
    The goal is to test the 'happy path' execution flow, not the
    logic of the dependencies themselves.
    """

    # --- Setup Mocks (Patching) ---
    # Mocks are stacked. The bottom decorator is executed first
    # and passed as the *last* argument to the test method.
    @patch("edas.pipeline.upsert_energy_production")
    @patch("edas.pipeline.upsert_energy_consumption")
    @patch("edas.pipeline.fetch_production")
    @patch("edas.pipeline.fetch_consumption")
    @patch("edas.pipeline._load_countries")
    @patch("edas.pipeline.get_engine") # This is the first mock (executed last)
    def test_run_pipeline_minimal(
        self,
        # Mocks are injected by @patch, in reverse order of the decorators:
        mock_get_engine,        # Mock for the DB connection factory
        mock_load_countries,    # Mock for the metadata loader
        mock_fetch_consumption, # Mock for the ENTSO-E client adapter
        mock_fetch_production,  # Mock for the ENTSO-E client adapter
        mock_upsert_cons,       # Mock for the Repository/Upsert logic
        mock_upsert_prod,       # Mock for the Repository/Upsert logic
    ):
        """
        Tests the 'run_pipeline' function in a minimal configuration
        (FR only, no flows) to ensure all components are called correctly.
        """
        
        # --- Arrange (Define Mock Behavior) ---

        # 1. Create Test Doubles (Fakes) for the SQLAlchemy Engine and Connection
        # This simulates the 'with engine.begin() as sa_conn:' context.
        class _FakeConn:
            """Fake SQLAlchemy Connection class (Test Double)."""
            def __init__(self):
                # Mock the 'driver_connection' (raw psycopg2 connection)
                self.connection = MagicMock()
                self.connection.driver_connection = object()
            def __enter__(self): return self
            def __exit__(self, *args): return False # Simulate successful transaction

        class _FakeEngine:
            """Fake SQLAlchemy Engine class (Test Double)."""
            def begin(self): return _FakeConn()

        # 2. Assign mock return values
        # When get_engine() is called, return our fake engine
        mock_get_engine.return_value = _FakeEngine()
        
        # When _load_countries() is called, return minimal metadata
        mock_load_countries.return_value = {
            "FR": {"name": "France", "zone": "10YFR-RTE------C"},
        }

        # When fetch adapters are called, return dummy DataFrames
        mock_fetch_consumption.return_value = _df(4)
        mock_fetch_production.return_value  = _df(5)
        
        # When upsert functions are called, simulate success by returning row count
        mock_upsert_cons.side_effect = lambda _raw, df: len(df)
        mock_upsert_prod.side_effect = lambda _raw, df: len(df)

        # --- Act ---
        # Import the SUT (System Under Test) *after* mocks are set up
        from edas.pipeline import run_pipeline

        # Run the pipeline with specific test parameters
        run_pipeline(countries=["FR"], include_flows=False, mode="last_10_days")

        # --- Assert ---
        # Verify that the pipeline orchestration logic called all the adapters
        # exactly one time.
        mock_fetch_consumption.assert_called_once()
        mock_fetch_production.assert_called_once()
        mock_upsert_cons.assert_called_once()
        mock_upsert_prod.assert_called_once()