from sqlalchemy import Integer, ForeignKey, String, Column

from .recipeAuth import RecipeApp
from app import db

class Category(db.Model):
    """This class represents the recipeApp table."""

    __tablename__ = 'category'

    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey(RecipeApp.user_id))
    recipes = db.relationship(
        'Recipe', order_by='Recipe.recipe_id', cascade="all, delete-orphan")

    def __init__(self, category_name, user_id, category_id=None, recipe_name=None):
        """initialize"""
        self.category_name = category_name
        self.category_id = category_id
        self.recipe_name = recipe_name
        self.user_id = user_id

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Category.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Category: {}>".format(self.category_name)