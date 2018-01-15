from . import category_api
from functools import wraps
from flask import Blueprint, make_response, request, jsonify, url_for
from app.models.category import Category
from app.models.recipe import Recipe
from app.models.recipeAuth import RecipeApp, ExpiredToken
import validate

def auth(func):
    @wraps(func)
    def user_login(*args, **kwargs):
        """Get the access token from the header"""
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            response = {'message': 'No token provided. Please provide a valid token.'}
            return make_response(jsonify(response)), 401
        access_token = auth_header.split(" ")[1]

        if ExpiredToken.check_expired_token(access_token) == False:
            # Attempt to decode the token and get the User ID
            user_id = RecipeApp.decode_token(access_token)
            if not isinstance(user_id, str):
                # Handle the request if the user is authenticated"""
                return func(user_id, *args, **kwargs)
            return None
        response = {'message': 'Please login'}
        return make_response(jsonify(response)), 401
    return user_login


@category_api.route('/categories/', methods=['POST'])
@auth
def create_categories(user_id):
    """adds categories to the database
    Query to see if the category already exists"""
    category = Category.query.filter(Category.user_id==user_id).filter_by(category_name=request.data['category_name']).first()

    if not category:
        if request.method == "POST":
            category_name = str(request.data.get('category_name', ''))
            if category_name is None:
                response = {'message': 'No content provided.'}
                return make_response(jsonify(response)), 400
            category_name.strip()
            if category_name:
                if validate.validate_name(category_name) == "True":
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
            response = {'message': 'Category name required.'}
            return make_response(jsonify(response)), 422
    # There is an existing category.
    response = {'message': 'Category already exists.'}
    return make_response(jsonify(response)), 409


@category_api.route('/categories/', methods=['GET'])
@auth
def view_categories(user_id):
    """retrieves categories from the database"""
    if request.method == "GET":
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 5))
        q = str(request.args.get('q', ''))
        #GET all the categories created by this user
        categories = Category.query.filter(Category.user_id==user_id).filter(Category.category_name.ilike('%'+q+'%')).paginate(page, per_page, False)

        if categories.total <= 0:
            return make_response(jsonify({'msg': 'no categories found'})), 404

        if categories.items:
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
        else:
            return make_response(jsonify({'msg': 'Page not found'})), 422
    

@category_api.route('/categories/<int:category_id>', methods=['GET'])
@auth
def view_one_category(user_id, category_id, **kwargs):
    """retrieve a category using it's ID"""
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
        response.status_code = 201
        return response


@category_api.route('/categories/<int:category_id>', methods=['PUT'])
@auth
def edit_category(user_id, category_id, **kwargs):
    """edit a category using it's ID"""
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
        response.status_code = 201
        return response


@category_api.route('/categories/<int:category_id>', methods=['DELETE'])
@auth
def delete_category(user_id, category_id, **kwargs):
    """delete a category using it's ID"""
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