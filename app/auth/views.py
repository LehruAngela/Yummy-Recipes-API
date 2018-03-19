import os

from flask import Blueprint, make_response, request, jsonify, Flask
from flask.views import MethodView
from flask_bcrypt import Bcrypt
from flasgger import swag_from
import jwt
import datetime
from flask_mail import Mail, Message

from app.models.recipeAuth import RecipeApp, ExpiredToken
from . import auth_blueprint
import validate

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

recipients = []

class RegistrationView(MethodView):
    """This class registers a new user."""
    @swag_from('/app/docs/register.yml')
    def post(self):
        user = RecipeApp.query.filter_by(email=request.data['email']).first()
        if user:
            return make_response(jsonify({'message': 'User already exists. Please login or use another email.'})), 409
        try:
            # Register the user
            email = request.data['email']
            username = request.data['username']
            password =  request.data['password']
            confirm_password =  request.data['confirm_password']
            if not email or not password or not confirm_password:
                return make_response(jsonify({'message': 'All fields are required'})), 400   
            if validate.validate_email(email) != "True":
                return make_response(jsonify({'message': 'Invalid email! A valid email should in this format name@gmail.com' })), 401
            if validate.validate_password(password) != "True":
                return make_response(jsonify({'message': 'Password is short. Enter a password longer than 6 characters'})), 400
            if password != confirm_password:
                return make_response(jsonify({'message': 'Passwords do not match'})), 400
            else:
                user = RecipeApp(email=email, password=password, username=username)
                user.save()
                return make_response(jsonify({'message': 'You registered successfully.', 'username':username})), 201
        except Exception as e:
            return make_response(jsonify({'message': str(e)})), 400
        

class LoginView(MethodView):
    """This class-based view handles user login and access token generation."""
    @swag_from('/app/docs/login.yml')
    def post(self):
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
                        'access_token': access_token.decode(),
                        'username':user.username}
                    return make_response(jsonify(response)), 200
            return make_response(jsonify({'message': 'Invalid email or password, Please try again'})), 403
        except Exception as e:
            # Create a response containing an string error message
            return make_response(jsonify({'message': str(e)})), 500


class LogoutView(MethodView):
    @swag_from('/app/docs/logout.yml')
    def post(self):
        if request.method == "POST":
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
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            response = {
                'message': 'No token provided. Please provide a valid token.'}
            return make_response(jsonify(response)), 401
        access_token = auth_header.split(" ")[1]
        if access_token:
            #register user
            email = request.data['email'].strip()
            new_password = request.data['new_password'].strip()
            confirm_new_password = request.data['confirm_new_password'].strip()

            if not email or not new_password or not confirm_new_password:
                return make_response(jsonify({'message':'All fields are required'}))

            if validate.validate_email(email) == "False":
                return make_response(jsonify({'message':'Invalid email format'}))

            if validate.validate_password(new_password) == "False":
                return make_response(jsonify({'message': 'Password is short. Enter a password longer than 6 characters'}))

            if new_password != confirm_new_password:
                return make_response(jsonify({'message': 'Password mismatch'}))

            user = RecipeApp.query.filter_by(email=email).first()
            if user:
                user.password = Bcrypt().generate_password_hash(new_password).decode()
                user.save()
                response = {'message': 'Your password has been reset'}
                return make_response(jsonify(response)), 201
            return make_response(jsonify({'message': 'Email does not exist, try again'})), 401
        return make_response(jsonify({'message': 'Invalid token'})), 401


class SendEmailView(MethodView):
    """ This will send an email with the token to reset password."""
    def post(self):
    # This method will edit the already existing password
        email = request.data['email'].strip()
        print(email)
        user = RecipeApp.query.filter_by(email=email).first()
        if not email:
            return make_response(jsonify({'message': 'Please input the email'})), 412

        if validate.validate_email(email) == "False":
                return make_response(jsonify({'message':'Invalid email format'})),401
        if not user:
            return make_response(jsonify({'message': 'User does not exist!'})), 404
        try:
            access_token = jwt.encode({'id': user.user_id, 'expiry_time': str(datetime.datetime.utcnow() +
            datetime.timedelta(minutes=30))},
            os.getenv('SECRET', '$#%^%$^%@@@@@56634@@@'))
            print(access_token)
            subject = "Yummy Recipes Reset Password"
            recipients.append(email)
            msg = Message(subject, sender="Admin", recipients=recipients)
            styles = "background-color:blue; color:white; padding: 5px 10px; border-radius:3px; text-decoration: none;"
            msg.html = f"Click the link to reset password:\n \n<h3><a href='http://localhost:3000/resetpassword?tk={access_token.decode()}' style='{styles}'>Reset Password</a></h3>"
            print(msg.html)
            with app.app_context():
                
                mail.send(msg)
            return make_response(jsonify({'message': 'Password Reset link sent successfully to '+email+''})), 201
        except Exception as e:
            return make_response(jsonify({'message': 'Invalid request sent.'})), 400

# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
logout_view = LogoutView.as_view('logout_view')
reset_password_view = ResetPasswordView.as_view('reset_password_view')
send_email_view = SendEmailView.as_view('send_email_view')


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

# Define the rule for the send email url --->  /auth/send_email
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/auth/send_email',
    view_func=send_email_view,
    methods=['POST'])