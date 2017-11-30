from flask import Blueprint

# This is the instance of a Blueprint that represents the categories blueprint
category_api = Blueprint('category_api', __name__, url_prefix='/api-v1')

from . import views
api = Blueprint('api', __name__, url_prefix='/api-v1')
