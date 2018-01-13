from . import recipe_api
from flask import Blueprint, make_response, request, jsonify
from app.models.recipe import Recipe
from app.models.recipeAuth import RecipeApp
from app.models.category import Category
from functools import wraps
import validate


def auth(func):

    @wraps(func)
    def user_login(*args, **kwargs):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            response = {'message': 'No token provided. Please provide a valid token.'}
            return make_response(jsonify(response)), 401
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


@recipe_api.route('/categories/<int:category_id>/recipes/', methods=['POST'])
@auth
def create_recipes(user_id, category_id, **kwargs):
    """
        Creates a new recipe
        ---
        tags:
          - Recipes
        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
            description: Specify the category id
          - in: body
            name: body
            required: true
            type: string
            description: This route creates a recipe
        security:
          - TokenHeader: []
        responses:
          200:
            description: You successfully created a recipe
          201:
            description: Recipe successfully created
            schema:
              id: Create recipe
              properties:
                recipe_name:
                  type: string
                  default: Chicken
                response:
                  type: string
                  default: {'category_id': 1, 'recipe_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          409:
            description: Recipe name already exists
            schema:
              id: Already existing recipe name being added
              properties:
                recipe_name:
                  type: string
                  default: {'category_id': 1, 'recipe_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
                response:
                  type: string
                  default: Recipe name already exists.
        """
    #checks if category exists
    category = Category.query.filter(Category.user_id==user_id).filter(Category.category_id==category_id).first()
    if not category:
        response = {'message': 'Category doesnt exist.'}
        return make_response(jsonify(response)), 404
    # adds recipes to the database
    recipe = Recipe.query.filter(Recipe.user_id==user_id).filter(Recipe.category_id==category_id).filter_by(recipe_name=request.data['recipe_name']).first()

    if not recipe:
        if request.method == "POST":
            recipe_name = str(request.data.get('recipe_name', ''))
            ingredients = str(request.data.get('ingredients', ''))
            directions = str(request.data.get('directions', ''))

            recipe_name.strip()

            if recipe_name:
                if validate.validate_name(recipe_name) == "True":
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
            response = {'message': 'Recipe name required.'}
            return make_response(jsonify(response)), 400
    # There is an existing recipe.
    response = {'message': 'Recipe already exists.'}
    return make_response(jsonify(response)), 409


@recipe_api.route('/categories/<int:category_id>/recipes/', methods=['GET'])
@auth
def view_recipes(user_id, category_id, **kwargs):
    """
        Retrieves all created recipes by that user
        ---
        tags:
          - Recipes
        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
            description: Specify the category id
          - in: query
            name: q
            required: false
            type: string
            description: This route retrieves all recipes of that name
          - in: query
            name: page
            required: false
            type: integer
            description: This route retrieves all recipes of that page number
          - in: query
            name: per_page
            required: false
            type: integer
            description: This route retrieves the specified number of recipes on a page
        security:
          - TokenHeader: []
        responses:
          200:
            description: You successfully retrieved all recipes
          201:
            description: Recipes retrieved successfully
            schema:
              id: View recipes
              properties:
                recipe_name by q:
                  type: string
                  default: ?q=Chick
                pagination:
                  type: string
                  default: ?page=1&per_page=1
                response:
                  type: string
                  default: {'category_id': 1, 'recipe_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          404:
            description: Searching for a title that is not there or invalid
            schema:
              id: Invalid
              properties:
                recipe_name:
                  type: string
                  default: '6oo06'
                response:
                  type: string
                  default: Recipe not found
        """
    # checks if category exists
    category = Category.query.filter(Category.user_id==user_id).filter(Category.category_id==category_id)
    if not category:
        response = {'message': 'Category name doesnt exist.'}
        return make_response(jsonify(response)), 422
    # retrieves recipes from the database
    if request.method == "GET":
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
        if results:
            return make_response(jsonify(results)), 200
        response = {'message': 'No recipes found'}
        return make_response(jsonify(response)), 422


