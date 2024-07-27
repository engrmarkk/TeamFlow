from flask_socketio import join_room, emit
from extensions import socketio
from models import create_message, is_project_valid
from http_status import HttpStatus
from status_res import StatusRes
from flask_jwt_extended import current_user


@socketio.on('send-message')
def send_message(data):
    # Extract project_id outside try-except block to ensure accessibility
    project_id = data.get('project_id')
    print(project_id, "project_id")
    print(current_user.id, "current_user_id")

    # Validate project_id immediately
    if not is_project_valid(project_id):
        print("Invalid project ID")
        emit('error', {
            'status': HttpStatus.BAD_REQUEST,
            'status_res': StatusRes.FAILED,
            'message': "Invalid project ID"
        }, room=project_id)
        return

    join_room(project_id)

    try:
        content = data.get('content')
        author_id = data.get('author_id')

        if not content:
            raise ValueError("Content is required")

        if not author_id:
            raise ValueError("Author id is required")

        # Assuming create_message is a function that saves the message to the database
        msg = create_message(content, author_id, project_id)
        if not msg:
            raise Exception("Network Error")

        emit('receive-message', msg.to_dict(), room=project_id)

    except ValueError as ve:
        # Handle validation errors specifically
        print(ve, "error@message_socket/send-message")
        emit('error', {
            'status': HttpStatus.BAD_REQUEST,
            'status_res': StatusRes.FAILED,
            'message': "Invalid request"
        }, room=project_id)
    except Exception as e:
        # General error handling
        print(e, "error@message_socket/send-message")
        emit('error', {
            'status': HttpStatus.INTERNAL_SERVER_ERROR,
            'status_res': StatusRes.FAILED,
            'message': "Network Error"
        }, room=project_id)
