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
from ..processes import Tree

class Pricer(object):
    def __init__(self):
        pass

    def price(self, asset, underlying, greeks, save=False):
        """ Header / layout for primary API to the Pricer class.
        :param asset: instance of Asset class or a derivative
        :param underlying: instance of Asset class or a derivative
        :param save: boolean to save calculated price
        :return: price or (price & greeks)
        """
        return None

    def __repr__(self):
        return "<Pricer>"


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
        T = (asset.maturity_date - valuation_date).days / 365.
        tree = Tree(underlying, T=T,num_nodes=self.n, rfr=rfr)
        tree.initialize()
        value_tree = self.backpropagate(asset, tree)
        if greeks:
            return (round(value_tree[0,0], 3), self.greeks(asset))
        return round(value_tree[0,0], 3)

    def backpropagate(self, asset, tree):
        value_tree = np.zeros(tree.lattice.shape)
        for ix in range(0, tree.lattice.shape[0]):
            value_tree[ix, -1] = asset.parity(tree.lattice[ix, -1])
        for n in range(tree.lattice.shape[1]-2, -1, -1):
            for m in range(n, -1, -1):
                value_tree[m, n] = tree._disc(value_tree[m, n+1] * tree.p + value_tree[m+1, n+1] * (1 - tree.p), per=1)
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
    def __init__(self, n):
        super(MCOptionPricer, self).__init__()
        self.n = n

    def price(self, asset, underlying, greeks=True, save=False):
        pass


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
            return (round(value_tree[0,0], 3), self.greeks(asset))
        return round(value_tree[0,0], 3)

    def backpropagate(self, asset, tree):
        value_tree = np.zeros(tree.lattice.shape)
        #TODO: does final coupon usually pay on maturity date at the same time conversion happens?
        #TODO (cont): if so, this needs to handle final coupon @ last node.
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
