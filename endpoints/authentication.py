from flask import Blueprint, request
from utils import return_response, return_access_token, is_valid_email, validate_password
from http_status import HttpStatus
from status_res import StatusRes
from models import (authenticate,
                    username_exist, email_exist,
                    create_user, create_otp,
                    get_user_by_email, create_reset_p,
                    get_user_by_reset_p, update_password)
from datetime import datetime


auth = Blueprint('auth', __name__)


AUTH_PREFIX = 'auth'


@auth.route('/')
def test_endpoint():
    return return_response(HttpStatus.OK, status=StatusRes.SUCCESS, message="Welcome to TeamFlow", data={})


@auth.route(f'/{AUTH_PREFIX}/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        print(email, password)

        if not email or not password:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Email and Password are required", data={})
        user = authenticate(email.lower(), password)
        if user:
            if not user.email_verified:
                return return_response(HttpStatus.FORBIDDEN, status=StatusRes.FAILED, message="Email not verified",
                                       data={})
            return return_response(HttpStatus.OK, status=StatusRes.SUCCESS, message="Login Successful", data={
                "access_token": return_access_token(user)
            })
        return return_response(HttpStatus.NOT_FOUND, status=StatusRes.FAILED, message="Invalid Email or Password",
                               data={})
    except Exception as e:
        print(e, "error@auth/login")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error", data={})


@auth.route(f'/{AUTH_PREFIX}/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Username is required", data={})

        if not email:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Email is required", data={})

        if not password:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Password is required", data={})

        username = username.lower()
        email = email.lower()

        if not is_valid_email(email):
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Invalid Email", data={})

        val_pass = validate_password(password)
        if val_pass:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message=val_pass, data={})

        if username_exist(username):
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Username already exists", data={})

        if email_exist(email):
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Email already exists", data={})
        user = create_user(username, email, password)
        usersession = create_otp(user.id)
        otp = usersession.otp
        print(otp, "otp")
        # send mail to the user
        return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                               message="Please check your email for OTP to verify your account",
                               data={"user_email": user.email})
    except Exception as e:
        print(e, "error@auth/register")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error", data={})


# verify email
@auth.route(f'/{AUTH_PREFIX}/verify-email', methods=['POST'])
def verify_email():
    try:
        data = request.get_json()
        otp = data.get("otp")
        email = data.get("email")
        if not otp:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="OTP is required", data={})
        if not email:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Email is required", data={})
        user = get_user_by_email(email.lower())
        if not user:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="User not found", data={})
        if user.email_verified:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Email already verified", data={})
        if user.usersession.otp == otp:
            user.email_verified = True
            user.update()
            return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                                   message="Email verified successfully", data={})
        return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                               message="Invalid OTP", data={})
    except Exception as e:
        print(e, "error@auth/verify-email")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error", data={})


# resend otp
@auth.route(f'/{AUTH_PREFIX}/resend-otp', methods=['POST'])
def resend_otp():
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Email is required", data={})
        user = get_user_by_email(email.lower())
        if not user:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="User not found", data={})
        otp = create_otp(user.id)
        print(otp, "otp")
        # send mail to the user
        return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                               message="OTP sent successfully", data={})
    except Exception as e:
        print(e, "error@auth/resend-otp")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error", data={})


# reset password
@auth.route(f'/{AUTH_PREFIX}/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Email is required", data={})
        user = get_user_by_email(email.lower())
        if not user:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="User not found", data={})
        usersession = create_reset_p(user.id)
        print(usersession.reset_p, "reset_p")
        # send mail to the user
        return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                               message="Password reset link sent successfully", data={})
    except Exception as e:
        print(e, "error@auth/reset-password")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error", data={})


# verify reset password
@auth.route(f'/{AUTH_PREFIX}/verify-reset-password', methods=['POST'])
def verify_reset_password():
    try:
        data = request.get_json()
        reset_p = data.get("reset_p")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        if not reset_p:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Reset password is required", data={})
        if not new_password:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="New password is required", data={})
        if not confirm_password:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Confirm password is required", data={})
        if new_password != confirm_password:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Passwords do not match", data={})
        usersession = get_user_by_reset_p(reset_p)
        if not usersession:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                message="Invalid Token", data={})
        if usersession.reset_p_expiry < datetime.now():
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Token expired", data={})
        update_password(usersession.user, new_password)
        return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                               message="Password reset successfully", data={})

    except Exception as e:
        print(e, "error@auth/verify-reset-password")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error", data={})


# resend reset password
@auth.route(f'/{AUTH_PREFIX}/resend-reset-password', methods=['POST'])
def resend_reset_password():
    try:
        data = request.get_json()
        email = data.get("email")
        if not email:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Email is required", data={})
        user = get_user_by_email(email.lower())
        if not user:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="User not found", data={})
        usersession = create_reset_p(user.id)
        print(usersession.reset_p, "reset_p")
        # send mail to the user
        return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                               message="Password reset link sent successfully", data={})
    except Exception as e:
        print(e, "error@auth/resend-reset-password")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error", data={})
