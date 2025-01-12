class SessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SessionManager, cls).__new__(cls)
            cls._connected_clients = {}  # Tracking connected clients
        return cls._instance

    def add_session(self, user, sid):
        if user.name not in self._connected_clients:
            self._connected_clients[user.name] = []
        self._connected_clients[user.name].append(sid)

    def remove_session(self, sid):
        for name, sids in self._connected_clients.items():
            if sid in sids:
                sids.remove(sid)
                if not sids:
                    del self._connected_clients[name]
                return name
        return None
    def get_sessions(self, user):
        return self._connected_clients.get(user.name, [])
