import logging

logger = logging.getLogger(__name__)

class Messenger:
    def __init__(self, db, session_manager, socketio):
        self.db = db
        self.session_manager = session_manager
        self.socketio = socketio
        logger.info("Messenger initialized")

    def send_message(self, message):
        self.db.write_message(message)
        self.broadcast(message)
        logger.info(f"Message sent: {message}")

    def broadcast(self, message):
        session_ids = self.session_manager.get_sessions(message.receiver)
        for sid in session_ids:
            self.socketio.emit('new_message', {'sender': message.sender, 'content': message.content, 'timestamp': message.timestamp}, room=sid)
        logger.info(f"Message broadcasted to sessions: {session_ids}")