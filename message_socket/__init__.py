from flask_socketio import emit, join_room
from flask import request
from models import create_message, is_project_valid
from http_status import HttpStatus
from status_res import StatusRes
from extensions import socketio
from flask_jwt_extended import decode_token
from jwt import ExpiredSignatureError, InvalidTokenError


# decode token
def decode_bearer_token(token):
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token.get("sub")
        return user_id
    except ExpiredSignatureError:
        print("Token has expired")
        return None
    except InvalidTokenError:
        print("Invalid token")
        return None


@socketio.on("connect")
def test_connect_handler():
    print("Client connected")


@socketio.on("join-room")
def on_join(data):
    token = request.args.get("token")
    print("token", token)
    if not token:
        emit(
            "error-message",
            {
                "status": HttpStatus.UNAUTHORIZED,
                "status_res": StatusRes.FAILED,
                "message": "Unauthorized",
            },
        )
        return

    user_id = decode_bearer_token(token)
    print(user_id, "USER ID")
    if not user_id:
        print("Unauthorized, No user id")
        emit(
            "error-message",
            {
                "status": HttpStatus.UNAUTHORIZED,
                "status_res": StatusRes.FAILED,
                "message": "Unauthorized",
            },
        )
    project_id = data.get("project_id")
    print(user_id, "current_user.id")
    if not is_project_valid(project_id):
        print("Invalid project ID")
        emit(
            "error-message",
            {
                "status": HttpStatus.BAD_REQUEST,
                "status_res": StatusRes.FAILED,
                "message": "Invalid project ID",
            },
        )
        return
    join_room(project_id)


# error handler
@socketio.on_error()
def error_handler(e):
    print(e, "error@socketio.on_error")
    emit(
        "error-message",
        {
            "status": HttpStatus.INTERNAL_SERVER_ERROR,
            "status_res": StatusRes.FAILED,
            "message": str(e),
        },
    )


@socketio.on("send-message")
def send_message(data):
    token = request.args.get("token")
    print("token", token)
    if not token:
        emit(
            "error-message",
            {
                "status": HttpStatus.UNAUTHORIZED,
                "status_res": StatusRes.FAILED,
                "message": "Unauthorized",
            },
        )
        return

    user_id = decode_bearer_token(token)
    print(user_id, "USER ID")
    if not user_id:
        print("Unauthorized, No user id")
        emit(
            "error-message",
            {
                "status": HttpStatus.UNAUTHORIZED,
                "status_res": StatusRes.FAILED,
                "message": "Unauthorized",
            },
        )
        return
    project_id = data.get("project_id")
    print(project_id, "project_id")

    if not is_project_valid(project_id):
        print("Invalid project ID")
        emit(
            "error-message",
            {
                "status": HttpStatus.BAD_REQUEST,
                "status_res": StatusRes.FAILED,
                "message": "Invalid project ID",
            },
        )  # Send error to the requesting client only
        return

    try:
        content = data.get("content", None)
        author_id = user_id

        if not content:
            emit(
                "error-message",
                {
                    "status": HttpStatus.BAD_REQUEST,
                    "status_res": StatusRes.FAILED,
                    "message": "Content is required",
                },
            )
            return

        # Assuming create_message is a function that saves the message to the database
        msg = create_message(content, author_id, project_id)
        if not msg:
            raise Exception("Network Error")

        emit("receive-message", msg.to_dict(), room=project_id)
    except Exception as e:
        # General error handling
        print(e, "error@message_socket/send-message")
        emit(
            "error",
            {
                "status": HttpStatus.INTERNAL_SERVER_ERROR,
                "status_res": StatusRes.FAILED,
                "message": "Network Error",
            },
            room=project_id,
        )
