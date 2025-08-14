import tensorflow as tf


# todo: look into adding more dimensions for path history
class VectorizedGeometricBrownianMotion(tf.Module):
    """
    Geometric Brownian Motion calculator with vectorization for multiple paths.

    Calculates a Geometric Brownian Motion simulation based on the equation:

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


class BlackScholes(tf.Module):
    """
    Black-Scholes model with vectorization for multiple paths.

    Calculates greeks with a Black-Scholes model based on the equations:

    d_1 = (ln (s_t / K) + (r + sigma^2 / 2) * tau) / (sigma * sqrt(tau))
    d_2 = d_1 - sigma * sqrt(tau)
    delta = N(d_1)
    price = s_t * delta - K * e ^ (-r * tau) * N(d_2)

    Where:
        * s is the price
        * t is the current time
        * sigma is the annualized volatility standard deviation
        * r is the risk-free interest rate
        * tau is the time to option maturity
        * K is the strike price
        * N is the cumulative distribution function of the standard normal distribution

    Note: we set tau to the maximum between tau and 1e-12 to avoid division by zero.
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


class Assets:
    underlying = 0
    option = 0
    cash = 0

    def sell_price_call(self, cost):
        """Write a price call that is cashed immediately into our account."""
        self.cash += cost
        self.option += 1

    def adjust_underlying_share(self, total_amount, unit_cost):
        """Own (total) amount of underlying means buying or selling until we get to total."""
        change = total_amount - self.underlying
        total_cost = change * unit_cost
        self.cash -= total_cost
        self.underlying = total_amount

    def expire_option(self, K, current_underlying_cost):
        """Option holder sells if the current cost is larger than the initial cost."""
        self.cash -= max(current_underlying_cost - K, 0.0)
        self.option -= 1
        self.cash += self.underlying * current_underlying_cost
        # todo: include liquidation cost
        self.underlying = 0

    def get_dump(self, time):
        return {
            "underlying": self.underlying,
            "option": self.option,
            "cash": self.cash,
        }

    @staticmethod
    def get_var5(all_assets):
        n = len(all_assets)
        sorted_cash = sorted(r.cash for r in all_assets)
        var5_index = int(0.05 * n)
        return sorted_cash[var5_index]

    @staticmethod
    def get_cvar5(all_assets):
        n = len(all_assets)
        sorted_cash = sorted(r.cash for r in all_assets)
        var5_index = int(0.05 * n)
        return sum(sorted_cash[:var5_index+1]) / (var5_index+1)
