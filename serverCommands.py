"""
Handles functionality for server commands.
"""

import socket


class user:
    def __init__(self, conn, addr):
        self.connection = conn
        self.address = addr

    registered = False
    connection = socket
    username = ""
    address = ""
    nickname = ""
    prefix = ""
    password = ""
    server = ""


class Message:
    """
    tags = { key : [ values ] }
    source = @ "HostName.com"
    command = / "DOTHIS"
    params = [ "with","these","params" ]
    trailing = : "Message"
    """

    def __init__(self, msg):
        self.msgSplit(msg)

    tags = {}
    source = ""
    command = ""
    params = []
    trailing = ""

    def msgSplit(self, msg):
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
        if msg[0] == ":":
            source, msg = msg.split(" ", 1)
            source = source[1:]
        command, msg = msg.split(" ", 1)
        params, trailing = msg.split(":", 1)
        params = params.rstrip().split(" ")

        self.source = source
        self.command = command.upper()
        self.params = params
        self.tags = tags
        self.trailing = trailing

    def constructMsg(self):
        outMessage = ""
        if self.tags:
            outMessage = "@"
            for key in self.tags.keys():
                outMessage = outMessage + f"{key}:"
                for value in self.tags[key]:
                    outMessage = outMessage + f"{value}"
        if self.source:
            outMessage = outMessage + f"source"

    def msgPrint(self):
        print(
            f"tags: {self.tags}\nsource: {self.source}\ncommand: {self.command}\nparams: {self.params}\ntrailing: {self.trailing}"
        )


def receiveMessage(client, msg):
    # conn.sendall("Goodbye!\n".encode())
    match msg.commands:
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
            print("error")
