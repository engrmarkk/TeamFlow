from flask import Blueprint, request
from utils import return_response, return_user_dict
from http_status import HttpStatus
from status_res import StatusRes
from flask_jwt_extended import current_user, jwt_required
from utils import is_valid_email
from sqlalchemy.exc import IntegrityError
from pusher_conn import pusher_client
from models import (
    current_user_info,
    is_project_valid,
    create_message,
    create_project,
    create_document,
    change_password,
    get_all_users,
    get_users_by_organization,
    create_task,
    create_user,
    update_user_role,
    get_one_task,
    get_messages,
    email_exist,
    username_exist, get_user_task,
    create_otp,
    get_users_tasks_for_project,
    get_task,
    statistics,
    get_tasks_for_user,
    update_task,
    update_project,
    get_one_project,
    get_projects,
    get_task_for_project,
    get_user_by_id,
    task_assigned_to_user,
)
from decorators import email_verified_required, super_admin_required
from datetime import datetime
from flask_socketio import emit, join_room
import traceback

account = Blueprint("account", __name__)

ACCOUNT_PREFIX = "account"


@account.route(f"/{ACCOUNT_PREFIX}/dashboard", methods=["GET"])
@jwt_required()
@email_verified_required
def dashboard():
    try:
        """
        Get the user dashboard
        - Get the user information
        - Get the user role
        - Get the tasks assigned to the user
        - Get the statistics of the user tasks (the total tasks, completed tasks, not started tasks, in progress tasks, expired tasks)
        """
        (
            total_tasks,
            completed_tasks,
            not_started_tasks,
            in_progress_tasks,
            expired_tasks,
        ) = statistics(current_user.id)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="User Dashboard",
            user_info=current_user_info(current_user),
            role=(
                "super_admin"
                if current_user.is_super_admin
                else "admin" if current_user.is_admin else "user"
            ),
            tasks=task_assigned_to_user(current_user.id),
            statistics={
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "not_started_tasks": not_started_tasks,
                "in_progress_tasks": in_progress_tasks,
                "expired_tasks": expired_tasks,
            },
        )
    except Exception as e:
        print(e, "error@account/dashboard")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get staffs/users
@account.route(f"/{ACCOUNT_PREFIX}/users", methods=["GET"])
@jwt_required()
@email_verified_required
# super admin required
@super_admin_required
def get_all_users_endpoint():
    try:
        # this is actually a super admin required endpoint
        # only super admin can view all users in the organization
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        users, total_items, total_pages = get_users_by_organization(
            current_user.organization_id, page, per_page
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="All Users",
            users=[return_user_dict(user) for user in users],
            organization=current_user.organization.name.title(),
            total_items=total_items,
            total_pages=total_pages,
            page=page,
            per_page=per_page,
        )
    except Exception as e:
        print(e, "error@account/users")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


@account.route(f"/{ACCOUNT_PREFIX}/create-user", methods=["POST"])
@jwt_required()
@email_verified_required
# super admin required
@super_admin_required
def create_user_endpoint():
    try:
        """
        Create a new user
        Only super admin has the permission to create a new user
        """
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
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid Email Format",
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
        user = create_user(
            first_name,
            last_name,
            username,
            email,
            password,
            current_user.organization_id,
            is_admin=is_admin,
            is_super_admin=is_super_admin,
        )

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


# get user details
@account.route(f"/{ACCOUNT_PREFIX}/user-details", methods=["GET"])
@jwt_required()
@email_verified_required
def get_user_details_endpoint():
    return return_response(
        HttpStatus.OK,
        status=StatusRes.SUCCESS,
        message="User Details",
        user=current_user.to_dict(),
    )


# update user role
@account.route(f"/{ACCOUNT_PREFIX}/update-user-role", methods=["POST"])
@jwt_required()
@email_verified_required
@super_admin_required
def update_user_role_endpoint():
    try:
        # only super admin can update user role to either admin or super admin or neither
        data = request.get_json()
        user_id = data.get("user_id")
        is_admin = data.get("is_admin", False)
        is_super_admin = data.get("is_super_admin", False)
        if not user_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User id is required",
            )
        if not isinstance(is_admin, bool) or not isinstance(is_super_admin, bool):
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="is_admin and is_super_admin must be boolean",
            )
        user = update_user_role(user_id, is_admin, is_super_admin)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="User role updated successfully",
            user=user.to_dict(),
        )

    except IntegrityError as e:
        print(e, "error@account/update-user-role")
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="User does not exist",
        )

    except Exception as e:
        print(e, "error@account/update-user-role")
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
        project = create_project(
            name, description, current_user.id, current_user.organization_id
        )
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


