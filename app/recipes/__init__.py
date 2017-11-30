from flask import Blueprint

# This is the instance of a Blueprint that represents the authentication blueprint
recipes_blueprint = Blueprint('recipes', __name__)

from . import views
