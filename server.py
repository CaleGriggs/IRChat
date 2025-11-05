"""
IRC server
"""

import socket
import ssl
import threading
from datetime import datetime
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

file_path = os.path.join(BASE_DIR, "ssl_files")

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

class user:
    def __init__(self, conn, addr):
        self.connection = conn
        self.address = addr

    registered = False
    connection = ssl.SSLSocket
    username = ""
    address = ""
    nickname = ""
    prefix = ""
    server = ""


class Message:
    """
    tags = { key : [ values ] }
    source = @ "HostName.com"
    command = / "DOTHIS"
    params = [ "with","these","params" ]
    trailing = : "Message"
    """

    def __init__(self, msg=""):
        self.msgSplit(msg)

    tags = {}
    source = ""
    command = ""
    params = []
    trailing = ""

    def msgSplit(self, msg):
        if msg == "" or msg[-1:] != "\n":
            return
        msg = msg[:-1]
        if msg[-1:] == "\r":
            msg = msg[:-1]
        tag = ""
        tags = {}
        if msg[0] == "@":
            tag, msg = msg.split(" ", 1)
            tag = tag[1:]
            tagPairs = tag.split(";")
            for pair in tagPairs:
                try:
                    key, value = pair.split("=", 1)
                    value = value.split(",")
                    tags[key] = []
                except ValueError:
                    tags.setdefault(pair, "")
                for i in value:
                    tags[key].append(i)
        source = ""
        try:
            if msg[0] == ":":
                source, msg = msg.split(" ", 1)
                source = source[1:]
        except ValueError:
            pass
        try:
            command, msg = msg.split(" ", 1)
        except ValueError:
            command = ""
        msg.lstrip()
        i = 0
        params = []
        while i < len(msg):
            if msg[i] == ' ' and i < len(msg):
                if msg[i+1] == ' ':
                    params.append(msg)
                    break
                else:
                    params = msg.split(' ',1)
                    msg = params.pop(1)
                    i = 0
                    continue
            i += 1
        if msg:
            params.append(msg)
        trailing = params.pop(-1)
        
        self.tags = tags
        self.source = source
        self.command = command.upper()
        self.params = params
        self.trailing = trailing

    def constructMsg(self):
        outMessage = ""
        if self.tags:
            outMessage = "@"
            keys = list(self.tags.keys())
            for k in range(len(keys)):
                key = keys[k]
                outMessage = outMessage + str(key) + "="
                for v in range(len(self.tags[key])):
                    if v + 1 == len(self.tags[key]):
                        sep = ';'
                    if k + 1 == len(keys):
                        sep = ' '
                    if v + 1 != len(self.tags[key]):
                        sep = ','
                    outMessage = outMessage + str(self.tags[key][v]) + sep
        if self.source:
            outMessage = outMessage + ":" + self.source + " "
        outMessage = outMessage + str(self.command) + " "
        if self.params:
            for param in self.params:
                outMessage = outMessage + str(param) + " "
        if self.trailing:
            outMessage = outMessage + ":" + self.trailing 
        return outMessage + "\r\n"

    def msgPrint(self):
        print(
            f"tags: {self.tags}\nsource: {self.source}\ncommand: {self.command}\nparams: {self.params}\ntrailing: {self.trailing}"
        )


def receiveMessage(client, msg, args=[]):
    """
    client = user()  
    msg = Message()  
    agrs = [Either nothing or anything]
    """
    # conn.sendall("Goodbye!\n".encode())
    match msg.command:
        case "CAP":
            print()
        case "AUTHENTICATE":
            print()
        case "PASS":
            """
            Command: PASS
            Parameters: <password>
            args = [serverPassword]
            could also open a file here to check password against that
            """
            # ERR_ALREADYREGISTERED (462) - IF CLIENT TRIES TO CHANGE REGISTRATION INFO AFTER REGISTRATION
            if client.registered:
                return ["ERR_ALREADYREGISTERED", "462"]
             # ERR_NEEDMOREPARAMS (461) - CONNOT BE PARSED, NOT ENOUGH PARAMS
            elif msg.trailing == "":
                return ["ERR_NEEDMOREPARAMS", "461"]
            # ERR_PASSWDMISMATCH (464) - PASSWORD DOES NOT MATCH
            elif msg.trailing != serverPass:
                return ["ERR_PASSWDMISMATCH", "464"]
            # PASSWORD ACCEPTED
            elif msg.trailing == serverPass and not client.registered:
                client.registered = True
                return f"Password accepted from {client.address}"
        case "NICK":
            
            if msg.trailing == "":
                return ["ERR_NONICKNAMEGIVEN", "(431)"]
            
            elif msg.trailing != "":
                client.nickname = msg.trailing
            else:
                #TODO something wrong with input
                pass
        case "USER":
            if msg.trailing != "":
                client.username = msg.trailing
            else:
                #TODO something wrong with input
                pass
        case "PING":
            """
            Command: PING
            Parameters: <token>
            """
            if args:
                return f"PONG {args[0]}\r\n"
            else:
                return "PONG \r\n"
        case "PONG":
            """
            Command: PONG
            Parameters: [<server>] <token>
            """
            return f"PONG {args[0]}\r\n"
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
            # default/no command
            print("error")
    return ""


def connectionReg(userClient, msg):
    parsedMessage = Message(msg.decode())
    
    """
    PASSword comes first, but not required
    needs new NICKname and USERname
    """
    return receiveMessage(userClient, parsedMessage)

    if userClient.nickname != "" and userClient.username != "":
        if not passwordProvided:
            # userClient.nickname = "guest"
            #TODO reply that user has limited commands and their NICKname is set to guest
            pass
            
        userClient.registered = True
        print(f"{userClient.address} set their nickname to {userClient.nickname} and username to {userClient.username}")
    else:
        # TODO NICKname or USERname not accepted
        pass


def handle_client(conn, addr):
    #TODO watch out for many messages collected
    # and appending to the data buffer, split by \r\n
    # check for max number of bytes (512)
    print(type(conn))
    
    response = ""
    userClient = user(conn, addr)
    userClient.username = "guest"+str(len(clients.keys()))
    clients[userClient.username] = userClient

    buffer =[]
    while True:
        try:
            data = userClient.connection.recv(1024)
            if not data:
                break
            response = ""
            if userClient.registered:
                parsedMessage = Message(data.decode())
                response = receiveMessage(userClient, parsedMessage)
            else:
                response = connectionReg(userClient,data)
                # start PING/PONG loop
            now = datetime.now().strftime("%m/%d %I:%M:%S %p")
            print(f"{now}: {response}")
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

    
    # Setup
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=file_path+"\\server.crt", keyfile=file_path+"\\server.key")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()
        print("Server is running. Waiting for connections...")
        while True:
            # Wait for connections
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
