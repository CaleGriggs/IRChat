"""
IRC server
"""


import socket
import ssl
import threading
from datetime import datetime
import time
import serverCommands


HOST = "0.0.0.0"    # Local for now | listen on all network interfaces
PORT = 6667         # typical IRC port | might switch to TLS 6697

clients = {}        # socket -> nickname

class user():
    registered = False
    connection = socket
    address = ""
    nickname = ""
    prefix = ""
    password = ""
    server = ""
    def __init__(self, conn, addr):
        self.connection = conn
        self.address = addr
  
class Message():
    tags = {}
    source = ""
    commands = ""
    params = []
    trailing = ""

def msgSplit(msg,parsedMessage):
    tag = ""
    tags = {}
    if msg[0] == "@":
         tag,msg = msg.split(' ',1)
         tag = tag[1:]
         tagPairs = tag.split(';')
         for pair in tagPairs:
            try:
                key, value = pair.split('=',1)
            except ValueError:
                tags.setdefault(pair, '')
            tags.update({key: value})
    source = ""
    if msg[0] == ":":
        source, msg = msg.split(' ', 1)
        source = source[1:]   
    command,msg = msg.split(' ',1)
    params,trailing = msg.split(':',1)
    params = params.split(' ')

    parsedMessage.tags = tags
    parsedMessage.source = source
    parsedMessage.command = command.upper()
    parsedMessage.params = params
    parsedMessage.trailing = trailing

def broadcast(message, exclude=None):
    """Send message to all clients except one."""
    for client in clients:
        if client != exclude:
            try:
                client.sendall(message.encode('utf-8'))
            except:
                client.close()
                del clients[client]

def connectionReg(userClient, msg):
    conn = userClient.connection, addr = userClient.address
    now = datetime.now().strftime("%m/%d %I:%M:%S %p")
    currentName = ""
    nickname = None
    while not userClient.registered:
        match msg.split(" ",1)[0]:
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
                    broadcast(f"[{currentName}] changed their name to {nickname}.\n", exclude=conn)
                print(f"{now}:{currentName} set nickname to {nickname}")
                currentName = nickname
            case _:
                pass

def handle_client(conn, addr):
    userClient = user(conn, addr)
    while True:
        try:
            data = userClient.connection.recv(1024)
            if not data:
                break
            msg = data.decode().strip()
            if userClient.registered:
                receiveMessage(userClient, msg)
            else:
                connectionReg(userClient,msg)
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
        #print("Server is running. Waiting for connections...")
        while True:
            conn, addr = server.accept()
            now = datetime.now().strftime("%m/%d %I:%M:%S %p")
            print(f"{now}: New connection from {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()

def receiveMessage(userClient, msg):
    parsedMessage = Message
    msgSplit(msg, parsedMessage)
    # conn.sendall("Goodbye!\n".encode())
    match parsedMessage.commands:
        case "CAP":
            print()
        case "AUTHENTICATE":
            print()
        case "PASS":
            """
            Command: PASS
            Parameters: <password> <version> <flags> [<options>]
            """
            print()
        case "NICK":
            userClient.nickname = serverCommands.nick(parsedMessage.trailing)
        case "USER":
            print()
        case "PING":
            """
            Command: PING
            Parameters: <token>
            """
            print()
        case "PONG":
            """
            Command: PONG
            Parameters: [<server>] <token>
            """
            print()
        case "OPER":
            print()
        case "QUIT":
            print()
        case "ERROR":
            print()
        case "JOIN":
            print()
        case "PART":
            print()
        case "TOPIC":
            print()
        case "NAMES":
            print()
        case "LIST":
            print()
        case "INVITE":
            print()
        case "KICK":
            print()
        case "MOTD":
            print()
        case "VERION":
            print()
        case "ADMIN":
            print()
        case "CONNECTION":
            print()
        case "LUSERS":
            print()
        case "TIME":
            print()
        case "STATS":
            print()
        case "HELP":
            print()
        case "INFO":
            print()
        case "MODE":
            print()
        case "PRIVMSG":
            print()
        case "NOTICE":
            print()
        case "WHO":
            print()
        case "WHOIS":
            print()
        case "WHOWAS":
            print()
        case "KILL":
            print()
        case "REHASH":
            print()
        case "RESTART":
            print()
        case "SQUIT":
            print()
        case "AWAY":
            print()
        case "LINKS":
            print()
        case "USERHOST":
            print()
        case "WALLOPS":
            print()
        case _:
            print("error")