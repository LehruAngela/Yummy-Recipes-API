from . import categories_blueprint

from flask.views import MethodView
from flask import Blueprint, make_response, request, jsonify
from app.models.category import Category

class CategoryView(MethodView):
    """This class allows a user use the CRUD features."""

    def post(self):
    """Handle POST request for this view. Url ---> /categories"""

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

categories_view = CategoryView.as_view('category_view')
# Define the rule for the registration url --->  /auth/register
# Then add the rule to the blueprint
categories_blueprint.add_url_rule(
'/categories',
view_func=categories_view,
methods=['POST'])
