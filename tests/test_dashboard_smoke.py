import unittest

class TestDashboardSmoke(unittest.TestCase):
    """
    A simple smoke test for the Dash dashboard (Client/UI).
    
    This test verifies that the dashboard application can be imported
    and that its layout is constructed without raising any errors.
    """
    
    def test_layout_builds(self):
        """
        Tests if the Dash app's layout is successfully built.
        """
        # --- Arrange & Act ---
        # We import *inside* the test method. This ensures that the 'app'
        # object is initialized only when this test is run.
        from edas.dashboard.app import app
        
        # --- Assert ---
        # The test passes if 'app.layout' is not None, meaning the 
        # Dash application layout was defined correctly.
        self.assertIsNotNone(app.layout)