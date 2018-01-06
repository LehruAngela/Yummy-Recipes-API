from . import auth_blueprint
import validate
from flask.views import MethodView
from flask import Blueprint, make_response, request, jsonify
from app.models.recipeAuth import RecipeApp

class RegistrationView(MethodView):
    """This class registers a new user."""

    def post(self):
        """
            Register a new user
            ---
            tags:
              - Users
            parameters:
              - in: body
                name: body
                required: true
                type: string
                description: This route registers a new user
            responses:
              200:
                description: You successfully registered
              201:
                description: User registered successfully
                schema:
                  id: Register user
                  properties:
                    email:
                      type: string
                      default: angela.lehru@andela.com
                    password:
                      type: string
                      default: 1234567
                    response:
                      type: string
                      default: You registered successfully. Please log in.
              500:
                description: An error has occured
              409:
                description: User already exists. Please login.
        """
        """Handle POST request for this view. Url ---> /api/v1/auth/register"""
        # Query to see if the user already exists
        user = RecipeApp.query.filter_by(email=request.data['email']).first()

        if not user:
            # There is no user so we'll try to register them
            try:
                # Register the user
                email = request.data['email']
                password =  request.data['password']
                if validate.validate_email(email) == "True" and validate.validate_password(password) == "True":
                    user = RecipeApp(email=email, password=password)
                    user.save()

                    response = {
                        'message': 'You registered successfully. Please log in.'
                    }
                    # return a response notifying the user that they registered successfully
                    return make_response(jsonify(response)), 201
            except Exception as e:
                # An error occured, therefore return a string message containing the error
                response = {
                    'message': str(e)
                }
                return make_response(jsonify(response)), 500
        else:
            # There is an existing user.
            response = {
                'message': 'User already exists. Please login.'
            }

            return make_response(jsonify(response)), 409

registration_view = RegistrationView.as_view('register_view')
# Define the rule for the registration url --->  /auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST'])


class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""

    def post(self):
        """
            Log in a user
            ---
            tags:
              - Users
            parameters:
              - in: body
                name: body
                required: true
                type: string
                description: This route logs in a user
            responses:
              200:
                description: User logged in successfully
              201:
                description: You logged in successfully
                schema:
                  id: successful login
                  properties:
                    email:
                      type: string
                      default: angela.lehru@andela.com
                    password:
                      type: string
                      default: 1234567
                    response:
                      type: string
                      default: {'access_token': "eyJ0eXAiOiJKV1QiLCJhbGci", 'message': You logged in successfully}
              401:
                description: User does not exist.
                schema:
                  id: Invalid password or email
                  properties:
                    email:
                      type: string
                      default: angela.lehru1@andela.com
                    password:
                      type: string
                      default: 9987794
                    response:
                      type: string
                      default: Invalid email or password, Please try again
              500:
               description: An error has occured

        """
        """Handle POST request for this view. Url ---> /auth/login"""
        try:
            # Get the user object using their email (unique to every user)
            user = RecipeApp.query.filter_by(email=request.data['email']).first()

            # Try to authenticate the found user using their password
            if user and user.password_is_valid(request.data['password']):
                # Generate the access token. This will be used as the authorization header
                access_token = user.generate_token(user.user_id)
                if access_token:
                    response = {
                        'message': 'You logged in successfully.',
                        'access_token': access_token.decode()
                    }
                    return make_response(jsonify(response)), 201
            else:
                # User does not exist. Therefore, we return an error message
                response = {
                    'message': 'Invalid email or password, Please try again'
                }
                return make_response(jsonify(response)), 401

        except Exception as e:
            # Create a response containing an string error message
            response = {
                'message': str(e)
            }
            return make_response(jsonify(response)), 500

# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')

# Define the rule for the registration url --->  /auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/register',
    view_func=registration_view,
    methods=['POST'])

# Define the rule for the registration url --->  /auth/login
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/login',
    view_func=login_view,
    methods=['POST']
)
