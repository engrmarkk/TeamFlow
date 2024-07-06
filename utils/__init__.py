from flask import jsonify
import uuid
from flask_jwt_extended import create_access_token
import re
from random import randint, choice
import string
import datetime


def return_response(status_code, status=None, message=None, **data):
    res_data = {
        "status": status,
        "message": message,
    }
    res_data.update(data)

    return jsonify(res_data), status_code


def gen_uuid():
    return str(uuid.uuid4())


def return_access_token(user):
    return create_access_token(identity=user.id, expires_delta=datetime.timedelta(days=1))


def is_valid_email(email):
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    if re.fullmatch(regex, email):
        return True
    return False


def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long"
    if not re.search("[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search("[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search("[0-9]", password):
        return "Password must contain at least one digit"
    if not re.search("[_@$]", password):
        return "Password must contain at least one special character"
    return None


def generate_otp():
    return str(randint(100000, 999999))


def generate_random_string(length=20):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(choice(characters) for _ in range(length))
    return random_string

