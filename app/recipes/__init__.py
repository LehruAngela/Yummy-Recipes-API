from flask import Blueprint

# This is the instance of a Blueprint that represents the recipes blueprint
recipe_api = Blueprint('recipe_api', __name__, url_prefix='/api-v1')

from . import views
