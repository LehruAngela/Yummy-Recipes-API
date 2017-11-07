import unittest
from app import create_app, db

class TestRecipeApp(unittest.TestCase):
    """class to test valid user registration and login."""
    def setUp(self):
        self.app = create_app(config_name="testing")
