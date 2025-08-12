import asyncio
import json
import websockets
import copy
import collections

from holly_simulator import GeometricBrownianMotion

motions = [
    copy.deepcopy(GeometricBrownianMotion(100, 0.04, 0.18, 1 / 365)) for _ in range(100)
]
time = 0

playing = False
examplesample = collections.deque(
    [copy.deepcopy({"time": 0, "data": [100] * 100}) for _ in range(100)], maxlen=100
)


async def send_dump(websocket):
    msg = {"playing": playing, "gbm_paths": list(examplesample)}
    await websocket.send(json.dumps(msg))


clients = set()


async def handler(websocket):
    global playing
    clients.add(websocket)
    await send_dump(websocket)
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
    global time
    while True:
        if playing:
            # modify some_data, e.g. take a step here
            time += 1
            data = []
            for motion in motions:
                motion.step()
                data.append(motion.s)

            examplesample.append({"time": time, "data": data})

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
