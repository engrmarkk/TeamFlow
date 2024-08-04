from flask_socketio import emit, join_room
from models import create_message, is_project_valid
from http_status import HttpStatus
from status_res import StatusRes
from extensions import socketio
from flask_jwt_extended import current_user, jwt_required


@socketio.on('connect')
def test_connect_handler():
    print('Client connected')


@socketio.on('join-room')
@jwt_required()
def on_join(data):
    project_id = data.get('project_id')
    print(current_user.id, "current_user.id")
    if not is_project_valid(project_id):
        print("Invalid project ID")
        emit('error-message', {
            'status': HttpStatus.BAD_REQUEST,
            'status_res': StatusRes.FAILED,
            'message': "Invalid project ID"
        })
        return
    join_room(project_id)


# error handler
@socketio.on_error()
def error_handler(e):
    print(e, "error@socketio.on_error")
    emit('error-message', {
        'status': HttpStatus.INTERNAL_SERVER_ERROR,
        'status_res': StatusRes.FAILED,
        'message': str(e)
    })


@socketio.on('send-message')
@jwt_required()
def send_message(data):
    project_id = data.get('project_id')
    print(project_id, "project_id")

    if not is_project_valid(project_id):
        print("Invalid project ID")
        emit('error-message', {
            'status': HttpStatus.BAD_REQUEST,
            'status_res': StatusRes.FAILED,
            'message': "Invalid project ID"
        })  # Send error to the requesting client only
        return

    try:
        content = data.get('content', None)
        author_id = current_user.id

        if not content:
            emit('error-message', {
                'status': HttpStatus.BAD_REQUEST,
                'status_res': StatusRes.FAILED,
                'message': "Content is required"
            })
            return

        # Assuming create_message is a function that saves the message to the database
        msg = create_message(content, author_id, project_id)
        if not msg:
            raise Exception("Network Error")

        emit('receive-message', msg.to_dict(), room=project_id)
    except Exception as e:
        # General error handling
        print(e, "error@message_socket/send-message")
        emit('error', {
            'status': HttpStatus.INTERNAL_SERVER_ERROR,
            'status_res': StatusRes.FAILED,
            'message': "Network Error"
        }, room=project_id)
