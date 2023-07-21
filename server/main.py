# подключаемые библиотеки
import socket  # для работы с сокетами
import tkinter as tk  # для создания графического интерфейса
from threading import Thread  # для работы с потоками
from datetime import datetime  # для работы с временем

SERVER_HOST = "0.0.0.0"  # ip
SERVER_PORT = 5002  # port
PASSWORD = "PASSWORD"  # пароль сервера

MAX_USERNAME_LENGTH = 30  # максимальная длина имени пользователя


connected_users = {}  # словарь для подключаемых пользователей, нужен для хранения сокета и имени
s = socket.socket()  # сокет сервера
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #
s.bind((SERVER_HOST, SERVER_PORT))  # привязывает сервер к определенному IP-адресу и порту
s.listen(5)  # прослушивание входящих сообщений
print(f"Server {SERVER_HOST}:{SERVER_PORT} is running...")  # вывод в консоль текста, что сервер начал работать


# основная функция для прослушивания пользователей, открывается потоком для каждого нового пользователя
def listen_for_client(client_socket):
    password = client_socket.recv(1024).decode('cp1251')  # принимаем пароль от пользователя
    while password != PASSWORD:  # если отправлен неправильный пароль, то сообщаем об этом и ждём правильный
        client_socket.send("wrong password".encode())  # отправляет сообщение пользователю, что пароль неправльный
        password = client_socket.recv(1024).decode('cp1251')  # принимает пароль от пользователя ещё раз
    name = client_socket.recv(1024).decode('cp1251')  # принимает имя от пользователя
    name = name[:MAX_USERNAME_LENGTH]  #
    connected_users[client_socket] = name
    update_users_list()

    update_chat_text(f"{name} has joined the chat.\n", color="green")

    while True:   # цикл для отправки сообщения пользователям от других пользователей
        try:
            message = client_socket.recv(1024).decode('cp1251')
            if not message:
                break

            if is_private_message(message):
                recipient, message = extract_private_message(message)
                send_private_message(connected_users[client_socket], recipient, message)
            else:
                broadcast_message(connected_users[client_socket], message)
                update_chat_text(f"{connected_users[client_socket]}: {message}\n")
        except ConnectionResetError:
            break

    disconnect_client(client_socket)


# проверяет приватное ли сообщение
def is_private_message(message):
    return message.startswith("@")


def extract_private_message(message):
    recipient, message = message[1:].split(" ", 1)
    return recipient, message


def send_private_message(sender_name, recipient, message):
    for client_socket, name in connected_users.items():
        if name == recipient:
            client_socket.send(f"(Private) {sender_name}: {message}".encode())
            break


def broadcast_message(sender_name, message):
    print(f"{sender_name}: {message}")
    for client_socket, name in connected_users.items():
        if name != sender_name:
            client_socket.send(f"{sender_name}: {message}".encode())
        else:
            client_socket.send(f"{name}: {message}".encode())


def disconnect_client(client_socket):
    name = connected_users[client_socket]
    del connected_users[client_socket]
    client_socket.close()
    print(f"[-] {name} disconnected")
    update_users_list()
    update_chat_text(f"{name} has left the chat. \n", color="red")


def update_users_list():
    users_list.delete(0, tk.END)
    for name in connected_users.values():
        users_list.insert(tk.END, name)


def get_connected_users():
    return f"[{', '.join(connected_users.values())}]"


def send_message(event=None):
    message = entry_message.get()
    if message:
        broadcast_message("Server", message)
        update_chat_text(f"Server: {message}\n")
        entry_message.delete(0, tk.END)


def update_chat_text(text, color=None):
    time_stamp = datetime.now().strftime('%H:%M:%S')
    formatted_text = f"{time_stamp:>8} | {text}"
    chat_text.config(state=tk.NORMAL)

    if color:
        chat_text.tag_configure(color, foreground=color)
        chat_text.insert(tk.END, formatted_text, color)
    else:
        chat_text.insert(tk.END, formatted_text)

    chat_text.see(tk.END)
    chat_text.config(state=tk.DISABLED)


def on_closing():
    s.close()
    root.destroy()


root = tk.Tk()
root.title("Chat Server")
root.minsize(800, 200)

# Create a grid layout with 3 columns and 2 rows
root.columnconfigure(0, weight=1, minsize=200)  # First column expands with window width
root.columnconfigure(1, weight=1)  # Second column expands with window width
root.columnconfigure(2, weight=0)  # Third column does not expand
root.rowconfigure(0, weight=1)     # First row expands with window height
root.rowconfigure(1, weight=0)     # Second row does not expand

users_frame = tk.Frame(root)
users_list = tk.Listbox(users_frame, width=20, bd=0)
users_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=(13, 3))
users_frame.grid(row=0, column=0, sticky=tk.NSEW)

chat_frame = tk.Frame(root)
chat_text = tk.Text(chat_frame, state=tk.DISABLED)
chat_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
chat_frame.grid(row=0, column=1, sticky=tk.NSEW)

entry_message = tk.Entry(root)
entry_message.grid(row=1, column=1, columnspan=1, sticky=tk.EW)
entry_message.bind("<Return>", send_message)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.grid(row=1, column=2, padx=(0, 3), pady=(0, 5))

# Закрытие окна
root.protocol("WM_DELETE_WINDOW", on_closing)


# Запускаем сервер в отдельном потоке
def start_server():
    while True:
        client_socket, client_address = s.accept()
        t = Thread(target=listen_for_client, args=(client_socket, ))
        t.daemon = True
        t.start()


Thread(target=start_server).start()

# Запускаем графический интерфейс
root.mainloop()
