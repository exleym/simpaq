

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

from .numerical import LatticeOptionPricer, MCOptionPricer
from .analytic import BlackScholesPricer, DCF