@recipe_api.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['GET'])
@auth
def view_one_recipe(user_id, category_id, recipe_id, **kwargs):
    """
        Retrieves a single recipe using it's ID
        ---
        tags:
          - Recipes
        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
            description: Specify the category ID
          - in: path
            name: recipe_id
            required: true
            type: integer
            description: Specify the recipe ID
        security:
          - TokenHeader: []
        responses:
          200:
            description: You successfully retrieved a recipe using its ID
          201:
            description: Recipe retrieved successfully
            schema:
              id: View one recipe
              properties:
                category_id:
                  type: integer
                  default: 1
                response:
                  type: string
                  default: {'category_id': 1, 'recipe_id': 1, 'recipe_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          404:
            description: Url doesn't exist. Please type existing url
            schema:
              id: Invalid ID
              properties:
                category_id:
                  type: integer
                  default: 2
                recipe_id:
                  type: integer
                  default: 2
                response:
                  type: string
                  default: Recipe not found
        """
    #checks if category exists
    category = Category.query.filter(Category.user_id==user_id).filter(Category.category_id==category_id)
    if not category:
        response = {'message': 'Category name doesnt exist.'}
        return make_response(jsonify(response)), 422
    # retrieve a recipe using it's ID
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        # Raise an HTTPException with a 404 not found status code
        return {"message": "No recipe found"}, 404
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


@recipe_api.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['PUT'])
@auth
def edit_recipe(user_id, category_id, recipe_id, **kwargs):
    """
        Updates a recipe of a specified ID
        ---
        tags:
          - Recipes
        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
            description: Specify the category id
          - in: path
            name: recipe_id
            required: true
            type: string
            description: Specify the recipe id
          - in: body
            name: body
            required: true
            type: string
            description: This routes edits a category
        security:
          - TokenHeader: []
        responses:
          200:
            description: You successfully retrieved a recipe using its ID
          201:
            description: Recipe edited successfully
            schema:
              id: Edit recipe
              properties:
                category_id:
                  type: integer
                  default: 1
                recipe_id:
                  type: integer
                  default: 1
                recipe_name:
                  type: string
                  default: Chicken
                response:
                  type: string
                  default: {'category_id': 1, 'recipe_id': 1, 'recipe_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          404:
            description: Url doesn't exist. Please type existing url
            schema:
              id: Invalid ID
              properties:
                category_id:
                  type: integer
                  default: 2
                recipe_id:
                  type: integer
                  default: 2
                response:
                  type: string
                  default: No recipe found
        """
    #checks if category exists
    category = Category.query.filter(Category.user_id==user_id).filter(Category.category_id==category_id)
    if not category:
        response = {'message': 'Category name doesnt exist.'}
        return make_response(jsonify(response)), 422
    # edit a recipe
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        # Raise an HTTPException with a 404 not found status code
        return {"message": "Url doesn't exist. Please type existing url"}, 404
    if request.method == 'PUT':
        recipe_name = str(request.data.get('recipe_name', ''))
        ingredients = str(request.data.get('ingredients', ''))
        directions = str(request.data.get('directions', ''))
    #
    # recipe = Recipe.query.filter_by(recipe_name=request.data['recipe_name']).first()
    # #checks if recipe exists
    # if recipe != recipe_name:
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


@recipe_api.route('/categories/<int:category_id>/recipes/<int:recipe_id>', methods=['DELETE'])
@auth
def delete_recipe(user_id, category_id, recipe_id, **kwargs):
    """
        Deletes a recipe of a specified ID
        ---
        tags:
          - Recipes
        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
            description: Specify the category id
          - in: path
            name: recipe_id
            required: true
            type: string
            description: Specify the recipe id
        security:
          - TokenHeader: []
        responses:
          200:
            description: You successfully retrieved a recipe using its ID
          201:
            description: Recipe created successfully
            schema:
              id: Delete recipe
              properties:
                category_id:
                  type: integer
                  default: 1
                recipe_id:
                  type: integer
                  default: 1
                response:
                  type: string
                  default: Recipe 1 deleted
          404:
            description: Url doesn't exist. Please type existing url
            schema:
               id: Invalid delete
               properties:
                 category_id:
                   type: integer
                   default: 2
                 recipe_id:
                   type: integer
                   default: 2
                 response:
                   type: string
                   default: Recipe not found
        """
    #checks if category exists
    category = Category.query.filter(Category.user_id==user_id).filter(Category.category_id==category_id)
    if not category:
        response = {'message': 'Category name doesnt exist.'}
        return make_response(jsonify(response)), 422
    # delete a recipe
    recipe = Recipe.query.filter_by(recipe_id=recipe_id).first()
    if not recipe:
        # Raise an HTTPException with a 404 not found status code
        return {"message": "Url doesn't exist. Please type existing url"}, 404
    if request.method == 'DELETE':
        recipe.delete()
        return {"message": "recipe {} deleted successfully".format(recipe.recipe_id)
            }, 200
