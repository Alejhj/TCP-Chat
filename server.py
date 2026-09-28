import socket
import threading
import sys

HEADER = 64
CONTROL_PORT = int(sys.argv[1])

SERVER = "0.0.0.0"
ADDR = (SERVER, CONTROL_PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


print("Starting server…")
print("Creating server socket")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

server.listen()

clients = []
nicknames = []
clients_lock = threading.Lock()


def handle_client(conn, addr):

    data_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_server.bind((SERVER, 0))
    data_server.listen()
    DATA_PORT = data_server.getsockname()[1]
    conn.sendall(f"200\n\n{DATA_PORT}".encode(FORMAT))

    data_socket, data_addr = data_server.accept()

    connected = True
    while connected:
        try:
            message = conn.recv(1024).decode(FORMAT)

            if not message:
                break

            parts = message.split()
            if not parts:
                data_socket.sendall(f"500\n\n".encode(FORMAT))
                continue

            command = parts[0].lower()

            if command == "login":
                if len(parts) < 2:
                    data_socket.sendall(f"500\n\n".encode(FORMAT))
                    continue

                nickname = parts[1]

                with clients_lock:
                    if nickname in nicknames:
                        data_socket.sendall(f"500\n\n".encode(FORMAT))
                        continue

                    existing_clients = list(clients)
                    nicknames.append(nickname)
                    clients.append((conn, data_socket))

                print(f"Login requested by: {nickname}")
                data_socket.sendall(f"200\n\n".encode(FORMAT))

                for client in existing_clients:
                    client[1].sendall(f"200\n\njoin\n{nickname}".encode(FORMAT))

            elif command == "who":
                print("Who requested. Sending users.")
                with clients_lock:
                    users = ", ".join(nicknames)
                data_socket.sendall(f"200\n\n{users}".encode(FORMAT))

            elif command == "broadcast":
                if len(parts) < 2:
                    data_socket.sendall(f"500\n\n".encode(FORMAT))
                    continue

                with clients_lock:
                    if (conn, data_socket) not in clients:
                        data_socket.sendall(f"500\n\n".encode(FORMAT))
                        continue
                    index = clients.index((conn, data_socket))
                    user = nicknames[index]
                    current_clients = list(clients)

                parts = message.split(maxsplit=1)
                rest = parts[1]
                print(f"Broadcast requested by {user}")
                print(f"Message: {rest}")

                for client in current_clients:
                    client[1].sendall(f"200\n\nBroadcast\n{user}\n{rest}".encode(FORMAT))

            elif command == "private":
                if len(parts) < 3:
                    data_socket.sendall(f"500\n\n".encode(FORMAT))
                    continue

                with clients_lock:
                    if (conn, data_socket) not in clients or parts[1] not in nicknames:
                        data_socket.sendall(f"500\n\n".encode(FORMAT))
                        continue

                    sender_index = clients.index((conn, data_socket))
                    sender_user = nicknames[sender_index]
                    target_index = nicknames.index(parts[1])
                    target_client = clients[target_index][1]

                private_parts = message.split(maxsplit=2)
                rest = private_parts[2]

                print(f"Private message from {sender_user} to {private_parts[1]}")
                target_client.sendall(f"200\n\nPrivate\n{sender_user}\n{rest}".encode(FORMAT))
                data_socket.sendall(f"200\n\n".encode(FORMAT))

            elif command == "quit":
                connected = False
                nickname = None

                with clients_lock:
                    if (conn, data_socket) in clients:
                        index = clients.index((conn, data_socket))
                        clients.remove((conn, data_socket))
                        nickname = nicknames[index]
                        nicknames.pop(index)
                        current_clients = list(clients)
                    else:
                        current_clients = []

                if nickname is not None:
                    print(f"Quit requested by {nickname}")
                    for client in current_clients:
                        client[1].sendall(f"200\n\nquit\n{nickname}".encode(FORMAT))

                data_socket.sendall(f"200\n\n".encode(FORMAT))

            else:
                data_socket.sendall(f"500\n\n".encode(FORMAT))

        except (OSError, ValueError, IndexError):
            try:
                data_socket.sendall(f"500\n\n".encode(FORMAT))
            except OSError:
                pass
            break

    disconnected_nickname = None
    with clients_lock:
        if (conn, data_socket) in clients:
            index = clients.index((conn, data_socket))
            clients.remove((conn, data_socket))
            disconnected_nickname = nicknames[index]
            nicknames.pop(index)
            current_clients = list(clients)
        else:
            current_clients = []

    if disconnected_nickname is not None:
        for client in current_clients:
            try:
                client[1].sendall(f"200\n\nquit\n{disconnected_nickname}".encode(FORMAT))
            except OSError:
                pass

    conn.close()
    data_socket.close()
    data_server.close()



def start():
    print("Awaiting connections…")

    while True:
        conn, addr = server.accept()
        print("Connection requested. Creating data socket")
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

start()
