"""
Command Line Interface for IRC client

"""

#TODO rewrite the whole thing

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
quit = threading.Event()


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
    serverPass = ""
    tryLogin = True
    
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
            if field == "Password" and not connected.is_set():
                val = "•" * len(val)
            # cursor indicator for the active field
            cursor_char = "_" if i == field_index else ""
            win.addstr(y, 2, f"{label:<12} {val}{cursor_char}")

        if error_msg == "" or error_msg == "Needs a Passord.":
            win.addstr(win_height - 5, 2, "Please provide a Severname and Passowrd.")

        if fields[0] == "USER":
            win.addstr(win_height - 5, 2, "Please Provide a Username and Nickname.")

        #if len(inputWarning) > 40:    # word wrapping?
        win.addstr(win_height - 4, 2, f"{error_msg}")
        win.addstr(win_height - 2, 2, "<Tab> Next   <Enter> OK   <Esc> Cancel")
        win.refresh()

    
    render()
    while tryLogin:
        ch = win.getch()
        if ch in (9, curses.KEY_BTAB):                                    # Tab
            field_index = (field_index + 1) % len(fields)
        elif ch in (10, 13):                                              # Enter
            if not values[0] and not values[1] and field_index == len(fields) - 1:
                inputWarning = True
            else:
                if field_index == len(fields)-1 and not values[1]:
                    inputWarning = False
                    error_msg = "Needs a Passord."
                else:
                    error_msg = ""
            if values[0] and values[1] and field_index == len(fields)-1 and not inputWarning and not connected.is_set():  # Confirm input
                    error_msg = "Connecting..."
                    attempts = 4
                    SERVER = values[0]

#################################### <For Testing> ########################################################
                    try:
                        with open("IRCchat\test.txt", "r") as file:
                            SERVER = file.read()
                            file.close()
                    except FileNotFoundError:
                        print("The file 'test.txt' was not found.")
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        
#################################### </For Testing> ########################################################                        

                    while attempts > 0:
                        render()
                        try:
                            context = ssl.create_default_context()
#################################### <For Testing> ########################################################
                            context.check_hostname = False
                            context.verify_mode = ssl.CERT_NONE
#################################### </For Testing> ########################################################
                            raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                            sock = context.wrap_socket(raw_sock, server_hostname=SERVER) 
                            sock.connect((SERVER, PORT))
                            connected.set()
                            error_msg = "Connected!"
                            serverPass = values[1]
                            fields = ["USER","NICK"] 
                            time.sleep(1)
                            sock.sendall(f"PASS {serverPass}\r\n".encode())
                            values = ["",""]
                            render()   # Will now ask for USER and NICK
                            break
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
                                tryLogin = False
                                break
                            time.sleep(.5)
                        except (socket.gaierror, UnboundLocalError):
                            error_msg = "DNS lookup failed, check hostname."
                            render()
                            time.sleep(5)
                            draw_connect_window(stdscr, error_msg)
                        except KeyboardInterrupt:
                            error_msg = "Connection request canceled."
                            break
            elif values[0] and values[1] and field_index == len(fields)-1 and not inputWarning and connected.is_set():
                user, nick = values
                sock.sendall(f"USER {user}\r\n".encode())
                time.sleep(1)
                sock.sendall(f"NICK {nick}\r\n".encode())
                return sock
            
            field_index = (field_index + 1) % len(fields)
        elif ch == 27:                                                    # Esc
            #TODO check if connected/ about to send NICK/USER should only
            # go back/ drop connection
            fields = ["",""]
            values = ["",""]
            quit.set()
            tryLogin = False
            return None
        elif ch in (8, 127, curses.KEY_BACKSPACE):                        # Backspace
            values[field_index] = values[field_index][:-1]
        elif 32 <= ch <= 126:                                             # Update buffer
            if len(values[field_index]) < 100:
                values[field_index] += chr(ch)
        if tryLogin: 
            render()  

def redraw_input(stdscr, sock, buffer=""):
    curses.curs_set(1)

    #redraw_chat(stdscr, buffer)

    height, width = stdscr.getmaxyx()
    chat_height = height - 3
    input_height = 3

    input_win = curses.newwin(input_height, width, chat_height, 0)
    input_win.nodelay(True)
    input_win.timeout(100)

    try:
        while True and connected.is_set(): 
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
                quit.set()
                return

    except KeyboardInterrupt:
        connected.clear()

def redraw_chat(stdscr, msg = ''):
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
    while connected.is_set():
        try:
            msg = sock.recv(1024).decode()
            if not msg or not connected.is_set():
                break
            with lock:
                parsedMessage = serverCommands.Message(msg)

                redraw_chat(stdscr, parsedMessage)
        except:
            connected.clear()
            sock.close()
            draw_connect_window(stdscr, "Disconnected from server.")
            break


def send_message(stdscr, sock, msg):
    # default = PRIVMSG
    # /COMMAND auto capitalize
    # prepend source, tags
    # append params and \r\n
    newMessage = serverCommands.Message(msg)
    msg = newMessage.constructMsg()
    sock.sendall(msg.encode())


def main(stdscr):
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    sock = draw_connect_window(stdscr)
    if sock is None:
        return  # user pressed Esc
    
    
    lock = threading.Lock()
    threading.Thread(target=receive_messages, args=(stdscr,sock, lock), daemon=True).start()
    redraw_chat(stdscr)
    redraw_input(stdscr, sock)
    
    sock.close()
    connected.clear()

    #TODO ask if user wants to quit


if __name__ == "__main__":
    curses.wrapper(main)
    input()