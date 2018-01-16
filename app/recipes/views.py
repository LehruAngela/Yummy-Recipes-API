from flask import Blueprint, make_response, request, jsonify
from functools import wraps

from app.models.recipe import Recipe
from app.models.recipeAuth import RecipeApp
from app.models.category import Category
from app.categories.views import login_required
from . import recipe_api
import validate


@recipe_api.route('/categories/<int:category_id>/recipes/', methods=['POST'])
@login_required
def create_recipes(user_id, category_id):
    """Create recipes in an existing category"""
    category = Category.query.filter(Category.user_id == user_id).filter(
        Category.category_id == category_id).first()
    if not category:
        return make_response(jsonify({'message': 'Category doesnt exist.'})), 404
    recipe = Recipe.query.filter(Recipe.user_id == user_id).filter(Recipe.category_id == category_id).filter_by(recipe_name=request.data['recipe_name']).first()
    if not recipe:
        if request.method == "POST":
            recipe_name = str(request.data.get('recipe_name', ''))
            ingredients = str(request.data.get('ingredients', ''))
            directions = str(request.data.get('directions', ''))
            recipe_name.strip()
            if recipe_name:
                if validate.validate_name(recipe_name) == "True":
                    recipe = Recipe(recipe_name=recipe_name,
                                    user_id=user_id, category_id=category_id)
                    recipe.save()
                    response = jsonify(recipe.recipe_json())
                    return make_response(response), 201
            return make_response(jsonify({'message': 'Recipe name required.'})), 400
    return make_response(jsonify({'message': 'Recipe already exists.'})), 409


@recipe_api.route('/categories/<int:category_id>/recipes/', methods=['GET'])
@login_required
def view_recipes(user_id, category_id):
    """View recipes in an existing category"""
    category = Category.query.filter(Category.user_id == user_id).filter(
        Category.category_id == category_id)
    if not category:
        response = {'message': 'Category name doesnt exist.'}
        return make_response(jsonify(response)), 422
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        q = str(request.args.get('q', '')).title()
        # GET all the recipes under this category
        recipes = Recipe.query.filter(Recipe.user_id == user_id).filter(
            Recipe.category_id == category_id).filter(Recipe.recipe_name.like('%' + q + '%')).paginate(page, per_page)
        results = []
        if recipes:
            for recipe in recipes.items:
                obj = {'Recipes': recipe.recipe_json()}
                results.append(obj)
        if results:
            return make_response(jsonify(results)), 200
        return make_response(jsonify({'message': 'No recipes found'})), 422


@recipe_api.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
@login_required
def view_one_recipe(user_id, category_id, recipe_id):
    """View one recipe in an existing category"""
    category = Category.query.filter(Category.user_id == user_id).filter(
        Category.category_id == category_id)
    if not category:
        response = {'message': 'Category name doesnt exist.'}
        return make_response(jsonify(response)), 422
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        return {"message": "No recipe found"}, 404
    response = jsonify({'Recipe': recipe.recipe_json()})
    response.status_code = 200
    return response


@recipe_api.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['PUT'])
@login_required
def edit_recipe(user_id, category_id, recipe_id):
    """Edit a recipe in an existing category"""
    category = Category.query.filter(Category.user_id == user_id).filter(
        Category.category_id == category_id)
    if not category:
        response = {'message': 'Category name doesnt exist.'}
        return make_response(jsonify(response)), 422
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        return {"message": "No recipe found to edit"}, 404
    if request.method == 'PUT':
        recipe_name = str(request.data.get('recipe_name', ''))
        ingredients = str(request.data.get('ingredients', ''))
        directions = str(request.data.get('directions', ''))
        # checks if recipe exists
        recipe.recipe_name = recipe_name
        recipe.ingredients = ingredients
        recipe.directions = directions
        recipe.save()
        response = jsonify({'Edited recipe': recipe.recipe_json()})
        response.status_code = 200
        return response


@recipe_api.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['DELETE'])
@login_required
def delete_recipe(user_id, category_id, recipe_id):
    """Delete a recipe in an existing category"""
    category = Category.query.filter(Category.user_id == user_id).filter(
        Category.category_id == category_id)
    if not category:
        response = {'message': 'Category name doesnt exist.'}
        return make_response(jsonify(response)), 422
    # delete a recipe
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        # Raise an HTTPException with a 404 not found status code
        return {"message": "No recipe found to delete"}, 404
    if request.method == 'DELETE':
        recipe.delete()
        return {"message": "recipe {} deleted successfully".format(recipe.recipe_id)}, 200
