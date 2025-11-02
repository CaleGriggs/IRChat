"""
Command Line Interface for IRC client

"""

import socket
import threading
from datetime import datetime
import curses
import time
import sys
import serverCommands
import ssl


SERVER = "127.0.0.1"  # localhost for now
PORT = 6697  # Might switch to TSL 6697

chatHistory = []

connected = threading.Event()


def draw_connect_window(stdscr,error_msg=""):
    curses.curs_set(1)
    height, width = stdscr.getmaxyx()
    win_width = 45
    win_height = 9
    start_y = (height - win_height) // 2
    start_x = (width - win_width) // 2
    win = curses.newwin(win_height, win_width, start_y, start_x)
    win.keypad(True)

    fields = ["Servername", "Password"]
    values = ["", ""]
    field_index = 0
    inputWarning = False

    def render():
        win.clear()
        win.box()
        win.addstr(0, (win_width - 28) // 2, " Connect to remote server ")

        for i, field in enumerate(fields):
            y = 2 + i
            label = f"{field}:"
            val = values[i]
            if len(val) > 23:
                val = val[-23:]
            if field == "Password":
                val = "•" * len(val)
            # Add cursor indicator for the active field
            cursor_char = "_" if i == field_index else ""
            win.addstr(y, 2, f"{label:<12} {val}{cursor_char}")

        if inputWarning:
            win.addstr(win_height - 4, 2, "Please provide a Severname and Passowrd.")

        #if len(inputWarning) > 40:    # word wrapping?
        win.addstr(win_height - 4, 2, f"{error_msg}")
        win.addstr(win_height - 2, 2, "<Tab> Next   <Enter> OK   <Esc> Cancel")
        win.refresh()

    render()

    while True:
        ch = win.getch()

        if ch in (9, curses.KEY_BTAB):                                    # Tab
            field_index = (field_index + 1) % len(fields)
        elif ch in (10, 13):                                              # Enter
            if not values[0] and not values[1] and field_index == len(fields) - 1:
                inputWarning = True
                field_index = (field_index + 1) % len(fields)
            else:
                if field_index == len(fields)-1 and not values[0]:
                    inputWarning = False
                    error_msg = ""
            if values[0] and values[1] and field_index == len(fields)-1:  # Confirm input
                    error_msg = "Connecting..."
                    attempts = 4
                    SERVER = values[0]

                    try:
                        with open("test.txt", "r") as file:
                            SERVER = file.read()
                            file.close()
                    except FileNotFoundError:
                        print("The file 'test.txt' was not found.")
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    while attempts > 0:
                        render()
                        try:
                            context = ssl.create_default_context()
#########################################################################################################
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
#########################################################################################################
                            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                            sock = context.wrap_socket(raw_sock, server_hostname=SERVER) 
                            sock.connect((SERVER, PORT))
                            connected.set()
                            error_msg = "Connected!"
                            #TODO fields = ["USER","NICK"]
                            # 
                            render()
                            time.sleep(1)

                            #TODO once fields is updated remove this and do render() again
                            # and check for connected == True
                            return sock
                        except (ConnectionRefusedError, TimeoutError, socket.timeout):
                            sock.close()
                            attempts  -= 1
                            error_msg = f"Failed to connect. Trying again... {attempts}"
                            render()
                            if not attempts:
                                error_msg = "Connection timeout, try again later"
                                render()
                                time.sleep(3)
                                sock.close()
                                connected.clear()
                                draw_connect_window(stdscr)
                            time.sleep(.5)
                        except (socket.gaierror, UnboundLocalError):
                            error_msg = "DNS lookup failed, check hostname."
                            render()
                            time.sleep(5)
                            draw_connect_window(stdscr, error_msg)
                        except KeyboardInterrupt:
                            error_msg = "Connection request canceled."
                            break
            field_index = (field_index + 1) % len(fields)
        elif ch == 27:                                                    # Esc
            return None
        elif ch in (8, 127, curses.KEY_BACKSPACE):                        # Backspace
            values[field_index] = values[field_index][:-1]
        elif 32 <= ch <= 126:                                             # Update buffer
            if len(values[field_index]) < 100:
                values[field_index] += chr(ch)
        render()  

def redraw_input(stdscr, sock, lock, buffer=""):
    curses.curs_set(1)

    #redraw_chat(stdscr, buffer)

    height, width = stdscr.getmaxyx()
    chat_height = height - 3
    input_height = 3

    input_win = curses.newwin(input_height, width, chat_height, 0)
    input_win.nodelay(True)
    input_win.timeout(100)

    try:
        while True: 
            input_win.clear()
            width = input_win.getmaxyx()[1]
            input_win.addstr(0, 0, "=" * (width - 1))
            input_win.addstr(2, 0, "> " + buffer)
            input_win.refresh()

            ch = input_win.getch()
            if ch == -1:
                continue
            elif ch in (10, 13):                        # newline, return
                #TODO message object?
                msg = buffer.strip()
                if msg:
                    redraw_chat(stdscr, msg)
                    send_message(stdscr, sock, msg)
                buffer = ""
            elif ch in (8, 127, curses.KEY_BACKSPACE):  # back space, delete
                buffer = buffer[:-1]
            elif 0 <= ch <= 255:
                buffer += chr(ch)
            if ch == 27:                                # Esc
                return

    except KeyboardInterrupt:
        connected.clear()

def redraw_chat(stdscr, msg=""):
    height, width = stdscr.getmaxyx()
    chat_height = height - 3
    chat_win = curses.newwin(chat_height, width, 0, 0)

    now = datetime.now().strftime("%m/%d %I:%M:%S %p")
    if msg:
        chatHistory.append(f"{now}: {msg}")
    chat_win.clear()
    height, width = chat_win.getmaxyx()
    start_line = max(0, len(chatHistory) - height)
    for i, msg in enumerate(chatHistory[start_line:]):
        chat_win.addstr(i, 0, msg[: width - 1])
    chat_win.refresh()
    if len(chatHistory) > 20:
        chatHistory.pop(0)

def receive_messages(stdscr, sock, lock):
    while connected:
        try:
            msg = sock.recv(1024).decode()
            if not msg or not connected:
                break
            with lock:
                parsedMessage = serverCommands.Message(msg)

                redraw_chat(stdscr, msg)
        except:
            connected.clear()
            sock.close()
            draw_connect_window(stdscr, "Disconnected from server.")


def send_message(stdscr, sock, msg):
    # default = PRIVMSG
    # /COMMAND auto capitalize
    # prepend source, tags
    # append params and \r\n
    newMessage = serverCommands.Message(msg)

    sock.sendall(msg.encode())


def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    sock = draw_connect_window(stdscr)
    if sock is None:
        return  # user pressed Esc
    
    #TODO send NICK and USER commands
    
    lock = threading.Lock()
    threading.Thread(target=receive_messages, args=(stdscr,sock, lock), daemon=True).start()
    redraw_chat(stdscr)
    redraw_input(stdscr, sock, lock)
    
    sock.close()
    connected.clear()


if __name__ == "__main__":
    curses.wrapper(main)
    input()