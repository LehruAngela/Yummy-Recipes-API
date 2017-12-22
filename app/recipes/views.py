from . import recipe_api
from flask import Blueprint, make_response, request, jsonify
from app.models.recipe import Recipe
from app.models.recipeAuth import RecipeApp
from functools import wraps


def auth(func):

    @wraps(func)
    def user_login(*args, **kwargs):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = RecipeApp.decode_token(access_token)
            if not isinstance(user_id, str):
                # Handle the request if the user is authenticated"""
                return func(user_id, *args, **kwargs)
            return None
        return None
    return user_login


@recipe_api.route('/categories/<int:category_id>/recipes/', methods=['POST', 'GET'])
@auth
def recipes(user_id, category_id, **kwargs):
    # retrieves/adds recipes from/to the database
    if request.method == "POST":
        recipe_name = str(request.data.get('recipe_name', ''))
        ingredients = str(request.data.get('ingredients', ''))
        directions = str(request.data.get('directions', ''))

        if recipe_name:
            #recipe_name = recipe_name.title()
            recipe = Recipe(recipe_name=recipe_name, user_id=user_id, category_id=category_id)
            recipe.save()
            response = jsonify({
                'recipe_id': recipe.recipe_id,
                'recipe_name': recipe.recipe_name,
                'ingredients': recipe.ingredients,
                'directions': recipe.directions,
                'date_created': recipe.date_created,
                'date_modified': recipe.date_modified,
                'created_by' : user_id,
                'category_id': recipe.category_id,
            })
            return make_response(response), 201

    else:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        q = str(request.args.get('q', '')).title()

        # GET all the recipes under this category
        recipes = Recipe.query.filter(Recipe.user_id==user_id).filter(Recipe.category_id==category_id).filter(Recipe.recipe_name.like('%'+q+'%')).paginate(page, per_page)

        results = []
        if recipes:
            for recipe in recipes.items:
                obj = {
                    'recipe_id': recipe.recipe_id,
                    'recipe_name': recipe.recipe_name,
                    'ingredients': recipe.ingredients,
                    'directions': recipe.directions,
                    'date_created': recipe.date_created,
                    'date_modified': recipe.date_modified,
                    'created_by' : user_id,
                    'category_id': recipe.category_id,
                    }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response
        return {
                "message": "There are no recipes in this category or Category doesn't exist"
                }, 404


@recipe_api.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET', 'PUT', 'DELETE'])
@auth
def recipe_edit_and_delete(user_id, category_id, recipe_id, **kwargs):
    # retrieve a recipe using it's ID
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
            'date_modified': recipe.date_modified,
            'created_by' : user_id,
            'category_id': recipe.category_id,
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
