
import datetime
import numpy as np
import scipy.stats as stats

from . import Pricer
from .numerical import DCF
from ..assets.standard import Option


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
        T = (asset.maturity - valuation_date).days / 365.
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
        return (1 / (vol * np.sqrt(T))) * (np.log(S / K) + (rfr + 0.5 * vol**2) * T)

    def d2(self, d1, vol, T):
        return d1 - vol * np.sqrt(T)


class BlackScholesMandyPricer(Pricer):
    """ Prices Mandatory convertible as a basket of two options and a fixed-income cash flow """
    def __init__(self):
        super(BlackScholesMandyPricer, self).__init__()

    def price(self, asset, underlying, rfr, spread=None, vol=None, greeks=False, save=False, valuation_date=None):
        if not spread:
            try:
                assert asset.spread
            except AssertionError:
                raise ValueError('Must pass spread argument of type float if Mandatory.spread is undefined')
            spread = asset.spread

        if not valuation_date:
            valuation_date = datetime.date.today()

        upside_option = Option('Upside', 'Mandy Upside Option',
                               underlying=underlying,
                               strike=asset.k2,
                               rfr=rfr,
                               maturity=asset.maturity,
                               call=True,
                               American=False)
        downside_option = Option('Downside', 'Mandy Downside Option',
                                 underlying=underlying,
                                 strike=asset.k1,
                                 maturity=asset.maturity,
                                 call=False,
                                 American=False)

        upside_price, upside_greeks = upside_option.calc_price(BlackScholesPricer, greeks=greeks)
        downside_price, downside_greeks = downside_option.calc_price(BlackScholesPricer, greeks=greeks)
        coupon_value = DCF().price(valuation_date, asset.coupons, asset.pay_dates, spread + rfr)
        greek = None
        if greeks:
            greek = {}
        return upside_price + downside_price + coupon_value + asset.par, greek
