from . import category_api
from flask import Blueprint, make_response, request, jsonify, url_for
from app.models.category import Category
from app.models.recipe import Recipe
from app.models.recipeAuth import RecipeApp

@category_api.route('/categories/', methods=['GET','POST'])
def create_and_view_categories():
    # retrieves/adds categories from/to the database
    # Get the access token from the header
    auth_header = request.headers.get('Authorization')
    access_token = auth_header.split(" ")[1]

    if access_token:
        # Attempt to decode the token and get the User ID
        user_id = RecipeApp.decode_token(access_token)
        if not isinstance(user_id, str):
            # Handle the request if the user is authenticated
            if request.method == "POST":
                category_name = str(request.data.get('category_name', ''))
                if category_name:
                    category = Category(category_name=category_name, user_id=user_id)
                    category.save()
                    response = jsonify({
                        'category_id': category.category_id,
                        'category_name': category.category_name,
                        'date_created': category.date_created,
                        'date_modified': category.date_modified,
                        'recipes': url_for('recipes', category_id=category.category_id, _external=True),
                        'created_by' : user_id
                        })
                    return make_response(response), 201

            else:
                #GET all the categories created by this user
                categories = Category.query.filter_by(user_id=user_id)
                results = []

                for category in categories:
                    obj = {
                        'category_id': category.category_id,
                        'category_name': category.category_name,
                        'date_created': category.date_created,
                        'date_modified': category.date_modified,
                        'recipes': url_for('recipes', category_id=category.category_id, _external=True),
                        'created_by' : user_id
                    }
                    results.append(obj)

                return make_response(jsonify(results)), 200


@category_api.route('/categories/<int:category_id>', methods=['GET', 'PUT', 'DELETE'])
def category_edit_and_delete(category_id, **kwargs):
    # retrieve a buckelist using it's ID
    category = Category.query.filter_by(category_id=category_id).first()
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

    elif request.method == 'PUT':
        # EDIT a category
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
        # GET a category
        response = jsonify({
            'category_id': category.category_id,
            'category_name': category.category_name,
            'date_created': category.date_created,
            'date_modified': category.date_modified,
            'recipes': url_for('recipes', category_id=category.category_id, _external=True)
        })
        response.status_code = 200
        return response
