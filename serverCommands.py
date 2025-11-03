"""
Handles functionality for server commands.
"""

import socket
import ssl


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
            command.setdefault(command,"")
        try:
            params, trailing = msg.split(":", 1)
            params = params.rstrip().split(" ")
        except ValueError:
            params,trailing = msg,""

        self.source = source
        self.command = command.upper()
        self.params = params
        self.tags = tags
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
    match msg.commands:
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
             # ERR_NEEDMOREPARAMS (461) - CONNOT BE PARSED, NOT ENOUGH PARAMS
            if msg.params == "":
                return ["ERR_NEEDMOREPARAMS", "461"]
            # ERR_PASSWDMISMATCH (464) - PASSWORD DOES NOT MATCH
            if msg.params != args[0]:
                return ["ERR_PASSWDMISMATCH", "464"]
            # ERR_ALREADYREGISTERED (462) - IF CLIENT TRIES TO CHANGE REGISTRATION INFO AFTER REGISTRATION
            if client.registered:
                return ["ERR_ALREADYREGISTERED", "462"]
            if msg.params == args[0] and not client.registered:
                return "Let em in"
            client.password = msg.trailing
            print()
        case "NICK":
            client.nickname = msg.trailing
        case "USER":
            client.usernam = msg.trailing
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
            # default/no command
            print("error")
    return ""
