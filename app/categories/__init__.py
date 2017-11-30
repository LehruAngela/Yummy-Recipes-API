from flask import Blueprint

# This is the instance of a Blueprint that represents the authentication blueprint
categories_blueprint = Blueprint('categories', __name__)

from . import views
