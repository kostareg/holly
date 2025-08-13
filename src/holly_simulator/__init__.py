import tensorflow as tf


# todo: look into adding more dimensions for path history
class VectorizedGeometricBrownianMotion(tf.Module):
    """
    Geometric Brownian Motion calculator with vectorization for multiple paths.

    Calculates one single value of a Geometric Brownian Motion simulation based on the equation:

    s_t = s_(t-1) * e ^ ( ( mu - sigma^2 / 2 ) * dt + sigma * sqrt(dt) * Z )

    Where:
        * s is the price
        * t is the current time
        * dt is the change in time
        * mu is the annualized drift rate
        * sigma is the annualized volatility standard deviation
        * Z is a random number drawn from a standard normal distribution mean=0 stddev=1
    """

    def __init__(self, n, s0, mu, sigma, dt):
        self.n = n
        self.s = tf.Variable(tf.fill(dims=(n), value=s0))
        self.mu = mu
        self.sigma = sigma
        self.dt = dt

    @tf.function
    def step(self):
        """
        Make a step in the simulation.
        """
        Z = tf.random.normal(shape=tf.shape(self.s), mean=0, stddev=1)
        self.s.assign(
            self.s
            * tf.math.exp(
                (self.mu - 0.5 * self.sigma**2) * self.dt
                + self.sigma * tf.math.sqrt(self.dt) * Z
            )
        )


# todo: vectorize
class BlackScholes(tf.Module):
    """
    We set tau to the maximum between tau and 1e-12 to avoid division by zero.
    """

    def __init__(self, s_t, sigma, tau, K, r):
        self.s_t = s_t
        self.sigma = sigma
        self.tau = tf.maximum(tau, 1e-12)
        self.K = K
        self.r = r

    @staticmethod
    @tf.function
    def N(x):
        return 0.5 * (1.0 + tf.math.erf(x / tf.sqrt(2.0)))

    @tf.function
    def calculate_delta_call(self):
        print("Calculating bs delta call...")
        d_1 = (
            tf.math.log(self.s_t / self.K) + (self.r + 0.5 * self.sigma**2) * self.tau
        ) / (self.sigma * tf.sqrt(self.tau))
        return self.N(d_1)

    @tf.function
    def calculate_price_call(self):
        print("Calculating bs price call...")
        d_1 = (
            tf.math.log(self.s_t / self.K) + (self.r + 0.5 * self.sigma**2) * self.tau
        ) / (self.sigma * tf.sqrt(self.tau))
        d_2 = d_1 - self.sigma * tf.sqrt(self.tau)
        return self.s_t * self.calculate_delta_call() - self.K * tf.math.exp(
            -self.r * self.tau
        ) * self.N(d_2)
