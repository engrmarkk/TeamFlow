from flask import jsonify
import uuid
from flask_jwt_extended import create_access_token
import re
from random import randint, choice
import string
import datetime
import hmac
import hashlib
import base64
from io import BytesIO
import time


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


def return_user_dict(user):
    return user.to_dict()


def convert_binary(base64_file):
    try:
        print("got here")
        binary_data = base64.b64decode(base64_file)
        # Convert binary data to a file-like object
        file_like = BytesIO(binary_data)
        print(file_like, "file_like from convert_binary")
        return file_like
    except Exception as e:
        print(e, "error from convert_binary")
        return None


def generate_signature(params_to_sign, api_secret):
    try:
        params_to_sign['timestamp'] = int(time.time())
        sorted_params = '&'.join([f'{k}={params_to_sign[k]}' for k in sorted(params_to_sign)])
        to_sign = f'{sorted_params}{api_secret}'
        signature = hmac.new(api_secret.encode('utf-8'), to_sign.encode('utf-8'), hashlib.sha1).hexdigest()
        print(signature, "signature from generate_signature")
        return signature
    except Exception as e:
        print(e, "error from generate_signature")
        return None
