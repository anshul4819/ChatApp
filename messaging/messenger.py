class Messenger:
    def __init__(self, db, session_manager, socketio):
        self.db = db
        self.session_manager = session_manager
        self.socketio = socketio

    def send_message(self, message):
        self.db.write_message(message)
        self.broadcast(message)

    def broadcast(self, message):
        session_ids = self.session_manager.get_sessions(message.receiver)
        for sid in session_ids:
            self.socketio.emit('new_message', {'sender': message.sender, 'content': message.content, 'timestamp': message.timestamp}, room=sid)
