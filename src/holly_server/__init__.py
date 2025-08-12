import asyncio
import json
import websockets
import copy
import collections
import random

from holly_simulator import GeometricBrownianMotion

motion = GeometricBrownianMotion(100, 0.05, 0.15, 1)

playing = False
examplesample = {
    "name": "XXX",
    "uv": 100,
    "pv": 200,
    "amt": 400,
}
somedata = collections.deque([examplesample] * 100, maxlen=100)


async def send_dump(websocket):
    msg = {"playing": playing, "some_data": list(somedata)}
    await websocket.send(json.dumps(msg))


clients = set()


async def handler(websocket):
    global playing
    clients.add(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("action") == "play":
                playing = True
            elif data.get("action") == "pause":
                playing = False
            await send_dump(websocket)
    finally:
        clients.remove(websocket)


async def periodic_sender():
    while True:
        if playing:
            # modify some_data, e.g. take a step here
            modifiedsample = copy.deepcopy(examplesample)
            modifiedsample["uv"] *= random.randint(1, 3)
            modifiedsample["pv"] *= random.randint(1, 3)
            modifiedsample["amt"] *= random.randint(1, 3)
            somedata.append(modifiedsample)

            motion.step()
            modifiedsample["uv"] = motion.s

            await asyncio.gather(*(send_dump(ws) for ws in clients))
        # todo: allow user to modify step time
        await asyncio.sleep(0.05)


async def main1():
    print("server started")
    asyncio.create_task(periodic_sender())
    async with websockets.serve(handler, "localhost", 65135):
        await asyncio.Future()


def main():
    asyncio.run(main1())
