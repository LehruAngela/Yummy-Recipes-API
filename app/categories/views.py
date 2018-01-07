from . import category_api
from functools import wraps
from flask import Blueprint, make_response, request, jsonify, url_for
from app.models.category import Category
from app.models.recipe import Recipe
from app.models.recipeAuth import RecipeApp

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


@category_api.route('/categories/', methods=['POST'])
@auth
def create_categories(user_id):
    """
        Creates a new category
        ---
        tags:
          - Categories

        parameters:
          - in: body
            name: body
            required: true
            type: string
            description: This route creates a category

        security:
          - TokenHeader: []

        responses:
          200:
            description: You successfully created a category
          201:
            description: Category successfully created
            schema:
              id: Create category
              properties:
                category_name:
                  type: string
                  default: Chicken
                response:
                  type: string
                  default: {'category_id': 1, 'category_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          409:
            description: Category name already exists
            schema:
              id: Already existing category name being added
              properties:
                category_name:
                  type: string
                  default: {'category_id': 1, 'category_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
                response:
                  type: string
                  default: Category name already exists.
        """
    # adds categories to the database
    # Query to see if the category already exists
    category = Category.query.filter(Category.user_id==user_id).filter_by(category_name=request.data['category_name']).first()

    if not category:
        if request.method == "POST":
            category_name = str(request.data.get('category_name', ''))
            #if validate.validate_name(category_name) == True:
            if category_name:
                category = Category(category_name=category_name, user_id=user_id)
                category.save()
                response = jsonify({
                    'category_id': category.category_id,
                    'category_name': category.category_name,
                    'date_created': category.date_created,
                    'date_modified': category.date_modified,
                    'recipes': url_for('recipe_api.create_recipes', category_id=category.category_id, _external=True),
                    'created_by' : user_id
                    })
                return make_response(response), 201
    # There is an existing category.
    response = {
        'message': 'Category already exists.'
    }
    return make_response(jsonify(response)), 409


@category_api.route('/categories/', methods=['GET'])
@auth
def view_categories(user_id):
    """
        Retrieves all created categories by that user
        ---
        tags:
          - Categories

        parameters:
          - in: query
            name: q
            required: false
            type: string
            description: This route retrieves all categories of that name
          - in: query
            name: page
            required: false
            type: integer
            description: This route retrieves all categories of that page number
          - in: query
            name: per_page
            required: false
            type: integer
            description: This route retrieves the specified number of categories on a page

        security:
          - TokenHeader: []

        responses:
          200:
            description: You successfully retrieved all categories
          201:
            description: Categories retrieved successfully
            schema:
              id: View categories
              properties:
                category_name by q:
                  type: string
                  default: ?q=Chick
                pagination:
                  type: string
                  default: ?page=1&per_page=1
                response:
                  type: string
                  default: {'category_id': 1, 'category_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          404:
            description: Url doesn't exist. Please type existing url
            schema:
              id: Invalid ID
              properties:
                category_id:
                  type: integer
                  default: 2
                response:
                  type: string
                  default: No category found
        """
    # retrieves categories from the database
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        q = str(request.args.get('q', '')).title()
        #GET all the categories created by this user
        #categories = Category.query.filter_by(user_id=user_id, category_name=q)
        categories = Category.query.filter(Category.user_id==user_id).filter(Category.category_name.like('%'+q+'%')).paginate(page, per_page, False)

        results = []

        for category in categories.items:
            obj = {
                'category_id': category.category_id,
                'category_name': category.category_name,
                'date_created': category.date_created,
                'date_modified': category.date_modified,
                'recipes': url_for('recipe_api.create_recipes', category_id=category.category_id, _external=True),
                'created_by' : user_id
            }
            results.append(obj)

        return make_response(jsonify(results)), 200


