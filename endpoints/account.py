from flask import Blueprint, request
from utils import return_response, return_user_dict
from http_status import HttpStatus
from status_res import StatusRes
from flask_jwt_extended import current_user, jwt_required
from models import (current_user_info,
                    create_project,
                    get_user_ids_by_project_id,
                    get_all_users, create_task, get_task, get_task_for_project)
from decorators import email_verified_required


account = Blueprint('account', __name__)

ACCOUNT_PREFIX = 'account'


@account.route(f'/{ACCOUNT_PREFIX}/dashboard', methods=['GET'])
@jwt_required()
@email_verified_required
def dashboard():
    return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                           message="User Dashboard", user_info=current_user_info(current_user))


# create project endpoint
@account.route(f'/{ACCOUNT_PREFIX}/create-project', methods=['POST'])
@jwt_required()
@email_verified_required
def create_project_endpoint():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        if not name:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Project name is required")
        if not description:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Project description is required")
        project = create_project(name, description, current_user.id)
        return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                               message="Project created successfully", project=project)

    except Exception as e:
        print(e, "error@account/create-project")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error")


# get users to be assigned to a project
@account.route(f'/{ACCOUNT_PREFIX}/get-users/<project_id>', methods=['GET'])
@jwt_required()
@email_verified_required
def get_users_endpoint(project_id):
    try:
        all_users = get_all_users()
        users = get_user_ids_by_project_id(project_id)
        if not users:
            return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                                   message="Users fetched successfully", users=[])
        not_assigned_users = [user for user in all_users if user.id not in users]
        not_assigned_users_list = list(map(return_user_dict, not_assigned_users))
        return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                               message="Users fetched successfully", users=not_assigned_users_list)

    except Exception as e:
        print(e, "error@account/get-users")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error")


# create task
@account.route(f'/{ACCOUNT_PREFIX}/create-task', methods=['POST'])
@jwt_required()
@email_verified_required
def create_task_endpoint():
    try:
        # title, description, status, project_id, assignee_id, due_date
        data = request.get_json()
        title = data.get('title')
        description = data.get('description')
        status = data.get('status', "To Do")
        project_id = data.get('project_id')
        assignee_id = data.get('assignee_id')
        due_date = data.get('due_date')
        task = create_task(title, description, status, project_id, assignee_id, due_date)
        if not task:
            return return_response(HttpStatus.BAD_REQUEST, status=StatusRes.FAILED,
                                   message="Task not created")
        return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                               message="Task created successfully", task=task)

    except Exception as e:
        print(e, "error@account/create-task")
        return return_response(HttpStatus.INTERNAL_SERVER_ERROR,
                               status=StatusRes.FAILED, message="Network Error")
