import math
import random


class GeometricBrownianMotion:
    def __init__(self, s0, mu, sigma, dt):
        self.s = s0
        self.mu = mu
        self.sigma = sigma
        self.dt = dt

    def step(self):
        print("trace: made a step")
        self.s *= math.exp(
            (self.mu - (self.sigma**2) / 2) * self.dt
            + self.sigma * math.sqrt(self.dt) * random.gauss(0, 1)
        )
