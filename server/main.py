import socket
from threading import Thread

MAX_CONNECTION = 3  # пользователей


def con():
    while True:
        conn, addr = sock.accept()
        print("connected: ", addr)


th1 = Thread(target=con, args=())

sock = socket.socket()
sock.bind(('26.235.8.168', 1025))
sock.listen(MAX_CONNECTION)

th1.start()
