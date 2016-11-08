__author__ = 'exleym'

"""
    Numerical Pricers
    -----------------------
    LatticePricer
    FDPricer
    MCPricer
"""
import datetime
import numpy as np

from . import Pricer
from ..processes import Tree, MonteCarlo
from ..solvers import LSM


class DCF(object):
    def __init__(self):
        pass

    def price(self, value_date, cash_flows, pay_dates, discount_rate):
        price = 0
        for cf, dt in zip(cash_flows, pay_dates):
            T = (dt - value_date).days / 365.25
            price += self.discount(cf, T, discount_rate)
        return price

    @staticmethod
    def discount(cf, T, discount_rate):
        return cf * (1 / (1 + discount_rate))**T


class LatticeOptionPricer(Pricer):
    def __init__(self, n):
        super(LatticeOptionPricer, self).__init__()
        self.n = n
        
    def price(self, asset, underlying, rfr, greeks=False, save=False, valuation_date=None):
        """ calculate the price of an option using a binomial lattice to calculate early exercises
        :param asset: derivative asset to be priced with lattice model
        :param underlying: underlying asset upon which the derivative is based
        :param rfr: currently a float. this needs to become a class that can handle forward curves, get data, etc
        :param greeks: boolean where True returns price and the greeks and false returns price.
        :param save: to be implemented later; boolean where True saves to a database.
        :param valuation_date: optional valuation_date override
        :return: price or (price & greeks)
        """
        if not valuation_date: valuation_date = datetime.date.today()
        T = (asset.maturity - valuation_date).days / 365.
        tree = Tree(underlying, T=T,num_nodes=self.n, rfr=rfr)
        tree.initialize()
        value_tree = self.backpropagate(asset, tree)
        if greeks:
            return round(value_tree[0, 0], 3), self.greeks(asset)
        return round(value_tree[0, 0], 3)

    @staticmethod
    def backpropagate(asset, tree):
        value_tree = np.zeros(tree.lattice.shape)
        for ix in range(0, tree.lattice.shape[0]):
            value_tree[ix, -1] = asset.parity(tree.lattice[ix, -1])
        for n in range(tree.lattice.shape[1]-2, -1, -1):
            for m in range(n, -1, -1):
                value_tree[m, n] = tree.disc(value_tree[m, n+1] * tree.p + value_tree[m+1, n+1] * (1 - tree.p), per=1)
                if asset.American:
                    value_tree[m, n] = max(value_tree[m, n], asset.parity(tree.lattice[m, n]))
        return value_tree

    def greeks(self, asset):
        return None

    def __repr__(self):
        return "<LatticeOptionPricer: N=%d>" % self.n


class FDOptionPricer(Pricer):
    def __init__(self, n):
        super(FDOptionPricer, self).__init__()
        self.n = n

    def price(self, asset, underlying, greeks=True, save=False):
        """ calculate the price of an option using a finite-difference matrix to calculate early exercises
        :param asset: derivative asset to be priced with finite-difference model
        :param underlying: underlying asset upon which the derivative is based
        :param rfr: currently a float. this needs to become a class that can handle forward curves, get data, etc
        :param greeks: boolean where True returns price and the greeks and false returns price.
        :param save: to be implemented later; boolean where True saves to a database.
        :param valuation_date: optional valuation_date override
        :return: price or (price & greeks)
        """
        pass

    def __repr__(self):
        return "<FDOptionPricer: N=%d>" % self.n


