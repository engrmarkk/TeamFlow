from flask_jwt_extended import current_user, jwt_required
from models import create_message, is_project_valid

# @app.route('/send-message', methods=['POST'])
# @jwt_required()
# def send_message():
#     data = request.json
#     project_id = data.get('project_id')
#     print(project_id, "project_id")
#
#     if not is_project_valid(project_id):
#         print("Invalid project ID")
#         return jsonify({
#             'status': HttpStatus.BAD_REQUEST,
#             'status_res': StatusRes.FAILED,
#             'message': "Invalid project ID"
#         }), 400
#
#     try:
#         content = data.get('content', None)
#         author_id = current_user.id
#
#         if not content:
#             return jsonify({
#                 'status': HttpStatus.BAD_REQUEST,
#                 'status_res': StatusRes.FAILED,
#                 'message': "Content is required"
#             }), 400
#
#         # Save the message to the database
#         msg = create_message(content, author_id, project_id)
#         if not msg:
#             raise Exception("Network Error")
#
#         # Trigger the message to the Pusher channel (room)
#         pusher_client.trigger(project_id, 'receive-message', msg.to_dict())
#         return jsonify({'status': 'success', 'message': 'Message sent'}), 200
#
#     except Exception as e:
#         # General error handling
#         print(e, "error@send-message")
#         return jsonify({
#             'status': HttpStatus.INTERNAL_SERVER_ERROR,
#             'status_res': StatusRes.FAILED,
#             'message': "Network Error"
#         }), 500

# @app.route('/join-room', methods=['POST'])
# @jwt_required()
# def join_room():
#     data = request.json
#     project_id = data.get('project_id')
#     print(current_user.id, "current_user.id")
#
#     if not is_project_valid(project_id):
#         print("Invalid project ID")
#         return jsonify({
#             'status': HttpStatus.BAD_REQUEST,
#             'status_res': StatusRes.FAILED,
#             'message': "Invalid project ID"
#         }), 400
#
#     # You can handle any additional logic for joining the room here
#     return jsonify({'status': 'success', 'message': 'Joined room'}), 200
