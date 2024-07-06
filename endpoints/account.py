from flask import Blueprint, request
from utils import return_response
from http_status import HttpStatus
from status_res import StatusRes
from flask_jwt_extended import current_user, jwt_required
from models import current_user_info
from decorators import email_verified_required


account = Blueprint('account', __name__)

ACCOUNT_PREFIX = 'account'


@account.route(f'/{ACCOUNT_PREFIX}/dashboard', methods=['GET'])
@jwt_required()
@email_verified_required
def dashboard():
    return return_response(HttpStatus.OK, status=StatusRes.SUCCESS,
                           message="User Dashboard", user_info=current_user_info(current_user))
