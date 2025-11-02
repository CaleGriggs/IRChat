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
PORT = 6697  # typical IRC port | might switch to TLS 6697

clients = {}  # socket -> nickname
channels = [] # list of channels


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
    now = datetime.now().strftime("%m/%d %I:%M:%S %p")
    passwordProvided = False
    while not userClient.registered:
        """
        PASSword comes first, but not required
        needs new NICKname and USERname
        """
        if msg.command == "PASS":
            # set PASSword
            pass
        elif msg.command == "NICK":
            # set NICKname
            pass
        elif msg.command == "USER":
            # set USER
            pass
        if userClient.nickname != "" and userClient.username != "":
            if not passwordProvided:
                userClient.nickname = "guest"
                #TODO reply that user has limited commands and their NICKname is set to guest
            userClient.registered = True
        else:
            # TODO NICKname or USERname not accepted
            pass
            


def handle_client(conn, addr):
    #TODO watch out for many messages collected
    # and appending to the data buffer, split by \r\n
    # check for max number of bytes (512)
    print(type(conn))
    response = ""
    userClient = serverCommands.user(conn, addr)
    while True:
        try:
            data = userClient.connection.recv(1024)
            if not data:
                break
            parsedMessage = serverCommands.Message(data.decode().strip())
            if userClient.registered:
                response = serverCommands.receiveMessage(userClient, parsedMessage)
            else:
                connectionReg(userClient, parsedMessage)
                # start PING/PONG loop
        except ConnectionResetError:
            break

    # Disconnect message sent upon while loop break
    if conn in clients:
        left_nick = clients[conn]
        del clients[conn]
        broadcast(f"*** {left_nick} left the chat ***\n")
    conn.close()


def main():
    print(f"Starting server on {HOST}:{PORT} ...")


    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print("Server is running. Waiting for connections...")
        while True:
            conn, addr = server.accept()
            now = datetime.now().strftime("%m/%d %I:%M:%S %p")
            print(f"{now}: New connection from {addr}")
            try:
                tls_client = context.wrap_socket(conn, server_side=True)
                threading.Thread(target=handle_client, args=(tls_client, addr), daemon=True).start()
            except ssl.SSLError as e:
                print(f"TLS handshake failed from {addr}: {e}")
                conn.close()

if __name__ == "__main__":
    main()
