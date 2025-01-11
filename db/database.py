import sqlite3

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect('messages.db', check_same_thread=False)
            cls.init_db()
        return cls._instance

    @staticmethod
    def init_db():
        conn = Database.get_instance().connection
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                receiver TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    def write_message(self, message):
        conn = self.connection
        conn.execute('INSERT INTO messages (sender, receiver, content, timestamp) VALUES (?, ?, ?, ?)',
                     (message.sender, message.receiver, message.content, message.timestamp))
        conn.commit()
    def get_messages_for_receiver(self, currUser):
        conn = self.connection
        cursor = conn.execute('''
            SELECT sender, receiver, content, timestamp 
            FROM messages 
            WHERE receiver = ? OR sender = ?
            ORDER BY timestamp
        ''', (currUser, currUser))
        
        messages = {}
        for row in cursor.fetchall():
            sender = row[0]
            receiver = row[1]
            content = row[2]
            timestamp = row[3]
            
            other_party = sender if sender != currUser else receiver
            if other_party not in messages:
                messages[other_party] = []
            
            msg = {'sender': sender, 'content': content, 'timestamp': timestamp}
            messages[other_party].append(msg)
        
        return messages
    
    @classmethod
    def get_instance(cls):
        return cls.__new__(cls)
