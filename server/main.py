import socket
from threading import Thread

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002

connected_users = {}
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print(f"Server {SERVER_HOST}:{SERVER_PORT} is running...")


def listen_for_client(client_socket, client_address):
    # Принимает имя клиента и добавляет его сокет в словарь клиентских сокетов
    name = client_socket.recv(1024).decode('cp1251')
    connected_users[client_socket] = name
    print(f"[+] {name} connected from {client_address}")

    while True:
        try:
            # Принимает сообщение от клиента
            message = client_socket.recv(1024).decode('cp1251')
            if not message:
                break
            sender_name, message = parse_message(message)

            if is_private_message(message):
                # Отправляет приватное сообщение получателю
                recipient, message = extract_private_message(message)
                send_private_message(sender_name, recipient, message)
            else:
                # Рассылает сообщение всем клиентам, кроме отправителя
                broadcast_message(sender_name, message)
        except ConnectionResetError:
            break

    # Отключает клиента и удаляет его сокет из словаря клиентских сокетов
    disconnect_client(client_socket)


# Разделяет сообщение на имя отправителя и текст сообщения
def parse_message(message):
    parts = message.split(":", 1)
    return parts[0], parts[1]


# Проверяет, является ли сообщение приватным
def is_private_message(message):
    return message.startswith("@")


# Извлекает имя получателя и текст приватного сообщения
def extract_private_message(message):
    recipient, message = message[1:].split(" ", 1)
    return recipient, message


# Отправляет приватное сообщение указанному получателю
def send_private_message(sender_name, recipient, message):
    for client_socket, name in connected_users.items():
        if name == recipient:
            client_socket.send(f"(Private) {sender_name}: {message}".encode())
            break


# Рассылает сообщение всем клиентам, кроме отправителя
def broadcast_message(sender_name, message):
    print(f"{sender_name}: {message}")
    for client_socket, name in connected_users.items():
        if name != sender_name:
            client_socket.send(f"{sender_name}: {message}".encode())
        else:
            client_socket.send(f"{name}: {message}".encode())


# Отключает клиента и удаляет его сокет из словаря клиентских сокетов
def disconnect_client(client_socket):
    name = connected_users[client_socket]
    del connected_users[client_socket]
    client_socket.close()
    print(f"[-] {name} disconnected")


#
def get_connected_users():
    return f"[{', '.join(connected_users.values())}]"


while True:
    client_socket, client_address = s.accept()
    t = Thread(target=listen_for_client, args=(client_socket, client_address))
    t.daemon = True
    t.start()
