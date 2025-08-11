import asyncio
import websockets

async def echo(websocket, path):
    async for message in websocket:
        await websocket.send(message)

async def main1():
    async with websockets.serve(echo, "localhost", 8765):
        await asyncio.Future()

def main():
    asyncio.run(main1())
