import unittest
from app import create_app, db


class TestRecipeApp(unittest.TestCase):
    """class to test valid user registration and login."""
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.user = {'email': 'Gela1@gela.com',
                     'password': '123'}

        with self.app.app_context():
            db.create_all()

    def test_register(self):
        """Test API can register users (POST request)"""
        res = self.client().post('/api-v1/auth/register', data=self.user)
        self.assertEqual(res.status_code, 201)

    def test_login(self):
        """Test API can login users (POST request)"""
        self.test_register()
        res = self.client().post('/api-v1/auth/login', data=self.user)
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
