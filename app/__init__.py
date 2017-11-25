from flask import request, jsonify, abort
from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

"""POSTGRESTEST = {
'user': 'postgres',
'db': 'recipe_db',
'host': 'localhost',
'port': '5432',
}"""
# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    from app.models.category import Category
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config['development']) # app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()


    @app.route('/categories/', methods=['POST', 'GET'])
    def categories():
        if request.method == "POST":
            category_name = str(request.data.get('category_name', ''))
            if category_name:
                category = Category(category_name=category_name)
                category.save()
                response = jsonify({
                    'category_name': category.category_name,
                    'date_created': category.date_created,
                    'date_modified': category.date_modified
                })
                response.status_code = 201
                return response
        else:
            # GET
            categories = Category.get_all()
            results = []

            for category in categories:
                obj = {
                    'category_name': category.category_name,
                    'date_created': category.date_created,
                    'date_modified': category.date_modified
                }
                results.append(obj)
            response = jsonify(results)
            response.status_code = 200
            return response


    @app.route('/categories/<category_name>', methods=['GET', 'PUT', 'DELETE'])
    def category_edit_and_delete(category_name, **kwargs):
     # retrieve a buckelist using it's ID
        category = Category.query.filter_by(category_name=category_name).first()
        if not category:
            # Raise an HTTPException with a 404 not found status code
            abort(404)

        if request.method == 'DELETE':
            category.delete()
            return {
            "message": "category {} deleted successfully".format(category.category_name)
         }, 200

        elif request.method == 'PUT':
            category_name = str(request.data.get('category_name', ''))
            category.category_name = category_name
            category.save()
            response = jsonify({
                'category_name': category.category_name,
                'date_created': category.date_created,
                'date_modified': category.date_modified
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'category_name': category.category_name,
                'date_created': category.date_created,
                'date_modified': category.date_modified
            })
            response.status_code = 200
            return response

    return app