# update project
@account.route(f"/{ACCOUNT_PREFIX}/update-project/<project_id>", methods=["PATCH"])
@jwt_required()
@email_verified_required
def update_project_endpoint(project_id):
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")

        proj = update_project(
            project_id, name, description, current_user.organization_id
        )

        if not proj:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Project not found",
            )

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Project updated successfully",
            project=proj.to_dict(),
        )

    except Exception as e:
        print(e, "error@account/update-project")
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
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        project_id = request.args.get("project_id")
        if project_id:
            project = get_one_project(project_id, current_user.organization_id)
            if not project:
                return return_response(
                    HttpStatus.NOT_FOUND,
                    status=StatusRes.FAILED,
                    message="Project not found",
                )
            return return_response(
                HttpStatus.OK,
                status=StatusRes.SUCCESS,
                message="Project fetched successfully",
                project=project.to_dict(),
            )

        projects, total_items, total_pages = get_projects(
            current_user.organization_id, page, per_page
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Projects fetched successfully",
            projects=[project.to_dict() for project in projects.items],
            page=page,
            per_page=per_page,
            total_pages=total_pages,
            total_items=total_items,
        )

    except Exception as e:
        print(e, "error@account/get-projects")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get users to be assigned to a project
@account.route(f"/{ACCOUNT_PREFIX}/get-users", methods=["GET"])
@jwt_required()
@email_verified_required
def get_users_endpoint():
    try:
        all_users = get_all_users(current_user.organization_id)
        not_assigned_users_list = list(map(return_user_dict, all_users))
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
        from celery_config.utils.cel_workers import send_mail

        # title, description, status, project_id, assignee_id, due_date
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        status = data.get("status", "To Do")
        project_id = data.get("project_id")
        assignee_id = data.get("assignee_id")
        due_date = data.get("due_date")

        if not title:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Title is required",
            )
        if not project_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Project id is required",
            )
        if not assignee_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Who are you assigning this task to?",
            )
        if not due_date:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="When is this task due?",
            )
        # convert due date to datetime
        try:
            due_date = datetime.strptime(due_date, "%d-%m-%Y")
        except ValueError as e:
            print(e, "error@account/create-task")
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid due date format,  should be dd-mm-yyyy",
            )
        task = create_task(
            title, description, status, project_id, assignee_id, due_date
        )
        if not task:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Task not created",
            )
        user = get_user_by_id(assignee_id)
        project = get_one_project(project_id, current_user.organization_id)
        payload = {
            "email": user.email,
            "subject": "Task Created",
            "template_name": "assigned_project.html",
            "name": f"{user.last_name.title()} {user.first_name.title()}",
            "project_name": project.name.title(),
            "task": task.title.title(),
            "due_date": due_date.strftime("%d-%b-%Y"),
            "date": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
        }
        print("Calling celery")
        send_mail.delay(payload)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Task created successfully",
            task=task.to_dict(),
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
        status = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
        tasks = get_task_for_project(
            project_id, status, start_date, end_date, page, per_page
        )

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Tasks fetched successfully",
            tasks=[task.to_dict2() for task in tasks.items],
            page=page,
            per_page=per_page,
            total_pages=tasks.pages,
            total_items=tasks.total,
        )
    except IntegrityError as e:
        print(e, "error@account/get-tasks")
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="Invalid project id",
        )

    except Exception as e:
        print(e, "error@account/get-tasks")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get tasks for a user
@account.route(f"/{ACCOUNT_PREFIX}/get-user-tasks", methods=["GET"])
@jwt_required()
@email_verified_required
def get_user_tasks_endpoint():
    try:
        status = request.args.get("status")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))

        if start_date:
            start_date = datetime.strptime(start_date, "%d-%m-%Y")
        if end_date:
            end_date = datetime.strptime(end_date, "%d-%m-%Y")

        tasks = get_tasks_for_user(
            current_user.id, status, start_date, end_date, page, per_page
        )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Tasks fetched successfully",
            tasks=[task.user_task_dict() for task in tasks.items],
            page=page,
            per_page=per_page,
            total_pages=tasks.pages,
            total_items=tasks.total,
        )

    except ValueError as e:
        print(traceback.format_exc())
        print(e, "error@account/get-user-tasks")
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="Invalid date format, should be dd-mm-yyyy",
        )

    except Exception as e:
        print(traceback.format_exc())
        print(e, "error@account/get-user-tasks")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get all task for a user
@account.route(f"/{ACCOUNT_PREFIX}/get-task/<user_id>", methods=["GET"])
@jwt_required()
@email_verified_required
@super_admin_required
def get_task_endpoint(user_id):
    try:
        tasks = get_user_task(user_id, current_user)
        if tasks is None:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="User not found",
            )
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Tasks fetched successfully",
            tasks=[task.user_task_dict() for task in tasks],
        )

    except Exception as e:
        print(e, "error@account/get-task")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# update task
