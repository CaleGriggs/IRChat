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
serverPass = "test"


def broadcast(message, exclude=None):
    """Send message to all clients except one."""
    for client in clients:
        if client != exclude:
            try:
                client.sendall(message.encode("utf-8"))
            except:
                client.close()
                del clients[client]


def connectionReg(userClient, msg, passwordProvided= False):
    while not userClient.registered:
        parsedMessage = serverCommands.Message(msg)
        now = datetime.now().strftime("%m/%d %I:%M:%S %p")
        """
        PASSword comes first, but not required
        needs new NICKname and USERname
        """
        if parsedMessage.command == "PASS":
            if parsedMessage.params == serverPass:
                passwordProvided = True
                print(f"Password accepted from {userClient.address}")
        elif parsedMessage.command == "NICK":
            if parsedMessage.params != "":
                userClient.nickname = parsedMessage.params
            else:
                #TODO something wrong with input
                pass
        elif parsedMessage.command == "USER":
            if parsedMessage.params != "":
                userClient.username = parsedMessage.params
            else:
                #TODO something wrong with input
                pass
        if userClient.nickname != "" and userClient.username != "":
            if not passwordProvided:
                # userClient.nickname = "guest"
                #TODO reply that user has limited commands and their NICKname is set to guest
                pass
                
            userClient.registered = True
            print(f"{userClient.address} set their nickname to {userClient.nickname} and username to {userClient.username}")
            break
        else:
            # TODO NICKname or USERname not accepted
            pass
        data = userClient.connection.recv(1024)
        msg = data.decode()


            


def handle_client(conn, addr):
    #TODO watch out for many messages collected
    # and appending to the data buffer, split by \r\n
    # check for max number of bytes (512)
    print(type(conn))
    response = ""
    userClient = serverCommands.user(conn, addr)
    userClient.username = "guest"f
    while True:
        try:
            data = userClient.connection.recv(1024)
            if not data:
                break
            
            if userClient.registered:
                parsedMessage = serverCommands.Message(data.decode())
                response = serverCommands.receiveMessage(userClient, parsedMessage)
            else:
                connectionReg(userClient,data)
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
