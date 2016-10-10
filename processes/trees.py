
import numpy as np

class Tree(object):
    def __init__(self, asset, T, rfr, num_nodes=None, dt=None):
        """ Trees are the building block for Lattice-based pricing models
        :param asset: The underlying asset whose process is being simulated
        :param T: Time to maturity of the derivative
        :param rfr: Risk-free rate (either a term-structure or a forward curve)
        :param num_nodes: Optional (xor with dt) number of nodes to fit between now and T
        :param dt: Optional (xor with num_nodoes) time-step between nodes
        :return:
        """
        self.asset = asset
        self.T = T
        self.rfr = rfr

        try:
            assert bool(dt) != bool(num_nodes)
        except AssertionError:
            raise KeyError('One and only one of num_nodes or dt must be provided in initialization')

        if not dt:
            dt = float(T) / num_nodes
        else:
            num_nodes = int(round(T / dt))
        self.num_nodes = num_nodes
        self.dt = dt
        self.u = np.exp(asset.vol * np.sqrt(self.dt))
        self.d = 1 / self.u
        self.p = (np.exp(self.rfr * self.dt) - self.d) / (self.u - self.d)

    def initialize(self):
        self.lattice = np.zeros((self.num_nodes, self.num_nodes))
        self.lattice[0,0] = self.asset.price

        for i in range(1, self.num_nodes):
            for j in range(i+1):
                if j == 0:
                    self.lattice[j, i] = self.lattice[j, i-1] * self.u
                else:
                    self.lattice[j, i] = self.lattice[j-1, i-1] * self.d

    def backpropagate(self, asset):
        value_tree = np.zeros(self.lattice.shape)
        for ix in range(0, self.lattice.shape[0]):
            value_tree[ix, -1] = asset.parity(self.lattice[ix, -1])
        for n in range(self.lattice.shape[1]-2, -1, -1):
            for m in range(n, -1, -1):
                value_tree[m, n] = self._disc(value_tree[m, n+1] * self.p + value_tree[m+1, n+1] * (1 - self.p), per=1)
                if asset.American:
                    value_tree[m, n] = max(value_tree[m, n], asset.parity(self.lattice[m, n]))
        return value_tree

    def greeks(self, asset):
        return None

    def _disc(self, value, per=1):
        return value / (1 + self.rfr)**(self.dt * per)