class MCOptionPricer(Pricer):
    """ Monte Carlo Simulation for option pricing. Based on Longstaff-Schwartz 2001 """
    def __init__(self, m, n=None, dt=None):
        super(MCOptionPricer, self).__init__()
        self.m = m
        try:
            assert bool(dt) != bool(n)
        except AssertionError:
            raise KeyError('One and only one of num_steps or dt must be provided in initialization')
        self.n = n
        self.dt = dt

    def price(self, asset, underlying, rfr, greeks=True, save=False, valuation_date=None):
        """ Calculate price subject to early exercise boundary (for American options, only) - This model uses a
        Longstaff-Schwartz-style least-squares regression model to estimate continuation value @ points in which
        early-exercise is allowed.
        :param asset: 
        :param underlying:
        :param rfr:
        :param greeks:
        :param save:
        :param valuation_date:
        :return:
        """
        if not valuation_date: valuation_date = datetime.date.today()
        T = (asset.maturity - valuation_date).days / 365.
        if not self.dt:
            dt = float(T) / self.n
            n = self.n
        else:
            n = int(round(T / self.dt))
            dt = self.dt
        process = MonteCarlo(underlying, T, rfr, self.m, n)
        paths = process.initialize()
        return self.backpropagate(asset, paths, rfr, n, dt)

    def backpropagate(self, asset, paths, rfr, n, dt):
        """
            Uses the least-squares method described in Longstaff-Schwartz [2001] to determine early exercise conditions
            for in-the-money paths of the Monte Carlo process.
        :param asset: Asset instance (should be a Derivative)
        :param paths: integer representing m paths
        :param rfr: risk-free rate
        :param n: number of steps being simulated
        :param dt: duration of a "time-step"
        """
        parity = np.zeros(paths.shape)
        value = np.zeros(paths.shape)
        parity[:, -1] = asset.parity(paths[:, -1])
        value[:, -1] = parity[:, -1]
        lsm = LSM([lambda x: x, lambda x: x**2, lambda x: x**3])

        for col in range(paths.shape[1]-2, -1, -1):
            if not asset.American:
                return round(self._disc(parity[:,-1], dt, per=self.n, rate=rfr).mean(),3)
            else:
                parity[:, col] = asset.parity(paths[:, col])
                itm = parity[:, col] > 0
                y = parity[itm, -1]
                x = parity[itm, col]
                params = lsm.calc(y, x)
                y_hat = np.ones(parity[:,0].shape) * params[-1]
                for ix in range(len(params)-2, -1, -1):
                    y_hat += params[ix] * parity[:,col]
                value[:,0] = self._disc(parity[:,-1], dt, per=1, rate=rfr)
                value[itm, 0] = np.maximum(self._disc(y_hat[itm], dt, per=1,rate=rfr), parity[itm, col])
                return round(value[:,0].mean(),3)

    @staticmethod
    def _disc(value_array, dt, per=1, rate=0):
        """ discounts an array of numbers back by a time period or array of time periods at the provided rate
        :param value_array: numpy array of values to be discounted
        :param dt: time step (in years - one day = 1/252 or 0.004)
        :param per: number of time steps over which the discounting applied (int or array of ints - defaults to 1)
        :param rate: discount rate to use in the discounting (float - defaults to 0, but you shouldn't use this)
        :return: array of discounted values
        """
        disc = (1+rate)**(dt * per)
        return value_array / disc


class LatticeMandyPricer(Pricer):
    def __init__(self, n):
        super(LatticeMandyPricer, self).__init__()
        self.n = n

    def price(self, asset, underlying, rfr, greeks=False, save=False, valuation_date=None):
        """ calculate the price of an option using a binomial lattice to calculate early exercises
        :param asset: derivative asset to be priced with lattice model
        :param underlying: underlying asset upon which the derivative is based
        :param rfr: currently a float. this needs to become a class that can handle forward curves, get data, etc
        :param greeks: boolean where True returns price and the greeks and false returns price.
        :param save: to be implemented later; boolean where True saves to a database.
        :param valuation_date: optional valuation_date override
        :return: price or (price & greeks)
        """
        if not valuation_date: valuation_date = datetime.date.today()
        T = (asset.maturity_date - valuation_date).days / 365.
        tree = Tree(underlying, T=T,num_nodes=self.n, rfr=rfr)
        tree.initialize()
        value_tree = self.backpropagate(asset, tree)
        if greeks:
            return round(value_tree[0, 0], 3), self.greeks(asset)
        return round(value_tree[0, 0], 3)

    def backpropagate(self, asset, tree):
        value_tree = np.zeros(tree.lattice.shape)
        # TODO: does final coupon usually pay on maturity date at the same time conversion happens?
        # TODO (cont): if so, this needs to handle final coupon @ last node.
        for ix in range(0, tree.lattice.shape[0]):
            value_tree[ix, -1] = asset.parity(tree.lattice[ix, -1])

        # this is currently calculating the conversion value @ each node and ignoring coupon payment
        # TODO: need to incorporate coupon value in the value nodes somehow. perhaps each node should be a tuple
        # Issues:
        #   1)  If you just do conversion values in the value tree, you miss out on incorporating future coupons @ each
        #       decision node.
        #   2)  If you try to incorporate both future coupons and conversion value in same decision node, you have to
        #       blend the discount rate based on how much value comes from coupon vs equity conversion. At least par
        #       value isn't part of the mix in mandies. Converts will be worse.
        # Each node is max(conversion value, prob-weighted pv of next two value nodes + any coupon between them)
        #   -   IF no future nodes contain a coupon payment, the next nodes should be discounted @ RFR.
        #   -   HOWEVER, IF some future nodes receive coupons, that portion of value should be discounted @ asset yield.
        for n in range(tree.lattice.shape[1]-2, -1, -1):
            for m in range(n, -1, -1):
                value_tree[m, n] = tree._disc(value_tree[m, n+1] * tree.p + value_tree[m+1, n+1] * (1 - tree.p), per=1)
                if asset.American:
                    value_tree[m, n] = max(value_tree[m, n], asset.ee_parity(tree.lattice[m, n]))
        return value_tree

    def greeks(self, asset):
        return None

    def __repr__(self):
        return "<LatticeMandyPricer: N=%d>" % self.n
