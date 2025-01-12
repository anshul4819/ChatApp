
# Messenger App

## Overview

This Messenger App is a real-time messaging application built using Flask, Flask-SocketIO, and SQLite. It supports user sessions, message broadcasting, and real-time updates using WebSockets.

## What are WebSockets?

WebSockets are a protocol that provides full-duplex communication channels over a single TCP connection. Unlike HTTP, which is a request-response protocol, WebSockets allow for persistent connections where both the client and server can send messages to each other at any time.

## How are WebSockets Useful in This App?

In this app, WebSockets are used to enable real-time communication between the server and connected clients. This allows users to receive messages instantly without needing to refresh the page or make repeated HTTP requests. The Flask-SocketIO library is used to manage WebSocket connections and events.

## How Are Different User Sessions Getting Messages at the Same Time?

Different user sessions receive messages simultaneously through the [`broadcast`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2FUsers%2Fanshul.narwal%2FDesktop%2FScreenshots%2Fprojects%2FChatApp%2Fmessaging%2Fmessenger.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A10%2C%22character%22%3A8%7D%5D "messaging/messenger.py") method in the [`Messenger`](command:_github.copilot.openSymbolInFile?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fanshul.narwal%2FDesktop%2FScreenshots%2Fprojects%2FChatApp%2Fmessaging%2Fmessenger.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22Messenger%22%5D "/Users/anshul.narwal/Desktop/Screenshots/projects/ChatApp/messaging/messenger.py") class. When a message is sent, it is written to the database and then broadcasted to all active sessions of the receiver. The [`broadcast`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2FUsers%2Fanshul.narwal%2FDesktop%2FScreenshots%2Fprojects%2FChatApp%2Fmessaging%2Fmessenger.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A10%2C%22character%22%3A8%7D%5D "messaging/messenger.py") method retrieves the session IDs for the receiver from the [`SessionManager`](command:_github.copilot.openSymbolInFile?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fanshul.narwal%2FDesktop%2FScreenshots%2Fprojects%2FChatApp%2Fsession%2Fsession_manager.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22SessionManager%22%5D "/Users/anshul.narwal/Desktop/Screenshots/projects/ChatApp/session/session_manager.py") and emits the message to each session using SocketIO.

```py
def broadcast(self, message):
    session_ids = self.session_manager.get_sessions(message.receiver)
    for sid in session_ids:
        self.socketio.emit('new_message', {'sender': message.sender, 'content': message.content, 'timestamp': message.timestamp}, room=sid)
```

## How Is a User Connected and Disconnected?

### Connecting a User

When a user connects, the `handle_connect` event is triggered. The user then joins by sending a `join` event with their username. The server creates a new [`User`](models/user.py) object and adds the session to the [`SessionManager`](session/session_manager.py). The server also fetches and emits all previous messages for the user.

```py
@self.socketio.on('join')
def handle_join(currUser):
    user = User(0, currUser, None)
    self.session_manager.add_session(user, request.sid)
    messages = self.db.get_messages_for_receiver(currUser)
    self.socketio.emit('all_messages', messages, room=request.sid)
```

### Disconnecting a User

When a user disconnects, the [`handle_disconnect`](command:_github.copilot.openSymbolFromReferences?%5B%7B%22%24mid%22%3A1%2C%22path%22%3A%22%2FUsers%2Fanshul.narwal%2FDesktop%2FScreenshots%2Fprojects%2FChatApp%2Fentrypoint.py%22%2C%22scheme%22%3A%22file%22%7D%2C%7B%22line%22%3A48%2C%22character%22%3A12%7D%5D "entrypoint.py") event is triggered. The server removes the user's session from the [`SessionManager`](command:_github.copilot.openSymbolInFile?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fanshul.narwal%2FDesktop%2FScreenshots%2Fprojects%2FChatApp%2Fsession%2Fsession_manager.py%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%2C%22SessionManager%22%5D "/Users/anshul.narwal/Desktop/Screenshots/projects/ChatApp/session/session_manager.py") and logs the disconnection.

```py
@self.socketio.on('disconnect')
def handle_disconnect():
    disconnected_user = self.session_manager.remove_session(request.sid)
    if disconnected_user:
        print(f'{disconnected_user} has disconnected')
```

## How Are Messages Written to the Database?

Messages are written to the database using the `write_message` method in the [`Database`](db/database.py) class. When a message is created, it is passed to the `send_message` method of the [`Messenger`](messaging/messenger.py) class, which then calls `write_message` to insert the message into the `messages` table in the SQLite database.

```py
def write_message(self, message):
    conn = self.connection
    conn.execute('INSERT INTO messages (sender, receiver, content, timestamp) VALUES (?, ?, ?, ?)',
                 (message.sender, message.receiver, message.content, message.timestamp))
    conn.commit()
```

## Getting Started

To run the app, follow these steps:

1. Build the Docker image:
    ```sh
    docker build -t messenger .
    ```

2. Run the Docker container:
    ```sh
    docker run -p 3000:3000 messenger
    ```

The app will be available at `http://localhost:3000`.

## Dependencies

- Flask==3.1.0
- Flask-Cors==5.0.0
- Flask-SocketIO==5.5.1
- python-engineio==4.11.2
- python-socketio==5.12.1

These dependencies are listed in the [`requirements.txt`](command:_github.copilot.openRelativePath?%5B%7B%22scheme%22%3A%22file%22%2C%22authority%22%3A%22%22%2C%22path%22%3A%22%2FUsers%2Fanshul.narwal%2FDesktop%2FScreenshots%2Fprojects%2FChatApp%2Frequirements.txt%22%2C%22query%22%3A%22%22%2C%22fragment%22%3A%22%22%7D%5D "/Users/anshul.narwal/Desktop/Screenshots/projects/ChatApp/requirements.txt") file and will be installed when building the Docker image.
