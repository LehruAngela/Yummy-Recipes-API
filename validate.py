import re #regular expressions

def validate_password(password):
    if re.match(r'[a-zA-Z0-9]', password):
        return "True"

def validate_email(email):
    if re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email):
        return "True"

def validate_name(name):
    name = str(name)
    if re.match(r'[A-Za-z]', name): 
        return "True"
