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
time = 0
T = 2
initial_cost = 100.0

playing = False
motion = VectorizedGeometricBrownianMotion(size, initial_cost, mu, sigma, dt)
live_data = collections.deque([None] * 100, maxlen=100)
gbm_paths = []
delta = 0
price = 0

assets = Assets()


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
        "dynamic_parameters": {
            "tau": T - time * dt,
        },
        "live_data": list(live_data),
    }
    await websocket.send(json.dumps(msg))


clients = set()


async def handler(websocket):
    global \
        playing, \
        motion, \
        live_data, \
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
                motion = VectorizedGeometricBrownianMotion(
                    size, initial_cost, mu, sigma, dt
                )
                live_data = collections.deque([None] * 100, maxlen=100)
                gbm_paths = []
                delta = 0
                price = 0
                assets = Assets()
                time = 0
            else:
                print(f"""unknown incoming message {data.get("action")}""")
            await send_dump(websocket)
    finally:
        clients.remove(websocket)


async def periodic_sender():
    global time, delta, price
    while True:
        if playing and (T - time * dt >= 0):
            # modify some_data, e.g. take a step here
            time += 1
            motion.step()

            gbm_paths = tf.reshape(tf.abs(motion.s), [-1]).numpy().tolist()

            d = BlackScholes(100.0, sigma, T - time * dt, K, r)
            delta = d.calculate_delta_call().numpy().item()
            price = d.calculate_price_call().numpy().item()

            # if it's the first time, sell a call option
            if time == 1:
                assets.sell_price_call(price)

            assets.adjust_underlying_share(delta, gbm_paths[0])

            # if it's the last time, expire the option
            if (time - 1) * dt == T:
                assets.expire_option(initial_cost, gbm_paths[0])

            live_data.append(
                {
                    "time": time,
                    "gbm": list(gbm_paths),
                    "price": price,
                    "delta": delta,
                    "assets": assets.get_dump(time),
                }
            )

            await asyncio.gather(*(send_dump(ws) for ws in clients))
        await asyncio.sleep(time_per_step)


async def main1():
    print("server started")
    asyncio.create_task(periodic_sender())
    async with websockets.serve(handler, "localhost", 65135):
        await asyncio.Future()


def main():
    asyncio.run(main1())
