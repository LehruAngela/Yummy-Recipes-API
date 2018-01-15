from . import auth_blueprint
import validate
from flask.views import MethodView
from flask import Blueprint, make_response, request, jsonify
from app.models.recipeAuth import RecipeApp, ExpiredToken
from flask_bcrypt import Bcrypt
from flasgger import swag_from

class RegistrationView(MethodView):
    """This class registers a new user."""
    @swag_from('/app/docs/register.yml')
    def post(self):
        """Handle POST request for this view. Url ---> /api/v1/auth/register. Query to see if the user already exists"""
        user = RecipeApp.query.filter_by(email=request.data['email']).first()

        if not user:
            # There is no user so we'll try to register them
            try:
                # Register the user
                email = request.data['email']
                password =  request.data['password']
                security_question = request.data['security_question']
                security_answer = request.data['security_answer']
                if not email or not password or not security_question or not security_answer:
                    response = {'message': 'All fields are required'}
                    return make_response(jsonify(response)), 400   
                if validate.validate_email(email) == "True":
                    if validate.validate_password(password) == "True":
                        user = RecipeApp(email=email, password=password, security_question=security_question, security_answer=security_answer)
                        user.save()
                        response = {'message': 'You registered successfully. Please log in.'}
                        # return a response notifying the user that they registered successfully
                        return make_response(jsonify(response)), 201
                    response = {'message': 'Password is short. Enter a password longer than 6 characters'}
                    return make_response(jsonify(response)), 400
                response = {'message': 'Invalid email! A valid email should in this format name@gmail.com' }
                return make_response(jsonify(response)), 401
            except Exception as e:
                # An error occured, therefore return a string message containing the error
                # response = {'message': str(e)}
                response = {'message': 'All fields are required'}
                return make_response(jsonify(response)), 400
        else:
            # There is an existing user.
            response = {'message': 'User already exists. Please login.'}
            return make_response(jsonify(response)), 409


class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""
    @swag_from('/app/docs/login.yml')
    def post(self):
        """Handle POST request for this view. Url ---> /auth/login"""
        email = request.data['email']
        password =  request.data['password']
        try:
            # Get the user object using their email (unique to every user)
            user = RecipeApp.query.filter_by(email=email).first()
            if not email or not password:
                response = {'message': 'All fields are required'}
                return make_response(jsonify(response)), 400
            # Try to authenticate the found user using their password
            if user and user.password_is_valid(password):
              # Generate the access token. This will be used as the authorization header
                access_token = user.generate_token(user.user_id)
                if access_token:
                    response = {
                        'message': 'You logged in successfully.',
                        'access_token': access_token.decode()}
                    return make_response(jsonify(response)), 200
            # User does not exist. Therefore, we return an error message
            response = {'message': 'Invalid email or password, Please try again'}
            return make_response(jsonify(response)), 403
        except Exception as e:
            # Create a response containing an string error message
            response = {'message': str(e)}
            return make_response(jsonify(response)), 500


class LogoutView(MethodView):
    @swag_from('/app/docs/logout.yml')
    def post(self):
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        if access_token:
            # Attempt to decode the token and get the User ID
            user_id = RecipeApp.decode_token(access_token)
            if not isinstance(user_id, str):
                # Handle the request if the user is authenticated"""
                expired_token = ExpiredToken(token=access_token)
                expired_token.save()
                return jsonify({'message': 'You have been logged out.'}),200
            else:
                message = user_id
                response = {'message': message}
                return make_response(jsonify(response)), 401
        else:
            return jsonify({'message': 'please provide a  valid token'})


class ResetPasswordView(MethodView):
    def post(self):
        #register user
        email = request.data['email']
        new_password = request.data['new_password']
        security_question = request.data['security_question']
        security_answer = request.data['security_answer']
        user = RecipeApp.query.filter_by(email=email,security_answer=security_answer).first()
        if user:
            user.password = Bcrypt().generate_password_hash(new_password).decode()
            user.save()
            response = {'message': 'Your password has been reset'}
            return make_response(jsonify(response)), 201
        response = {'message': 'wrong email or wrong security answer, try again'}
        return make_response(jsonify(response)), 401

# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
logout_view = LogoutView.as_view('logout_view')
reset_password_view = ResetPasswordView.as_view('reset_password_view')


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

# Define the rule for the logout url --->  /auth/logout
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)

# Define the rule for the reset password url --->  /auth/reset_password
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/reset_password',
    view_func=reset_password_view,
    methods=['POST'])