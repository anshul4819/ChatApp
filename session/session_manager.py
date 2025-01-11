class SessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls.online_user_session_id_map = {}
            cls.connected_clients = {}  # Tracking connected clients
        return cls._instance

    def add_session(self, user, sid):
        if user.name not in self.online_user_session_id_map:
            self.online_user_session_id_map[user.name] = []
        self.online_user_session_id_map[user.name].append(sid)
        if user.name not in self.connected_clients:
            self.connected_clients[user.name] = []
        self.connected_clients[user.name].append(sid)

    def remove_session(self, sid):
        for name, sids in self.connected_clients.items():
            if sid in sids:
                sids.remove(sid)
                if not sids:
                    del self.connected_clients[name]
                return name
        return None
