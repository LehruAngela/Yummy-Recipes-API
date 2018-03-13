import unittest
import os
import json
from app import create_app, db
from app.models.category import Category
from app.models.recipeAuth import RecipeApp

class TestCategory(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app"""
        self.app = create_app(config_name='testing')
        self.client = self.app.test_client
        self.category = {'category_name': 'Stews'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self):
        """Helper method to register a test user"""
        user = {'email': 'Gela@gela.com',
                'password': '1234567',
                'confirm_password': '1234567'}
        return self.client().post('/api-v1/auth/register', data=user)

    def login_user(self):
        """Helper method to login a test user"""
        user = {'email': 'Gela@gela.com',
                'password': '1234567'}
        return self.client().post('/api-v1/auth/login', data=user)

    def test_create_category(self):
        """Test API can create a category (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result=self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Stews', str(res.data))

    def test_view_categories(self):
        """Test API can get all categories(GET request)."""
        self.register_user()
        result=self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a category by making a POST request
        res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)

        # get all the categories that belong to the test user by making a GET request
        res = self.client().get(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        self.assertIn('Stews', str(res.data))

    def test_view_category_by_id(self):
        """Test API can get a category by using its id(GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)

        # assert that the category is created
        self.assertEqual(rv.status_code, 201)
        # get the response data in json format
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api-v1/categories/{}'.format(result_in_json['category_id']),
            headers=dict(Authorization="Bearer " + access_token),)
        # assert that the category is actually returned given its ID
        self.assertEqual(result.status_code, 201)
        self.assertIn('Stews', str(result.data))

    def test_edit_category(self):
        """Test API can edit an existing category(PUT request). """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # we create a category by making a POST request
        rv = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'category_name': 'Sauces'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the category
        results = json.loads(rv.data.decode())

        # then, we edit the created category by making a PUT request
        rv = self.client().put(
            '/api-v1/categories/{}'.format(results['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                'category_name': 'Soups and Sauces'
            })
        self.assertEqual(rv.status_code, 201)

        #  we get the edited category to see if it is actually edited.
        results = self.client().get(
            '/api-v1/categories/{}'.format(results['category_id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Soups and', str(results.data))

    def test_delete_category(self):
        """Test API can delete a category(DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'category_name': 'Sauces'})
        self.assertEqual(rv.status_code, 201)
        # get the category in json
        results = json.loads(rv.data.decode())

        # delete the category we just created
        res = self.client().delete(
                '/api-v1/categories/{}'.format(results['category_id']),
                headers=dict(Authorization="Bearer " + access_token)
            )
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/api-v1/categories/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_view_by_q(self):
        """Test API can retrieve categories using q"""
        self.register_user()
        result=self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a category by making a POST request
        res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)

        # get all the categories that belong to the q
        res = self.client().get(
            '/api-v1/categories/?q=Stews',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
        self.assertIn('Stews', str(res.data))

    def test_pagination(self):
        """Test API can retrieve categories using q"""
        self.register_user()
        result=self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a category by making a POST request
        res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 201)

        # get all the categories that belong to the q
        res = self.client().get(
            '/api-v1/categories/?page=1&per_page=5',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)
