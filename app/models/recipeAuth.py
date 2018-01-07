from sqlalchemy import Integer, ForeignKey, String, Column
from flask_bcrypt import Bcrypt
from flask import make_response, jsonify
from app import db
from instance.config import Config
import jwt
from datetime import datetime, timedelta

config = Config()

class RecipeApp(db.Model):
    """This class represents the recipeApp table."""

    __tablename__ = 'auth'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())
    categories = db.relationship(
            'Category', order_by='Category.category_id',
            cascade="all, delete-orphan",
            lazy='dynamic'
        )

    def __init__(self, email, password):
        """initialize"""
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        return Bcrypt().check_password_hash(self.password, password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def generate_token(self, user_id):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=1200),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                config.SECRET,
                algorithm='HS256'
            )
            return jwt_string

        except Exception as e:
            # return an error in string format if an exception occurs
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, config.SECRET)
            token_is_expired = ExpiredToken.check_expired_token(auth_token=token)
            if token_is_expired:
                response = {
                    'message': 'Expired token. Please login.'
                }
                return make_response(jsonify(response))
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"


class ExpiredToken(db.Model):
    """This class represents the expired_tokens table"""

    __tablename__ = 'expired_tokens'

    token_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    expired_on = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

    def __init__(self, token):
        self.token = token

    def save(self):
        """Save to expired_tokens table"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def check_expired_token(auth_token):
        """Checks if token is expired"""
        # check whether token has been revoked
        res = ExpiredToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
