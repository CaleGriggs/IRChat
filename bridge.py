"""
For future use.

Bridge TCP to WebSocket to create browser based client

"""


import asyncio
import websockets
import socket

IRC_HOST = "127.0.0.1" # local host for now
IRC_PORT = 6667 
WS_PORT = 8080 

async def handle_client(websocket):
    # Connect to your local IRC-style TCP server
    irc_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc_sock.connect((IRC_HOST, IRC_PORT))
    irc_sock.setblocking(False)

    async def ws_to_tcp():
        async for msg in websocket:
            irc_sock.sendall((msg + "\n").encode())

    async def tcp_to_ws():
        loop = asyncio.get_event_loop()
        while True:
            data = await loop.run_in_executor(None, irc_sock.recv, 1024)
            if not data:
                break
            await websocket.send(data.decode())

    await asyncio.gather(ws_to_tcp(), tcp_to_ws())

async def main():
    print(f"WebSocket bridge running on ws://0.0.0.0:{WS_PORT}")
    async with websockets.serve(handle_client, "0.0.0.0", WS_PORT):
        await asyncio.Future()  # Run forever

asyncio.run(main())