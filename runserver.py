from app_config import create_app
from dotenv import load_dotenv
from message_socket import socketio
import redis


load_dotenv()


app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=7000)