@category_api.route('/categories/<int:category_id>', methods=['GET'])
@auth
def view_one_category(user_id, category_id, **kwargs):
    """
        Retrieves a single category using it's ID
        ---
        tags:
          - Categories
        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
            description: This route retrieves a category using its ID
        security:
          - TokenHeader: []
        responses:
          200:
            description: Category retrieved successfully
            schema:
              id: View one category
              properties:
                category_id:
                  type: integer
                  default: 1
                response:
                  type: string
                  default: {'category_id': 1, 'category_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          404:
            description: Url doesn't exist. Please type existing url
            schema:
              id: Invalid ID
              properties:
                category_id:
                  type: integer
                  default: 2
                response:
                  type: string
                  default: No category found
        """
    # retrieve a category using it's ID
    user = RecipeApp.query.filter_by(user_id=user_id).first()
    category = user.categories.filter_by(category_id=category_id).first()
    if not category:
        # Raise an HTTPException with a 404 not found status code
        return {
        "message": "Url doesn't exist. Please type existing url"
        }, 404
    if request.method == 'GET':
    # GET a category
        response = jsonify({
            'category_id': category.category_id,
            'category_name': category.category_name,
            'date_created': category.date_created,
            'date_modified': category.date_modified,
            'recipes': url_for('recipe_api.create_recipes', category_id=category.category_id, _external=True)
        })
        response.status_code = 200
        return response


@category_api.route('/categories/<int:category_id>', methods=['PUT'])
@auth
def edit_category(user_id, category_id, **kwargs):
    """
        Updates a category of a specified ID
        ---
        tags:
          - Categories
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
            description: This routes edits a category
        security:
          - TokenHeader: []
        responses:
          200:
            description: You successfully retrieved a category using its ID
          201:
            description: Category edited successfully
            schema:
              id: Edit category
              properties:
                category_id:
                  default: 1
                category_name:
                  type: string
                  default: Chicken
                response:
                  type: string
                  default: {'category_id': 1, 'category_name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          404:
            description: Url doesn't exist. Please type existing url
            schema:
              id: Invalid ID
              properties:
                category_id:
                  type: integer
                  default: 2
                response:
                  type: string
                  default: No category found
        """
    user = RecipeApp.query.filter_by(user_id=user_id).first()
    category = user.categories.filter_by(category_id=category_id).first()
    if not category:
        # Raise an HTTPException with a 404 not found status code
        return {
        "message": "Url doesn't exist. Please type existing url"
        }, 404
    if request.method == 'PUT':
        # EDIT a category
        category_name = str(request.data.get('category_name', ''))
        category.category_name = category_name
        category.save()
        response = jsonify({
            'category_id': category.category_id,
            'category_name': category.category_name,
            'date_created': category.date_created,
            'date_modified': category.date_modified,
            'recipes': url_for('recipe_api.create_recipes', category_id=category.category_id, _external=True)
        })
        response.status_code = 200
        return response


@category_api.route('/categories/<int:category_id>', methods=['DELETE'])
@auth
def delete_category(user_id, category_id, **kwargs):
    """
        Deletes a category of a specified ID
        ---
        tags:
          - Categories

        parameters:
          - in: path
            name: category_id
            required: true
            type: integer
            description: Delete a category by specifying its ID

        security:
          - TokenHeader: []

        responses:
          200:
            description: You successfully retrieved a category using its ID
          201:
            description: Category created successfully
            schema:
              id: Delete category
              properties:
                category_id:
                  default: 1
                category_name:
                  type: string
                  default: Category 1 deleted
                response:
                  type: string
                  default: {'category_id': 1, 'name': Chicken, 'date_created': 22-12-2017, 'date_modified': 22-12-2017, 'created_by': 1}
          404:
            description: Url doesn't exist. Please type existing url
            schema:
               id: Invalid delete
               properties:
                 category_id:
                   type: integer
                   default: 2
                 response:
                   type: string
                   default: No category found to delete
    """
    user = RecipeApp.query.filter_by(user_id=user_id).first()
    category = user.categories.filter_by(category_id=category_id).first()
    if not category:
        # Raise an HTTPException with a 404 not found status code
        return {
        "message": "Url doesn't exist. Please type existing url"
        }, 404
    if request.method == 'DELETE':
        # DELETE a category
        category.delete()
        return {
        "message": "category {} deleted successfully".format(category.category_id)
        }, 200
