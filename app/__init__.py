from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    from app.models.category import Category
    from app.models.recipe import Recipe
    from app.models.recipeAuth import RecipeApp
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config['development']) # app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Blueprints
    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    # import the category blueprint and register it on the app
    from .categories import category_api
    app.register_blueprint(category_api)

    # import the recipe blueprint and register it on the app
    from .recipes import recipe_api
    app.register_blueprint(recipe_api)

    return app
