"""
Command Line Interface for IRC client

"""

import socket
import threading
from datetime import datetime
import curses
import time
import sys


class Message:
    tags = {}
    source = ""
    commands = ""
    params = []
    trailing = ""


SERVER = "127.0.0.1"  # localhost for now
PORT = 6667  # Might switch to TSL 6697

chatHistory = []

connected = threading.Event()
token = -1


def heartbeat(sock, chat_win, lock):
    global token

    while True:
        connected.clear()
        try:
            time.sleep(10)
            sock.sendall(f"PING {str(token)}".encode())
        except Exception as e:
            print(f"Error sending ping: {e}")
        if connected.wait():
            continue
        else:
            handleDisconnect(sock, chat_win, lock)


def handleDisconnect(sock, chat_win, lock):
    sock.close()
    with lock:
        redraw_chat(chat_win, "Disconnected trying to reconnect...")
    return estabConnection(chat_win)


def estabConnection(chat_win):
    global token
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SERVER, PORT))
            connected.set()
            """
                try:
                    while True:
                        msg = sock.recv(1024).decode()
                        if not msg:
                            break
                        connected.set()
                        break
                except:
                    print()
                """

            redraw_chat(chat_win, "Connected!")
            return sock
        except (ConnectionRefusedError, TimeoutError, socket.timeout):
            redraw_chat(chat_win, "Failed to connect. Trying again...")
            sock.close()
            time.sleep(5)
        except KeyboardInterrupt:
            redraw_chat(chat_win, "Connection request canceled.")
            break


def redraw_input(input_win, buffer=""):
    input_win.clear()
    width = input_win.getmaxyx()[1]
    input_win.addstr(0, 0, "=" * (width - 1))
    input_win.addstr(2, 0, "> " + buffer)
    input_win.refresh()


def redraw_chat(chat_win, msg):
    now = datetime.now().strftime("%m/%d %I:%M:%S %p")
    chatHistory.append(f"{now}: {msg}")
    chat_win.clear()
    height, width = chat_win.getmaxyx()
    start_line = max(0, len(chatHistory) - height)
    for i, msg in enumerate(chatHistory[start_line:]):
        chat_win.addstr(i, 0, msg[: width - 1])
    chat_win.refresh()
    if len(chatHistory) > 20:
        chatHistory.pop(0)


def msgSplit(msg, parsedMessage):
    tag = ""
    tags = {}
    if msg[0] == "@":
        tag, msg = msg.split(" ", 1)
        tag = tag[1:]
        tagPairs = tag.split(";")
        for pair in tagPairs:
            try:
                key, value = pair.split("=", 1)
            except ValueError:
                tags.setdefault(pair, "")
            tags.update({key: value})
    source = ""
    if msg[0] == ":":
        source, msg = msg.split(" ", 1)
        source = source[1:]
    command, msg = msg.split(" ", 1)
    params, trailing = msg.split(":", 1)
    params = params.split(" ")

    parsedMessage.tags = tags
    parsedMessage.source = source
    parsedMessage.command = command
    parsedMessage.params = params
    parsedMessage.trailing = trailing


def receive_messages(sock, chat_win, lock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg or not connected:
                break
            with lock:
                parsedMessage = Message()
                msgSplit(msg, parsedMessage)

                # print(f"{now}: {msg}", end="")
                if (
                    msg == "Welcome! Please set your nickname using: /NICK <name>\n"
                    or msg == "Goodbye!\n"
                ):
                    connected.set()

                if msg.split(" ", 1)[0] == "/PING":
                    msg = msg.split(" ", 1)[1]
                    sock.sendall(f"/PONG {msg}".encode())
                if msg.split(" ", 1)[0] == "/PONG":
                    connected.set()
                redraw_chat(chat_win, msg)
        except:
            print("Disconnected from server.")
            connected.clear()
            sock.close()
            break


def send_message(sock, msg):

    # default = PRIVMSG
    # /COMMAND auto capitalize
    # prepend source, tags
    # append params and \r\n
    newMessage = Message()

    sock.sendall(msg.encode())


def main(stdscr):
    curses.curs_set(1)
    height, width = stdscr.getmaxyx()

    chat_height = height - 3
    input_hieght = 3

    chat_win = curses.newwin(chat_height, width, 0, 0)
    input_win = curses.newwin(input_hieght, width, chat_height, 0)
    input_win.timeout(100)

    lock = threading.Lock()

    redraw_chat(chat_win, "Connecting to server...")
    sock = estabConnection(chat_win)
    threading.Thread(
        target=receive_messages, args=(sock, chat_win, lock), daemon=True
    ).start()

    redraw_input(input_win)

    buffer = ""
    input_win.nodelay(True)
    curses.curs_set(1)
    connected.wait()
    try:  # input handling
        while True:
            ch = input_win.getch()
            if ch == -1:
                continue
            elif ch in (10, 13):  # newline, return
                msg = buffer.strip()
                if msg:
                    if msg == "/QUIT":
                        send_message(sock, msg)

                        connected.wait()
                        time.sleep(1)
                        break
                    sock.sendall(msg.encode())
                    with lock:
                        redraw_chat(chat_win, f"[You]: {msg}")
                buffer = ""
            elif ch in (8, 127):  # back space, delete
                buffer = buffer[:-1]
            elif 0 <= ch <= 255:
                buffer += chr(ch)
            elif ch == 27:  # escape
                sock.sendall("/QUIT".encode())
                break
            with lock:
                redraw_input(input_win, buffer)
    except KeyboardInterrupt:
        sock.sendall("/QUIT".encode())

    send_message(sock, input_win, chat_win, lock)

    sock.close()


if __name__ == "__main__":
    curses.wrapper(main)
    input()
