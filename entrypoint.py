from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from messaging.messenger import Messenger
from db.database import Database
from session.session_manager import SessionManager
from models.user import User
from models.message import Message
from datetime import datetime

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)
db = Database.get_instance()
session_manager = SessionManager()
messenger = Messenger(db, session_manager, socketio)

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.json
    current_timestamp = datetime.now().isoformat()
    if 'sender' not in data or 'receiver' not in data or 'content' not in data:
        return jsonify({'error': 'Missing sender or content or receiver'}), 400
    msg = Message(data['sender'], data['receiver'], data['content'], current_timestamp)
    messenger.send_message(msg)
    return jsonify({'status': 'success'}), 201

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')

@socketio.on('join')
def handle_join(currUser):
    user = User(0, currUser, None)
    session_manager.add_session(user, request.sid)
    print(f'{currUser} has connected with session id {request.sid}')

    # Fetch and emit all messages for this receiver
    messages = db.get_messages_for_receiver(currUser)
    socketio.emit('all_messages', messages, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    disconnected_user = session_manager.remove_session(request.sid)
    if disconnected_user:
        print(f'{disconnected_user} has disconnected')

if __name__ == '__main__':
    socketio.run(app, port=3000, allow_unsafe_werkzeug=True)
