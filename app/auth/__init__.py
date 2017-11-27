from flask import Blueprint

# This is the instance of a Blueprint that represents the authentication blueprint
auth_blueprint = Blueprint('auth', __name__)

from . import views
