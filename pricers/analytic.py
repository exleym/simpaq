
import datetime
import numpy as np
import scipy.stats as stats
from .numerical import Pricer

class BlackScholesPricer(Pricer):
    def __init__(self):
        super(BlackScholesPricer, self).__init__()

    def price(self, asset, underlying, rfr, vol=None, greeks=False, save=False, valuation_date=None):
        """
        :param asset: derivative asset to be priced with lattice model
        :param underlying: underlying asset upon which the derivative is based
        :param rfr: currently a float. this needs to become a class that can handle forward curves, get data, etc
        :param greeks: boolean where True returns price and the greeks and false returns price.
        :param save: to be implemented later; boolean where True saves to a database.
        :param valuation_date: optional valuation_date override
        :return:
        """
        # Check that asset is European
        if asset.American: raise TypeError('You cannot use Black-Scholes Pricers on American Options')

        # Set vol and valuation_date if they are not defined
        if not vol: vol = underlying.vol
        if not valuation_date: valuation_date = datetime.date.today()

        # Calculate time to maturity (T), d1, and d2
        T = (asset.maturity_date - valuation_date).days / 365.
        d1 = self.d1(underlying.price, asset.strike, T, rfr, vol)
        d2 = self.d2(d1, vol, T)

        # Return Call or Put Option price
        if asset.call:
            return round(stats.norm.cdf(d1) * underlying.price -
                         stats.norm.cdf(d2) * asset.strike * np.exp(-rfr * T), 3)
        else:
            return round(stats.norm.cdf(-d2) * asset.strike * np.exp(-rfr * T) -
                         stats.norm.cdf(-d1) * underlying.price, 3)

    def d1(self, S, K, T, rfr, vol):
        return (1 / vol * np.sqrt(T)) * (np.log(S / K) + (rfr + 0.5 * vol**2) * T)

    def d2(self, d1, vol, T):
        return d1 - vol * np.sqrt(T)
