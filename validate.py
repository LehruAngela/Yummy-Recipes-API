import re #regular expressions
from flask import make_response, jsonify

def validate_email(email):
    if re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email):
        return "True"

def validate_password(password):
    if len(password) >= 6:
        return "True"

def validate_name(name):
    return "True"
    # name = str(name)
    # if re.match(r'(?=.*[A-Za-z]*$)', name):
    #     return "True"
    #     if not re.match(r"(^[ ]*$)", name):
    #         return "True"
    #     response = {'message':'A space is not a name'}
    #     return make_response(jsonify(response)), 401
    # response = {'message': 'Name should be in alphabetical'}
    # return make_response(jsonify(response)), 401
