
import numpy as np
import matplotlib.pyplot as plt

class MonteCarlo(object):
    """ Monte Carlo simulation - this class generates an m*n matrix following a GBM process """
    def __init__(self, asset, T, rfr, num_paths, num_steps=None, dt=None, antithetic=False):
        """ MonteCarlo simulations are the building block of path-dependent pricers and are based on a GBM stochastic
        process.
        :param asset: The underlying asset whose process is being simulated
        :param T: Time to maturity of the derivative
        :param rfr: Risk-free rate (either a term-structure or a forward curve)
        :param vol: Volatility of the underlying asset
        :param num_paths: number of paths to simulate
        :param num_steps: Optional (xor with dt) number of nodes to fit between now and T
        :param dt: Optional (xor with num_nodes) time-step between nodes
        :param antithetic: value of True pairs each path with its antithetic path improving convergence
        :return: None
        """
        self.asset = asset
        self.T = T
        self.num_paths = num_paths
        self.rfr = rfr
        self.antithetic = antithetic

        try:
            assert bool(dt) != bool(num_steps)
        except AssertionError:
            raise KeyError('One and only one of num_steps or dt must be provided in initialization')

        if not dt:
            dt = float(T) / num_steps
        else:
            num_steps = int(round(T / dt))
        self.num_steps = num_steps
        self.dt = dt

    def initialize(self):
        randoms = np.random.randn(self.num_paths, self.num_steps)
        if self.antithetic:
            randoms = np.vstack([randoms, -1*randoms])
        q = self.asset.div
        sims = np.exp((self.rfr - q - 0.5 * self.asset.vol**2)*self.dt + self.asset.vol*np.sqrt(self.dt)*randoms)
        sims = self.asset.price * np.cumprod(sims, axis=1)

        # rng = range(0, sims.shape[0])
        # xval = range(0, sims.shape[1])
        # for r in rng:
        #     plt.plot(xval, sims[r, :])
        # plt.show()

        return sims
