from flask import Blueprint, request
from utils import return_response, return_user_dict
from http_status import HttpStatus
from status_res import StatusRes
from flask_jwt_extended import current_user, jwt_required
from utils import is_valid_email
from sqlalchemy.exc import IntegrityError
from models import (
    current_user_info,
    create_project,
    get_user_ids_by_project_id,
    get_all_users, get_users_by_organization,
    create_task,
    create_user,
    email_exist, username_exist, create_otp,
    get_task,
    get_one_project, get_projects,
    get_task_for_project,
)
from decorators import email_verified_required, super_admin_required
from datetime import datetime


account = Blueprint("account", __name__)

ACCOUNT_PREFIX = "account"


@account.route(f"/{ACCOUNT_PREFIX}/dashboard", methods=["GET"])
@jwt_required()
@email_verified_required
def dashboard():
    return return_response(
        HttpStatus.OK,
        status=StatusRes.SUCCESS,
        message="User Dashboard",
        user_info=current_user_info(current_user),
        role=(
            "super_admin" if current_user.is_super_admin
            else "admin" if current_user.is_admin
            else "user"
        ),
    )


# get staffs/users
@account.route(f"/{ACCOUNT_PREFIX}/users", methods=["GET"])
@jwt_required()
@email_verified_required
# super admin required
@super_admin_required
def get_all_users_endpoint():
    users = get_users_by_organization(current_user.organization_id)
    return return_response(
        HttpStatus.OK,
        status=StatusRes.SUCCESS,
        message="All Users",
        users=[return_user_dict(user) for user in users],
        organization=current_user.organization.name.title()
    )


@account.route(f"/{ACCOUNT_PREFIX}/create-user", methods=["POST"])
@jwt_required()
@email_verified_required
# super admin required
@super_admin_required
def create_user_endpoint():
    try:
        from celery_config.utils.cel_workers import send_mail

        data = request.get_json()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        is_admin = data.get("is_admin", False)
        is_super_admin = data.get("is_super_admin", False)
        if not first_name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="First name is required",
            )
        if not last_name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Last name is required",
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
        if is_admin and is_super_admin:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Cannot create admin and super admin at the same time",
            )
        username = username.lower()
        email = email.lower()
        first_name = first_name.lower()
        last_name = last_name.lower()

        if not is_valid_email(email):
            return return_response(
                HttpStatus.BAD_REQUEST, status=StatusRes.FAILED, message="Invalid Email Format"
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
        if not isinstance(is_admin, bool) or not isinstance(is_super_admin, bool):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="is_admin and is_super_admin must be boolean",
            )
        is_admin = True if is_admin or is_super_admin else False
        user = create_user(first_name, last_name, username,
                           email, password, current_user.organization_id,
                           is_admin=is_admin, is_super_admin=is_super_admin)

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
            message="User created successfully",
            user=user.to_dict(),
        )

    except Exception as e:
        print(e, "error@account/create-user")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# create project endpoint
@account.route(f"/{ACCOUNT_PREFIX}/create-project", methods=["POST"])
@jwt_required()
@email_verified_required
def create_project_endpoint():
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
        if not name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Project name is required",
            )
        if not description:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Project description is required",
            )
        project = create_project(name, description, current_user.id, current_user.organization_id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Project created successfully",
            project=project.to_dict(),
        )

    except IntegrityError as e:
        print(e, "error@account/create-project")
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="Project name already exists",
        )

    except Exception as e:
        print(e, "error@account/create-project")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get projects endpoint
@account.route(f"/{ACCOUNT_PREFIX}/get-projects", methods=["GET"])
@jwt_required()
@email_verified_required
def get_projects_endpoint():
    try:
        project_id = request.args.get("project_id")
        if project_id:
            project = get_one_project(project_id, current_user.organization_id)
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Project fetched successfully",
                project=project.to_dict(),
            )

        projects = get_projects(current_user.organization_id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Projects fetched successfully",
            projects=[project.to_dict() for project in projects],
        )

    except Exception as e:
        print(e, "error@account/get-projects")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get users to be assigned to a project
@account.route(f"/{ACCOUNT_PREFIX}/get-users/<project_id>", methods=["GET"])
@jwt_required()
@email_verified_required
def get_users_endpoint(project_id):
    try:
        all_users = get_all_users()
        users = get_user_ids_by_project_id(project_id)
        not_assigned_users = [user for user in all_users if user.id not in users]
        not_assigned_users_list = list(map(return_user_dict, not_assigned_users))
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Users fetched successfully",
            users=not_assigned_users_list,
        )

    except Exception as e:
        print(e, "error@account/get-users")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# create task
@account.route(f"/{ACCOUNT_PREFIX}/create-task", methods=["POST"])
@jwt_required()
@email_verified_required
def create_task_endpoint():
    try:
        # title, description, status, project_id, assignee_id, due_date
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        status = data.get("status", "To Do")
        project_id = data.get("project_id")
        assignee_id = data.get("assignee_id")
        due_date = data.get("due_date")
        task = create_task(
            title, description, status, project_id, assignee_id, due_date
        )
        if not task:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Task not created",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Task created successfully",
            task=task,
        )

    except Exception as e:
        print(e, "error@account/create-task")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )

# get tasks for a project


@account.route(f"/{ACCOUNT_PREFIX}/get-tasks/<project_id>", methods=["GET"])
@jwt_required()
@email_verified_required
def get_tasks_endpoint(project_id):
    try:
        tasks = get_task_for_project(project_id)
        if not tasks:
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Tasks fetched successfully",
                tasks=[],
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Tasks fetched successfully",
            tasks=[task.to_dict() for task in tasks],
        )

    except Exception as e:
        print(e, "error@account/get-tasks")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
