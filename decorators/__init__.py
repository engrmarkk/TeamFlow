from functools import wraps
from flask_jwt_extended import current_user
from status_res import StatusRes
from http_status import HttpStatus
from utils import return_response


# decorator for email verified
def email_verified_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.email_verified:
            return return_response(HttpStatus.FORBIDDEN,
                                   status=StatusRes.FAILED, message="You are yet to verify your email address")
        return f(*args, **kwargs)
    return decorated


# super admin required
def super_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_super_admin:
            return return_response(HttpStatus.FORBIDDEN,
                                   status=StatusRes.FAILED,
                                   message="You are not authorized to perform this action")
        return f(*args, **kwargs)
    return decorated
