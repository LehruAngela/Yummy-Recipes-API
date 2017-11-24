import unittest
import os
import json
from app import create_app, db

class TestCategory(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'name': 'Stews'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_create_category(self):
        """Test API can create a category (POST request)"""
        res = self.client().post('/categories/', data=self.category)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Stews', str(res.data))

    def test_view_categories(self):
        """Test API can get all categories(GET request)."""
        res = self.client().post('/categories/', data=self.category)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/categories/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Stews', str(res.data))

    def test_view_category_by_id(self):
        """Test API can get a category by using its id(GET request)."""
        rv = self.client().post('/categories/', data=self.bucketlist)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/categories/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Stews', str(result.data))

    def test_edit_category(self):
        """Test API can edit an existing category(PUT request). """
        rv = self.client().post(
            '/categories/',
            data={'name': 'Sauces'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/categories/1',
            data={
                "name": "Soups and Sauces"
            })
        self.assertEqual(rv.status_code, 200)
        results = self.client().get('/categories/1')
        self.assertIn('Soups and', str(results.data))

    def test_delete_category(self):
        """Test API can delete a category(DELETE request)."""
        rv = self.client().post(
            '/categories/',
            data={'name': 'Sauces'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/categories/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/categories/1')
        self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
