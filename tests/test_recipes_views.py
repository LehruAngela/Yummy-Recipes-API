import unittest
import os
import json
from app import create_app, db
from app.models.category import Category
from app.models.recipeAuth import RecipeApp

class TestRecipe(unittest.TestCase):
    def setUp(self):
        """Define test variables and initialize app"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.recipe = {'recipe_name': 'Chicken Stew'}
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
                'username': 'Gela',
                'password': '1234567',
                'confirm_password': '1234567'}
        return self.client().post('/api-v1/auth/register', data=user)

    def login_user(self):
        """Helper method to login a test user"""
        user = {'email': 'Gela@gela.com',
                'password': '1234567'}
        return self.client().post('/api-v1/auth/login', data=user)

    def test_create_recipe(self):
        """Test API can create a recipe (POST request)"""
        self.register_user()
        result=self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']
        category_res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        print('created category', category_res)
        category_id = json.loads(category_res.data.decode('utf-8').replace("'", "\""))
        print ('fff', category_id)
        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api-v1/categories/{}/recipes/'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=self.recipe)
        print('created categoryyyyyy', res)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Chicken Stew'.title(), str(res.data))


    def test_view_recipes(self):
        """Test API can get all recipes(GET request)."""
        self.register_user()
        result=self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        category_res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        category_id = json.loads(category_res.data.decode('utf-8').replace("'", "\""))

        # create a recipe by making a POST request
        res = self.client().post(
            '/api-v1/categories/{}/recipes/'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=self.recipe)
        self.assertEqual(res.status_code, 201)

        # get all the recipes that belong to the test user by making a GET request
        res = self.client().get(
            '/api-v1/categories/{}/recipes/'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Chicken stew'.title(), str(res.data))

    def test_view_recipe_by_id(self):
        """Test API can get a recipe by using its id(GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        category_res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        category_id = json.loads(category_res.data.decode('utf-8').replace("'", "\""))

        rv = self.client().post(
            '/api-v1/categories/{}/recipes/'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=self.recipe)

        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api-v1/categories/{}/recipes/{}'.format(category_id['category_id'], (result_in_json['recipe_id'])),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Chicken Stew'.title(), str(result.data))


    def test_edit_recipe(self):
        """Test API can edit an existing recipe(PUT request). """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        category_res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        category_id = json.loads(category_res.data.decode('utf-8').replace("'", "\""))

        # we create a recipe by making a POST request
        rv = self.client().post(
            '/api-v1/categories/{}/recipes/'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={'recipe_name': 'Sauces'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the recipe
        results = json.loads(rv.data.decode())

        # then, we edit the created recipe by making a PUT request
        rv = self.client().put(
            '/api-v1/categories/{}/recipes/{}'.format(category_id['category_id'], (results['recipe_id'])),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "recipe_name": "Soups and Sauces"
            })
        self.assertEqual(rv.status_code, 200)

        #  we get the edited recipe to see if it is actually edited.
        results = self.client().get(
            '/api-v1/categories/{}/recipes/{}'.format(category_id['category_id'], (results['recipe_id'])),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Soups and', str(results.data))


    def test_delete_recipe(self):
        """Test API can delete a recipe(DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        category_res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        category_id = json.loads(category_res.data.decode('utf-8').replace("'", "\""))

        rv = self.client().post(
            '/api-v1/categories/{}/recipes/'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={'recipe_name': 'Sauces'})
        self.assertEqual(rv.status_code, 201)
        # get the recipe in json
        results = json.loads(rv.data.decode())

        # delete the recipe we just created
        res = self.client().delete(
            '/api-v1/categories/{}/recipes/{}'.format(category_id['category_id'], (results['recipe_id'])),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/api-v1/categories/{}/recipes/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 404)

    def test_view_by_q(self):
        """Test API can get all recipes(GET request)."""
        self.register_user()
        result=self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        category_res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        category_id = json.loads(category_res.data.decode('utf-8').replace("'", "\""))

        # create a recipe by making a POST request
        res = self.client().post(
            '/api-v1/categories/{}/recipes/'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=self.recipe)
        self.assertEqual(res.status_code, 201)

        # get all the recipes that belong to the test user by making a GET request
        res = self.client().get(
            '/api-v1/categories/{}/recipes/?q=Chicken stew'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Chicken stew'.title(), str(res.data))

    def test_pagination(self):
        """Test API can get all recipes(GET request)."""
        self.register_user()
        result=self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        category_res = self.client().post(
            '/api-v1/categories/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        category_id = json.loads(category_res.data.decode('utf-8').replace("'", "\""))

        # create a recipe by making a POST request
        res = self.client().post(
            '/api-v1/categories/{}/recipes/'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=self.recipe)
        self.assertEqual(res.status_code, 201)

        # get all the recipes that belong to the test user by making a GET request
        res = self.client().get(
            '/api-v1/categories/{}/recipes/?page=1&per_page=5'.format(category_id['category_id']),
            headers=dict(Authorization="Bearer " + access_token),
            data=self.category)
        self.assertEqual(res.status_code, 200)
