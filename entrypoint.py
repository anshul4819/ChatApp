import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from messaging.messenger import Messenger
from db.database import Database
from session.session_manager import SessionManager
from models.user import User
from models.message import Message
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduce the log level for socket logs
logging.getLogger('engineio').setLevel(logging.WARNING)
logging.getLogger('socketio').setLevel(logging.WARNING)

class MessengerApp:
    def __init__(self):
        self.app = Flask(__name__)
        # This will enable CORS for all routes
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*", logger=True, engineio_logger=True)
        self.db = Database.get_instance()
        self.session_manager = SessionManager()
        self.messenger = Messenger(self.db, self.session_manager, self.socketio)
        self.setup_routes()
        self.setup_socketio_events()
        logger.info("MessengerApp initialized")

    def setup_routes(self):
        @self.app.route('/messages', methods=['POST'])
        def create_message():
            data = request.json
            current_timestamp = datetime.now().isoformat()
            if 'sender' not in data or 'receiver' not in data or 'content' not in data:
                return jsonify({'error': 'Missing sender or content or receiver'}), 400
            msg = Message(data['sender'], data['receiver'], data['content'], current_timestamp)
            self.messenger.send_message(msg)
            return jsonify({'status': 'success'}), 201

    def setup_socketio_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f'Client connected: {request.sid}')

        @self.socketio.on('join')
        def handle_join(currUser):
            user = User(0, currUser, None)
            self.session_manager.add_session(user, request.sid)
            logger.info(f'{currUser} has connected with session id {request.sid}')

            # Fetch and emit all messages for this receiver
            messages = self.db.get_messages_for_receiver(currUser)
            self.socketio.emit('all_messages', messages, room=request.sid)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            disconnected_user = self.session_manager.remove_session(request.sid)
            if disconnected_user:
                logger.info(f'{disconnected_user} has disconnected')

    def run(self):
        logger.info("Starting MessengerApp")
        self.socketio.run(self.app, port=3000, allow_unsafe_werkzeug=True)

messenger_app = MessengerApp()
app = messenger_app.app
if __name__ == '__main__':
    logging.info("Flask app name:", messenger_app.app.name)
    messenger_app.run()