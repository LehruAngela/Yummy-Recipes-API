from sqlalchemy import Integer, ForeignKey, String, Column
from app import db
from category import Category

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
    category_id = db.Column(db.Integer, db.ForeignKey(Category.category_id))


    def __init__(self, recipe_name, ingredients=None, directions=None):
        self.recipe_name = recipe_name
        self.ingredients = ingredients
        self.directions = directions

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
