from flask import Blueprint, request
from utils import (
    return_response,
    return_access_token,
    is_valid_email,
    validate_password,
)
from http_status import HttpStatus
from status_res import StatusRes
from models import (
    authenticate,
    username_exist,
    email_exist,
    email_exist,
    create_user,
    create_otp,
    get_user_by_email,
    create_reset_p,
    get_user_by_reset_p,
    update_password,
    check_if_org_exist, create_org
)
from datetime import datetime
import traceback

auth = Blueprint("auth", __name__)

AUTH_PREFIX = "auth"


@auth.route("/")
def test_endpoint():
    return return_response(
        HttpStatus.OK, status=StatusRes.SUCCESS, message="Welcome to TeamFlow"
    )


@auth.route(f"/{AUTH_PREFIX}/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        print(email, password)

        if not email or not password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email and Password are required",
            )
        user = authenticate(email.lower(), password)
        if user:
            if not user.email_verified:
                return return_response(
                    HttpStatus.FORBIDDEN,
                    status=StatusRes.FAILED,
                    message="Email not verified",
                )
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Login Successful",
                access_token=return_access_token(user),
            )
        return return_response(
            HttpStatus.NOT_FOUND,
            status=StatusRes.FAILED,
            message="Invalid Email or Password",
        )
    except Exception as e:
        print(e, "error@auth/login")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@auth.route(f"/{AUTH_PREFIX}/register", methods=["POST"])
def register():
    try:
        from celery_config.utils.cel_workers import send_mail

        data = request.get_json()
        first_name = data.get("first_name")
        organization_name = data.get("organization_name")
        organization_desc = data.get("organization_description")
        last_name = data.get("last_name")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not first_name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="First Name is required",
            )

        if not last_name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Last Name is required",
            )

        if not username:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Username is required",
            )

        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required",
            )

        if not password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Password is required",
            )

        if not organization_name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Organization Name is required",
            )

        if not organization_desc:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Organization Description is required",
            )

        username = username.lower()
        email = email.lower()
        first_name = first_name.lower()
        last_name = last_name.lower()
        organization_name = organization_name.lower()

        if not is_valid_email(email):
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid Email Format"
            )

        val_pass = validate_password(password)
        if val_pass:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message=val_pass
            )

        if username_exist(username):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Username already exists",
            )

        if email_exist(email):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email already exists",
            )

        if check_if_org_exist(organization_name):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Organization already exists",
            )

        org_id = create_org(organization_name, organization_desc.lower())

        user = create_user(first_name, last_name, username, email, password, org_id,
                           is_super_admin=True, is_admin=True)
        usersession = create_otp(user.id)
        otp = usersession.otp
        print(otp, "otp")
        # send mail to the user

        payload = {
            "email": email,
            "subject": "Welcome to TeamFlow",
            "template_name": "otp.html",
            "name": f"{last_name.title()} {first_name.title()}",
            "otp": otp,
            "date": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        }
        print("Calling celery")
        send_mail.delay(payload)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Please check your email for OTP to verify your account",
            user_email=user.email,
        )
    except Exception as e:
        print(e, "error@auth/register")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# verify email
@auth.route(f"/{AUTH_PREFIX}/verify-email", methods=["PATCH"])
def verify_email():
    try:
        data = request.get_json()
        otp = data.get("otp")
        email = data.get("email")
        if not otp:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="OTP is required",
            )
        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required",
            )
        # to check if email is in a valid format
        if not is_valid_email(email):
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid Email Format"
            )
        user = get_user_by_email(email.lower())
        if not user:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User not found",
            )
        if user.email_verified:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email already verified",
            )
        if user.usersession.otp == otp:
            if user.usersession.otp_expiry < datetime.now():
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="OTP expired",
                )
            user.email_verified = True
            user.update()
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Email verified successfully",
            )
        return return_response(
            HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid OTP"
        )
    except Exception as e:
        print(e, "error@auth/verify-email")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# resend otp
@auth.route(f"/{AUTH_PREFIX}/resend-otp", methods=["POST"])
def resend_otp():
    try:
        from celery_config.utils.cel_workers import send_mail

        data = request.get_json()
        email = data.get("email")
        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required",
            )
        user = get_user_by_email(email.lower())
        if not user:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User not found",
            )
        if user.email_verified:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email already verified",
            )
        usersession = create_otp(user.id)
        print(usersession.otp, "otp")
        # send mail to the user
        payload = {
            "email": email,
            "subject": "Welcome to TeamFlow",
            "template_name": "otp.html",
            "name": f"{user.last_name.title()} {user.first_name.title()}",
            "otp": usersession.otp,
            "date": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        }
        print("calling celery")
        send_mail.delay(payload)
        return return_response(
            HttpStatus.OK, status=StatusRes.SUCCESS, message="OTP sent successfully"
        )
    except Exception as e:
        print(traceback.format_exc(), "error@auth/resend-otp TRACEBACK")
        print(e, "error@auth/resend-otp")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# reset password
@auth.route(f"/{AUTH_PREFIX}/reset-password", methods=["POST"])
def reset_password():
    try:
        from celery_config.utils.cel_workers import send_mail

        data = request.get_json()
        email = data.get("email")
        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required",
            )
        user = get_user_by_email(email.lower())
        if not user:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User not found",
            )
        usersession = create_reset_p(user.id)
        print(usersession.reset_p, "reset_p")
        # send mail to the user
        payload = {
            "email": email,
            "subject": "Reset Password",
            "template_name": "token.html",
            "name": f"{user.last_name.title()} {user.first_name.title()}",
            "token": usersession.reset_p,
            "date": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        }
        send_mail.delay(payload)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Password reset link sent successfully",
        )
    except Exception as e:
        print(e, "error@auth/reset-password")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# verify reset password
@auth.route(f"/{AUTH_PREFIX}/verify-reset-password", methods=["POST"])
def verify_reset_password():
    try:
        data = request.get_json()
        reset_p = data.get("reset_p")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        if not reset_p:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Reset password is required",
            )
        if not new_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="New password is required",
            )
        if not confirm_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Confirm password is required",
            )
        if new_password != confirm_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Passwords do not match",
            )
        usersession = get_user_by_reset_p(reset_p)
        if not usersession:
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid Token"
            )
        if usersession.reset_p_expiry < datetime.now():
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Token expired"
            )
        update_password(usersession.user, new_password)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Password reset successfully",
        )

    except Exception as e:
        print(e, "error@auth/verify-reset-password")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# resend reset password
@auth.route(f"/{AUTH_PREFIX}/resend-reset-password", methods=["POST"])
def resend_reset_password():
    try:
        from celery_config.utils.cel_workers import send_mail

        data = request.get_json()
        email = data.get("email")
        if not email:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Email is required",
            )
        user = get_user_by_email(email.lower())
        if not user:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User not found",
            )
        usersession = create_reset_p(user.id)
        print(usersession.reset_p, "reset_p")
        # send mail to the user
        payload = {
            "email": email,
            "subject": "Reset Password",
            "template_name": "token.html",
            "name": f"{user.last_name.title()} {user.first_name.title()}",
            "token": usersession.reset_p,
            "date": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        }
        send_mail.delay(payload)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Password reset link sent successfully",
        )
    except Exception as e:
        print(e, "error@auth/resend-reset-password")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
