__author__ = 'exleym'

"""
    Numerical Pricers
    -----------------------
    LatticePricer
    FDPricer
    MCPricer
"""

class Pricer(object):
    def __init__(self):
        pass

    def price(asset, underlying, save=False):
        """ Header / layout for primary API to the Pricer class.
        :param asset: instance of Asset class or a derivative
        :param underlying: instance of Asset class or a derivative
        :param save: boolean to save calculated price
        """
        return None


class LatticePricer(Pricer):
    def __init__(self, n):
        super(LatticePricer, self).__init__()
        self.n = n
        
    def price(asset, underlying, save=False)
        tree = Tree(asset, 
