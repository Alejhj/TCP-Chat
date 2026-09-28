import socket
import threading

PORT = 5050
FORMAT = 'utf-8'

response_received = threading.Event()
pending_command = None
pending_lock = threading.Lock()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def get_status(response):
    status, _, rest = response.partition("\n\n")

    command = ""
    data = rest

    first, separator, remaining = rest.partition("\n")
    if first.lower() in ["broadcast", "private", "join", "quit"]:
        command = first.lower()
        data = remaining if separator else ""

    return status.strip(), command, data


def recieve():
    global pending_command

    while True:
        try:
            response = data_socket.recv(1024).decode(FORMAT)

            if not response:
                break

            status, command, data = get_status(response)

            with pending_lock:
                waiting_for = pending_command

            if command == "broadcast":
                parts = data.splitlines()
                user = parts[0] if len(parts) > 0 else ""
                message = "\n".join(parts[1:]) if len(parts) > 1 else ""

                if status == "200":
                    print("200 status code received.")
                    print(f"Broadcast message from {user}: {message}")
                else:
                    print("500 status code received.")

                if waiting_for == "broadcast":
                    response_received.set()

            elif command == "private":
                parts = data.splitlines()
                user = parts[0] if len(parts) > 0 else ""
                message = "\n".join(parts[1:]) if len(parts) > 1 else ""

                if status == "200":
                    print("200 status code received.")
                    print(f"{user}: {message}")
                else:
                    print("500 status code received.")

            elif command == "join":
                if status == "200":
                    print(f"{data} has joined the chat")

            elif command == "quit":
                if status == "200":
                    print(f"{data} has left the chat")

            elif command == "":

                if waiting_for == "login":
                    if status == "200":
                        print("200 status code received. Login successful")
                    else:
                        print("500 status code received. Login unsuccessful")
                    response_received.set()

                elif waiting_for == "who":
                    if status == "200":
                        print(f"200 status code received. Users currently connected: {data}")
                    else:
                        print("500 status code received.")
                    response_received.set()

                elif waiting_for == "private":
                    if status == "200":
                        print("200 status code received. Message sent.")
                    else:
                        print("500 status code received.")
                    response_received.set()

                elif waiting_for == "quit":
                    if status == "200":
                        print("200 status code received.")
                    else:
                        print("500 status code received.")
                    response_received.set()
                    break

                elif waiting_for == "broadcast":

                    if status == "500":
                        print("500 status code received.")
                        response_received.set()

        except OSError:
            break

    data_socket.close()

        


def main():
    global pending_command

    print("Starting client…")

    while True:
        user_input = input("> ").strip()
        parts = user_input.split()

        
        if not parts:
            continue

        command = parts[0].lower()

        if command == "connect":
            if len(parts) < 3:
                print("500 status code received.")
                continue

            ADDR = (parts[1],int(parts[2]) )
            
            client.connect(ADDR)

            response = client.recv(1024).decode(FORMAT)

            
            status, _, data = response.partition("\n\n")
            data = data.strip()

            if status == "200":
                print(f"200 status code received. Starting data connection on port {data}")
            else:
                print("500 status code received.")
                continue
            
            DATAPORT = int(data)

            DATA_ADDR = (parts[1],DATAPORT)
            
            data_socket.connect(DATA_ADDR)

            if status == "200":
                recieve_thread = threading.Thread(target=recieve)
                recieve_thread.start()
            
        elif command in ["login", "who", "broadcast", "private", "quit"]:

            response_received.clear()

            with pending_lock:
                pending_command = command

            client.sendall(user_input.encode(FORMAT))

            response_received.wait()

            with pending_lock:
                pending_command = None

            if command == "quit":
                break

    client.close()

        

    

main_thread = threading.Thread(target=main)
main_thread.start()
