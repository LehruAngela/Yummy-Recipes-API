import unittest
import os
import json
from app import create_app, db

class TestRecipe(unittest.TestCase):

    def setUp(self):
        """Define test variables and initialize app"""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.category = {'recipe_name': 'Chicken stew'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def test_create_recipe(self):
        """Test API can create a recipe (POST request)"""
        res = self.client().post('/recipes/', data=self.recipe)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Stews', str(res.data))

    def test_view_recipes(self):
        """Test API can get all recipes(GET request)."""
        res = self.client().post('/recipes/', data=self.recipe)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/recipes/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Chicken stew', str(res.data))

    def test_view_recipe_by_id(self):
        """Test API can get a recipe by using its id(GET request)."""
        rv = self.client().post('/recipes/', data=self.recipe)
        self.assertEqual(rv.status_code, 201)
        result_in_json = json.loads(rv.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/recipes/{}'.format(result_in_json['recipe_name']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Chicken stew', str(result.data))

    def test_edit_recipe(self):
        """Test API can edit an existing recipe(PUT request). """
        rv = self.client().post(
            '/recipes/',
            data={'recipe_name': 'Sauces'})
        self.assertEqual(rv.status_code, 201)
        rv = self.client().put(
            '/recipes/1',
            data={
                "name": "Soups and Sauces"
            })
        #self.assertEqual(rv.status_code, 200)
        results = self.client().get('/recipes/1')
        #self.assertIn('Soups and', str(results.data))

    def test_delete_recipe(self):
        """Test API can delete a recipe(DELETE request)."""
        rv = self.client().post(
            '/recipes/',
            data={'recipe_name': 'Sauces'})
        self.assertEqual(rv.status_code, 201)
        res = self.client().delete('/recipes/1')
        #self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/recipes/1')
        #self.assertEqual(result.status_code, 404)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
