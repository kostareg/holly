import asyncio
import json
import websockets
import collections
import copy
import tensorflow as tf

from holly_simulator import VectorizedGeometricBrownianMotion, BlackScholes, Assets

time_per_step = 0.01
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
delta = []
price = []

all_assets = copy.deepcopy([Assets() for _ in range(100)])

def get_average_pnl():
    average, idx = 0, 0
    while idx < 15:
        average += all_assets[idx].cash
        idx += 1
    average /= 15
    return average


async def send_dump(websocket):
    tau = T - time * dt
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
            "tau": tau,
        },
        "final_parameters": None if tau > 0 else {
            "pnl": get_average_pnl(),
            "var5": Assets.get_var5(all_assets),
            "cvar5": Assets.get_cvar5(all_assets),
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
        all_assets, \
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
                delta = []
                price = []
                all_assets = copy.deepcopy([Assets() for _ in range(100)])
                time = 0
            else:
                print(f"""unknown incoming message {data.get("action")}""")
            await send_dump(websocket)
    finally:
        clients.remove(websocket)


async def periodic_sender():
    global time, delta, price, gbm_paths
    while True:
        if playing and (T - time * dt >= 0):
            # modify some_data, e.g. take a step here
            time += 1
            motion.step()

            gbm_paths = tf.reshape(tf.abs(motion.s), [-1])

            d = BlackScholes(gbm_paths, sigma, T - time * dt, K, r)
            delta = d.calculate_delta_call()
            price = d.calculate_price_call()

            gbm_paths = gbm_paths.numpy().tolist()
            price = price.numpy().tolist()
            delta = delta.numpy().tolist()

            # if it's the first time, sell a call option
            if time == 1:
                for i, assets in enumerate(all_assets):
                    assets.sell_price_call(price[i])

            print(f"going in: {all_assets[0].cash} option is valued at {price[0]}")

            for i, assets in enumerate(all_assets):
                assets.adjust_underlying_share(delta[i], gbm_paths[i])

            # if it's the last time, expire the option
            if (time - 1) * dt == T:
                for i, assets in enumerate(all_assets):
                    assets.expire_option(K, gbm_paths[i])

            live_data.append(
                {
                    "time": time,
                    "gbm": list(gbm_paths),
                    "price": list(price),
                    "delta": list(delta),
                    "assets": {
                        "underlying": all_assets[0].underlying,
                        "option": all_assets[0].option,
                        "cash": get_average_pnl(),
                    },
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
