"""
IRC server
"""

import socket
import ssl
import threading
from datetime import datetime
import time
import serverCommands

HOST = "0.0.0.0"  # Local for now | listen on all network interfaces
PORT = 6667  # typical IRC port | might switch to TLS 6697

clients = {}  # socket -> nickname


def broadcast(message, exclude=None):
    """Send message to all clients except one."""
    for client in clients:
        if client != exclude:
            try:
                client.sendall(message.encode("utf-8"))
            except:
                client.close()
                del clients[client]


def connectionReg(userClient, msg):
    conn = userClient.connection, addr = userClient.address
    now = datetime.now().strftime("%m/%d %I:%M:%S %p")

    while not userClient.registered:
        match msg.split(" ", 1)[0]:
            case "NICK":
                if nickname is None:
                    currentName = addr
                    nickname = msg.split(" ", 1)[1]
                    clients[conn] = nickname
                    broadcast(f"*** {nickname} joined the chat ***\n", exclude=conn)
                else:
                    nickname = msg.split(" ", 1)[1]
                    clients[conn] = nickname
                    conn.sendall(f"Nickname set to {nickname}\n".encode())
                    broadcast(
                        f"[{currentName}] changed their name to {nickname}.\n",
                        exclude=conn,
                    )
                print(f"{now}:{currentName} set nickname to {nickname}")
                currentName = nickname
            case _:
                pass


def handle_client(conn, addr):
    userClient = serverCommands.user(conn, addr)
    while True:
        try:
            data = userClient.connection.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            if userClient.registered:
                parsedMessage = serverCommands.Message(msg)
                serverCommands.receiveMessage(userClient, parsedMessage)
            else:
                connectionReg(userClient, msg)
        except ConnectionResetError:
            break

    # Disconnect message sent upon while loop break
    if conn in clients:
        left_nick = clients[conn]
        del clients[conn]
        broadcast(f"*** {left_nick} left the chat ***\n")
    conn.close()


def main():
    print(f"Starting server on {HOST}:{PORT}...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        # print("Server is running. Waiting for connections...")
        while True:
            conn, addr = server.accept()
            now = datetime.now().strftime("%m/%d %I:%M:%S %p")
            print(f"{now}: New connection from {addr}")
            threading.Thread(
                target=handle_client, args=(conn, addr), daemon=True
            ).start()


if __name__ == "__main__":
    main()
