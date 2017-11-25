from sqlalchemy import Integer, ForeignKey, String, Column
from app import db

class RecipeApp(db.Model):
    """This class represents the recipeApp table."""

    __tablename__ = 'auth'

    email = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, email, username, password):
        """initialize"""
        self.email = email
        self.username = username
        self.password = password

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return RecipeApp.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<RecipeApp: {}>".format(self.name)
