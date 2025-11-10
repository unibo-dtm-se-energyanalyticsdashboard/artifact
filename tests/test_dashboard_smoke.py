import unittest

class TestDashboardSmoke(unittest.TestCase):
    def test_layout_builds(self):
        from edas.dashboard.app import app
        self.assertIsNotNone(app.layout)
