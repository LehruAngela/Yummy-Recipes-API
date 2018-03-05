from sqlalchemy import Integer, ForeignKey, String, Column

from app import db
from .category import Category
from .recipeAuth import RecipeApp

class Recipe(db.Model):
    """This class represents the recipeApp table."""

    __tablename__ = 'recipe'

    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_name = db.Column(db.String(255))
    ingredients = db.Column(db.String(255))
    directions = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey(RecipeApp.user_id))
    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id))


    def __init__(self, recipe_name, category_id, user_id, ingredients=None, directions=None):
        self.recipe_name = recipe_name.title()
        self.ingredients = ingredients
        self.directions = directions
        self.category_id = category_id
        self.user_id = user_id

    def recipe_json(self):
        """This method jsonifies the recipe model"""
        return {'recipe_id': self.recipe_id,
                'recipe_name': self.recipe_name,
                'ingredients': self.ingredients,
                'directions': self.directions,
                'date_created': self.date_created,
                'date_modified': self.date_modified,
                'created_by' : self.user_id, 
                'category_id': self.category_id}

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Recipe.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Recipe: {}>".format(self.name)