import os

from flask import render_template, redirect
from flasgger import Swagger
from app import create_app
from instance.config import app_config

config_name = os.getenv('FLASK_CONFIG') #app.config['development']
app = create_app(config_name)

swag= Swagger(app,
   template={
       "info": {
       "title": "Yummy Recipes api-v1",
       "description": "API that registers and logs in a user so as to use the features and functionality of yummy recipes."},
       "securityDefinitions":{
           "TokenHeader": {
               "type": "apiKey",
               "name": "Authorization",
               "in": "header"
           }
       }
   })
@app.route("/")
def main():
    return redirect('/apidocs')


if __name__ == '__main__':
    app.run()
