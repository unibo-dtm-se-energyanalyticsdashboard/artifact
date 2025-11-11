import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import unittest
import pandas as pd

from edas.pipeline import _compute_range  
class TestComputeRange(unittest.TestCase):

    def test_last_10_days_dynamic_now(self):
        now_bxl = pd.Timestamp.utcnow().tz_convert("Europe/Brussels")
        expected_end = now_bxl.floor("h") - pd.Timedelta(hours=1)
        expected_start = expected_end - pd.Timedelta(days=10)

        start, end = _compute_range("last_10_days")

        self.assertEqual(start, expected_start)
        self.assertEqual(end, expected_end)

    def test_full_2025_range(self):
        start, end = _compute_range("full_2025")
        self.assertEqual(str(start), "2025-01-01 00:00:00+01:00")
        self.assertEqual(str(end),   "2025-12-31 23:00:00+01:00")

    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            _compute_range("unsupported_mode")


if __name__ == "__main__":
    unittest.main()
