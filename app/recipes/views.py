from . import recipes_blueprint

from flask.views import MethodView
from flask import Blueprint, make_response, request, jsonify
from app.models.recipe import Recipe

class RecipeView(MethodView):
    """This class allows a user use the CRUD features."""
