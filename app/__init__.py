from flask import request, jsonify, abort, url_for
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

"""POSTGRESTEST = {
'user': 'postgres',
'db': 'recipe_db',
'host': 'localhost',
'port': '5432',
}"""
# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    from app.models.category import Category
    from app.models.recipe import Recipe
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config['development']) # app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()


    @app.route('/categories', methods=['POST', 'GET'])
    def categories():
        if request.method == "POST":
            category_name = str(request.data.get('category_name', ''))
            if category_name:
                category = Category(category_name=category_name)
                category.save()
                response = jsonify({
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'date_created': category.date_created,
                    'date_modified': category.date_modified,
                    'recipes': url_for('recipes', category_id=category.category_id, _external=True)
                })
                response.status_code = 201
                return response
        else:
            # GET
            categories = Category.get_all()
            results = []

            for category in categories:
                obj = {
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'date_created': category.date_created,
                    'date_modified': category.date_modified,
                    'recipes': url_for('recipes', category_id=category.category_id, _external=True)
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response


    @app.route('/categories/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
    def category_edit_and_delete(category_id, **kwargs):
     # retrieve a buckelist using it's ID
        category = Category.query.filter_by(category_id=category_id).first()
        if not category:
            # Raise an HTTPException with a 404 not found status code
            return {
            "message": "Url doesn't exist. Please type existing url"
         }, 404

        if request.method == 'DELETE':
            category.delete()
            return {
            "message": "category {} deleted successfully".format(category.category_id)
         }, 200

        elif request.method == 'PUT':
            category_name = str(request.data.get('category_name', ''))
            category.category_name = category_name
            category.save()
            response = jsonify({
                'category_id': category.category_id,
                'category_name': category.category_name,
                'date_created': category.date_created,
                'date_modified': category.date_modified,
                'recipes': url_for('recipes', category_id=category.category_id, _external=True)
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'category_id': category.category_id,
                'category_name': category.category_name,
                'date_created': category.date_created,
                'date_modified': category.date_modified,
                'recipes': url_for('recipes', category_id=category.category_id, _external=True)
            })
            response.status_code = 200
            return response

    @app.route('/categories/<int:category_id>/recipes', methods=['POST', 'GET'])
    def recipes(category_id, **kwargs):
        if request.method == "POST":
            recipe_name = str(request.data.get('recipe_name', ''))
            ingredients = str(request.data.get('ingredients', ''))
            directions = str(request.data.get('directions', ''))

            if recipe_name:
                recipe = Recipe(recipe_name=recipe_name)
                recipe.save()
                response = jsonify({
                    'recipe_id': recipe.recipe_id,
                    'recipe_name': recipe.recipe_name,
                    'ingredients': recipe.ingredients,
                    'directions': recipe.directions,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified
                })
                response.status_code = 201
                return response
        else:
            # GET
            recipes = Recipe.query.filter_by(category_id=category_id).all()
            results = []

            for recipe in recipes:
                obj = {
                    'recipe_id': recipe.recipe_id,
                    'recipe_name': recipe.recipe_name,
                    'ingredients': recipe.ingredients,
                    'directions': recipe.directions,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET', 'PUT', 'DELETE'])
    def recipe_edit_and_delete(category_id, recipe_id, **kwargs):
     # retrieve a buckelist using it's ID
        recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
        if not recipe:
            # Raise an HTTPException with a 404 not found status code
            return {
            "message": "Url doesn't exist. Please type existing url"
         }, 404

        if request.method == 'DELETE':
            recipe.delete()
            return {
            "message": "recipe {} deleted successfully".format(recipe.recipe_id)
         }, 200

        elif request.method == 'PUT':
            recipe_name = str(request.data.get('recipe_name', ''))
            ingredients = str(request.data.get('ingredients', ''))
            directions = str(request.data.get('directions', ''))

            recipe.recipe_name = recipe_name
            recipe.ingredients = ingredients
            recipe.directions = directions

            recipe.save()
            response = jsonify({
                'recipe_id': recipe.recipe_id,
                'recipe_name': recipe.recipe_name,
                'ingredients': recipe.ingredients,
                'directions': recipe.directions,
                'date_created': recipe.date_created,
                'date_modified': recipe.date_modified
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'recipe_id': recipe.recipe_id,
                'recipe_name': recipe.recipe_name,
                'ingredients': recipe.ingredients,
                'directions': recipe.directions,
                'date_created': recipe.date_created,
                'date_modified': recipe.date_modified
            })
            response.status_code = 200
            return response

    return app
