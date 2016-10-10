__author__ = 'exleym'

"""
    Numerical Pricers
    -----------------------
    LatticePricer
    FDPricer
    MCPricer
"""
import datetime
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
        value_tree = tree.backpropagate(asset)
        if greeks:
            return (round(value_tree[0,0], 3), tree.greeks(asset))
        return round(value_tree[0,0], 3)

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
