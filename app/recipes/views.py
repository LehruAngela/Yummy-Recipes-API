from . import recipe_api
from flask import Blueprint, make_response, request, jsonify
from app.models.recipe import Recipe
from app.models.recipeAuth import RecipeApp


@recipe_api.route('/categories/<int:category_id>/recipes/', methods=['POST', 'GET'])
def recipes(category_id, **kwargs):
    # retrieves/adds recipes from/to the database
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = RecipeApp.decode_token(access_token)
        if not isinstance(user_id, str):
            # Handle the request if the user is authenticated
            category_id = Category.decode_token(access_token)
            if request.method == "POST":
                recipe_name = str(request.data.get('recipe_name', ''))
                ingredients = str(request.data.get('ingredients', ''))
                directions = str(request.data.get('directions', ''))

                if recipe_name:
                    recipe = Recipe(recipe_name=recipe_name)
                    recipe.save()
                    response = jsonify({
                        'category_id': recipe.recipe_id,
                        'recipe_id': recipe.recipe_id,
                        'recipe_name': recipe.recipe_name,
                        'ingredients': recipe.ingredients,
                        'directions': recipe.directions,
                        'date_created': recipe.date_created,
                        'date_modified': recipe.date_modified
                        'created_by' : user_id
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

@recipe_api.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET', 'PUT', 'DELETE'])
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