@account.route(f"/{ACCOUNT_PREFIX}/update-task/<task_id>", methods=["PATCH"])
@jwt_required()
@email_verified_required
def update_task_endpoint(task_id):
    try:
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        status = data.get("status")
        project_id = data.get("project_id")
        assignee_id = data.get("assignee_id")
        due_date = data.get("due_date")

        if due_date:
            try:
                due_date = datetime.strptime(due_date, "%d-%m-%Y")
            except ValueError as e:
                print(e, "error@account/update-task")
                return return_response(
                    HttpStatus.BAD_REQUEST,
                    status=StatusRes.FAILED,
                    message="Invalid due date format,  should be dd-mm-yyyy",
                )

        if status and status not in ["In Progress", "Completed"]:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Invalid status",
            )

        task = update_task(
            task_id, title, description, status, project_id, assignee_id, due_date
        )

        if not task:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="There was a problem updating the task",
            )

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Task updated successfully",
            task=task.to_dict(),
        )

    except Exception as e:
        print(e, "error@account/update-task")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# delete task
@account.route(f"/{ACCOUNT_PREFIX}/delete-task/<task_id>", methods=["DELETE"])
@jwt_required()
@email_verified_required
def delete_task_endpoint(task_id):
    try:
        task = get_one_task(task_id, current_user.organization_id)
        if not task:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Task not found",
            )
        task.delete()
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Task deleted successfully",
        )
    except Exception as e:
        print(e, "error@account/delete-task")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# delete project
@account.route(f"/{ACCOUNT_PREFIX}/delete-project/<project_id>", methods=["DELETE"])
@jwt_required()
@email_verified_required
def delete_project_endpoint(project_id):
    try:
        project = get_one_project(project_id, current_user.organization_id)
        if not project:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Project not found",
            )
        project.delete()
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Project deleted successfully",
        )
    except Exception as e:
        print(e, "error@account/delete-project")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# upload documents
@account.route(f"/{ACCOUNT_PREFIX}/upload-documents/<project_id>", methods=["POST"])
@jwt_required()
@email_verified_required
def upload_documents_endpoint(project_id):
    try:
        from celery_config.utils.cel_workers import send_all_users_email

        data = request.get_json()

        # This details will be gotten from the front end after calling the
        # upload cloudinary endpoint to get the details
        document_name = data.get("document_name")
        document_url = data.get("document_url")
        public_id = data.get("public_id")
        if not document_name:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Document Name are required",
            )
        if not document_url:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Document URL are required",
            )

        if not public_id:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Cloudinary Public ID is required",
            )

        project = get_one_project(project_id, current_user.organization_id)
        if not project:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Project not found",
            )
        create_document(
            document_name, document_url, project_id, current_user.id, public_id
        )
        users = get_users_tasks_for_project(project_id)

        print(users, "users")

        # celery send mail
        uploaded_by = (
            f"{current_user.last_name.title()} {current_user.first_name.title()}"
        )
        send_all_users_email.delay(users, uploaded_by, document_name, project.name)
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Document uploaded successfully",
        )

    except Exception as e:
        print(e, "error@account/upload-documents")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# change password
@account.route(f"/{ACCOUNT_PREFIX}/change-password", methods=["POST"])
@jwt_required()
@email_verified_required
def change_password_endpoint():
    try:
        data = request.get_json()
        old_password = data.get("old_password")
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        if not old_password:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Old password is required",
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
                message="Password and confirm password does not match",
            )

        res = change_password(current_user, old_password, new_password)
        if not res:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Old password is incorrect",
            )

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Password changed successfully",
        )

    except Exception as e:
        print(e, "error@account/change-password")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# get messages
@account.route(f"/{ACCOUNT_PREFIX}/get-messages/<project_id>", methods=["GET"])
@jwt_required()
@email_verified_required
def get_all_messages(project_id):
    try:
        messages = get_messages(project_id, current_user.organization_id)

        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Messages Fetched Successfully",
            data=[msg.to_dict(current_user.id) for msg in messages],
        )

    except Exception as e:
        print(e, "error@account/get_all_messages")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )


# This is for pusher
@account.route(f"/{ACCOUNT_PREFIX}/send-message", methods=["POST"])
@jwt_required()
def send_message():
    data = request.json
    project_id = data.get("project_id")
    print(project_id, "project_id")

    if not project_id:
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="Project ID is required",
        )

    if not is_project_valid(project_id):
        print("Invalid project ID")
        return return_response(
            HttpStatus.BAD_REQUEST,
            status=StatusRes.FAILED,
            message="Invalid project ID",
        )

    try:
        content = data.get("content", None)
        author_id = current_user.id

        if not content:
            return return_response(
                HttpStatus.BAD_REQUEST,
                status=StatusRes.FAILED,
                message="Content is required",
            )

        # Save the message to the database
        msg = create_message(content, author_id, project_id)
        if not msg:
            raise Exception("Network Error")

        # Trigger the message to the Pusher channel (room)
        pusher_client.trigger(project_id, "receive-message", msg.to_dict())
        return return_response(
            HttpStatus.OK,
            status=StatusRes.SUCCESS,
            message="Message sent",
        )

    except Exception as e:
        print(e, "error@send-message")
        return return_response(
            HttpStatus.INTERNAL_SERVER_ERROR,
            status=StatusRes.FAILED,
            message="Network Error",
        )
