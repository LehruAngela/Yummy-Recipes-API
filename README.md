[![Build Status](https://travis-ci.org/LehruAngela/yummy-recipes-api.png)](https://travis-ci.org/LehruAngela/yummy-recipes-api)
[![Coverage Status](https://coveralls.io/repos/github/LehruAngela/yummy-recipes-api/badge.svg?branch=input-validation)](https://coveralls.io/github/LehruAngela/yummy-recipes-api?branch=develop)
<a href="https://codeclimate.com/github/LehruAngela/yummy-recipes-api/maintainability"><img src="https://api.codeclimate.com/v1/badges/7c19031b376098381b04/maintainability" /></a>

## Yummy-Recipes-API
This is a Flask API of the Yummy-Recipes that handles:
1. User authentication
2. Creating, reading, updating and deleting of recipe categories
3. Creating, reading, updating and deleting of recipes

#### To test the application and get it running, do the following:
1. Create the virtual environment and activate it
 ```
 $ mkvirtualenv my_project
 $ workon my_project
 ```
 
2. Install the requirements file for all the dependencies of the application
```
$ pip install -r requirements.txt
```

3. Create the database and run migrations
```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```

4. Run the application
```
$ python run.py
```

#### Features
Endpoint | Functionality
------------ | -------------
POST api-v1/auth/register | Registers a new user
POST api-v1/auth/login | Login a user
POST api-v1/categories/ | Creates a new category
GET api-v1/categories/ | Retrieves all created categories by that user
GET api-v1/categories/category_id | Retrieves a single category using it's ID
PUT api-v1/categories/category_id | Updates a category of a specified ID
DELETE api-v1/categories/category_id | Deletes a category of a specified ID
POST api-v1/categories/category_id/recipes/ | Creates a new recipe in a category 
GET api-v1/categories/category_id/recipes/ | Retrieves all created recipes in a category
GET api-v1/categories/category_id/recipes/recipe_id | Retrieves a single recipe using it's ID
PUT api-v1/categories/category_id/recipes/recipe_id | Updates a recipe in a category
DELETE api-v1/category/category_id/recipes/recipe_id | Deletes a recipe in a category
