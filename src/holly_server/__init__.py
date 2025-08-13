import asyncio
import json
import websockets
import collections
import tensorflow as tf

from holly_simulator import VectorizedGeometricBrownianMotion, BlackScholes, Assets

time_per_step = 0
size = 100
dt = 1 / 252
mu = 0.04
sigma = 0.18
K = 100
r = 0.035
motion = VectorizedGeometricBrownianMotion(size, 100.0, mu, sigma, dt)
time = 0
T = 2

playing = False
gbm_paths = collections.deque([{}] * 100, maxlen=100)
delta = collections.deque([{}] * 100, maxlen=100)
price = collections.deque([{}] * 100, maxlen=100)

assets = collections.deque([{}] * 100, maxlen=100)


async def send_dump(websocket):
    msg = {
        "playing": playing,
        "static_parameters": {
            "time_per_step": time_per_step,
            "dt": dt,
            "mu": mu,
            "sigma": sigma,
            "T": T,
        },
        "assets": list(assets),
        "tau": T - time * dt,
        "gbm_paths": list(gbm_paths),
        "delta": list(delta),
        "price": list(price),
    }
    await websocket.send(json.dumps(msg))


clients = set()


async def handler(websocket):
    global \
        playing, \
        motion, \
        time, \
        gbm_paths, \
        delta, \
        price, \
        assets, \
        time_per_step, \
        dt, \
        mu, \
        sigma, \
        T
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
                motion = VectorizedGeometricBrownianMotion(size, 100.0, mu, sigma, dt)
                gbm_paths = collections.deque(
                    [{}] * 100,
                    maxlen=100,
                )
                delta = collections.deque([{}] * 100, maxlen=100)
                price = collections.deque([{}] * 100, maxlen=100)
                assets = collections.deque([{}] * 100, maxlen=100)
                time = 0
            else:
                print(f"""unknown incoming message {data.get("action")}""")
            await send_dump(websocket)
    finally:
        clients.remove(websocket)


async def periodic_sender():
    global time, delta
    while True:
        if playing:
            # modify some_data, e.g. take a step here
            time += 1
            motion.step()

            gbm_paths.append(
                {
                    "time": time,
                    "data": tf.reshape(tf.abs(motion.s), [-1]).numpy().tolist(),
                }
            )

            d = BlackScholes(100.0, sigma, T - time * dt, K, r)
            delta_step = d.calculate_delta_call()
            price_step = d.calculate_price_call()

            delta.append({"time": time, "data": delta_step.numpy().item()})
            price.append({"time": time, "data": price_step.numpy().item()})

            asset = Assets()
            asset.sell_price_call(1)
            if assets and isinstance(assets[-1], Assets):
                asset = assets[-1]
            assets.append(asset.get_dump(time))

            await asyncio.gather(*(send_dump(ws) for ws in clients))
        await asyncio.sleep(time_per_step)


async def main1():
    print("server started")
    asyncio.create_task(periodic_sender())
    async with websockets.serve(handler, "localhost", 65135):
        await asyncio.Future()


def main():
    asyncio.run(main1())
