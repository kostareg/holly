import asyncio
import json
import websockets
import collections
import tensorflow as tf

from holly_simulator import VectorizedGeometricBrownianMotion

size = 100
dt = 1 / 252
motion = VectorizedGeometricBrownianMotion(size, 100.0, 0.04, 0.18, dt)
time = 0
T_years = 2

playing = False
examplesample = collections.deque([{}] * 100, maxlen=100)


async def send_dump(websocket):
    msg = {
        "playing": playing,
        "gbm_paths": list(examplesample),
        "tau": T_years - time * dt,
    }
    await websocket.send(json.dumps(msg))


clients = set()


async def handler(websocket):
    global playing, motion, time, examplesample
    clients.add(websocket)
    await send_dump(websocket)
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("action") == "play":
                playing = True
            elif data.get("action") == "pause":
                playing = False
            elif data.get("action") == "reset":
                motion = VectorizedGeometricBrownianMotion(size, 100.0, 0.04, 0.18, dt)
                examplesample = collections.deque(
                    [{}] * 100,
                    maxlen=100,
                )
                time = 0
            await send_dump(websocket)
    finally:
        clients.remove(websocket)


async def periodic_sender():
    global time
    while True:
        if playing:
            # modify some_data, e.g. take a step here
            time += 1
            motion.step()

            examplesample.append(
                {
                    "time": time,
                    "data": tf.reshape(tf.abs(motion.s), [-1]).numpy().tolist(),
                }
            )

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
