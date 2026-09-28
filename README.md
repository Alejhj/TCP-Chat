# Python Multi-Client Chat Application

A multithreaded client-server chat application built with Python and TCP sockets. The application allows multiple users to connect to a server and communicate in real time using broadcast and private messages.

## Features

- Multiple concurrent client connections
- Unique user login
- Broadcast messages to all connected users
- Private messaging between users
- View currently connected users
- Join and leave notifications
- Multithreaded server architecture
- Thread-safe client management using locks
- Separate control and data socket connections
- Simple `200` and `500` status-code response system

## Technologies Used

- Python
- TCP/IP Socket Programming
- Multithreading
- Thread Synchronization
- Client-Server Architecture

## Project Structure

```text
.
├── client.py
└── server.py
```

## Requirements

- Python 3.x
- No external libraries required

The project only uses Python standard-library modules such as:

```python
socket
threading
sys
```

## Running the Project

### 1. Start the Server

Run the server and provide the port number you want it to listen on:

```bash
python server.py 5050
```

Example output:

```text
Starting server…
Creating server socket
Awaiting connections…
```

### 2. Start a Client

Open another terminal and run:

```bash
python client.py
```

The client will display:

```text
Starting client…
>
```

### 3. Connect to the Server

Use the `connect` command followed by the server IP address and port:

```text
connect 127.0.0.1 5050
```

For clients running on another computer, replace `127.0.0.1` with the IP address of the machine running the server.

## Commands

### Login

Choose a username:

```text
login username
```

Example:

```text
login Jake
```

Usernames must be unique.

### View Connected Users

```text
who
```

This displays the users currently connected to the server.

### Broadcast Message

Send a message to every connected user:

```text
broadcast message
```

Example:

```text
broadcast Hello everyone!
```

### Private Message

Send a message to a specific user:

```text
private username message
```

Example:

```text
private Alex Hey, how are you?
```

### Quit

Disconnect from the server:

```text
quit
```

Other connected users will receive a notification when a user leaves.

## How It Works

The application uses a client-server architecture based on TCP sockets.

The server listens for incoming client connections and creates a separate thread for each connected client. This allows multiple users to communicate with the server concurrently.

After the initial connection, the server creates a separate data socket for the client. The application therefore separates command communication from incoming message delivery.

The server keeps track of connected clients and their usernames while using a thread lock to safely manage shared data between multiple client threads.

The client also runs a separate receiving thread so incoming broadcasts, private messages, and user notifications can be processed while the user continues entering commands.

## Status Codes

The application uses a simple response system:

```text
200
```

Indicates that a request was completed successfully.

```text
500
```

Indicates that the request failed or was invalid.

## Example Session

### Client 1

```text
> connect 127.0.0.1 5050
200 status code received. Starting data connection

> login Jake
200 status code received. Login successful

> broadcast Hello everyone!
200 status code received.
Broadcast message from Jake: Hello everyone!
```

### Client 2

```text
> connect 127.0.0.1 5050

> login Alex
200 status code received. Login successful

> who
200 status code received. Users currently connected: Jake, Alex

> private Jake Hey Jake!
200 status code received. Message sent.
```

Client 1 receives:

```text
Alex: Hey Jake!
```

## Concepts Demonstrated

This project demonstrates several networking and concurrent-programming concepts, including:

- TCP socket creation and communication
- Client-server networking
- Concurrent connection handling
- Python threads
- Synchronization with locks and events
- Message parsing
- Command-response protocols
- Broadcast communication
- Point-to-point messaging

## Future Improvements

Possible improvements include:

- Graphical user interface
- Message encryption
- User authentication
- Persistent chat history
- Chat rooms or channels
- File transfer
- Improved error handling
- Server-side logging
- Configurable host and port settings

## Author

Created as a Python networking and socket programming project.
