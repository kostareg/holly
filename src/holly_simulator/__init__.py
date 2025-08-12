import tensorflow as tf


# todo: look into adding more dimensions for path history
class VectorizedGeometricBrownianMotion(tf.Module):
    def __init__(self, n, s0, mu, sigma, dt):
        self.n = n
        self.s = tf.Variable(tf.fill(dims=(n), value=s0))
        self.mu = mu
        self.sigma = sigma
        self.dt = dt

    @tf.function
    def step(self):
        print("trace: made a vectorized step")
        Z = tf.random.normal(shape=tf.shape(self.s), mean=0, stddev=1)
        self.s.assign(
            self.s
            * tf.math.exp(
                (self.mu - 0.5 * self.sigma**2) * self.dt
                + self.sigma * tf.math.sqrt(self.dt) * Z
            )
        )
