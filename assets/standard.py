__author__ = 'exleym'

from pandas.tseries.offsets import BDay
import pandas_datareader.data as web
import datetime
import numpy as np

class Asset(object):
    def __init__(self, ticker, name):
        self.ticker = ticker
        self.name = name
        self.price = None
        self.pricer = None
        self.features = dict()

    def add_feature(self, feature, feature_key=None):
        if not feature_key:
            feature_key = feature.code
        self.features[feature_key] = feature

    def set_price(self, price):
        self.price = price


class Equity(Asset):
    def __init__(self, ticker, name):
        super(Equity, self).__init__(ticker, name)
        self.vol = None
        self.dividend = None
        self.adv = None

    def __repr__(self):
        return "<Equity: %s>" % self.ticker

    def set_stock_data(self, source='yahoo', value_date=None, lookback=63):
        colmap = {'yahoo': 'Adj Close', 'google': 'Close'}
        if not value_date:
            value_date = datetime.datetime.today()
        lookback_date = value_date - lookback * BDay()
        px = web.DataReader(self.ticker, data_source=source, start=lookback_date, end=value_date)
        self.adv = px.loc[:, 'Volume'].mean()
        self.vol = (px.loc[:, colmap[source]] / px.loc[:, colmap[source]].shift(1) - 1).std() * np.sqrt(252)
        self.price = px.at[px.index.max(), 'Close']

    def set_vol(self, vol):
        self.vol = vol

    def set_dividend(self, div):
        self.div = div


class Bond(Asset):
    def __init__(self, ticker, name, underlying, coupon, maturity_date, frequency=None, coupon_dates=None):
        super(Bond, self).__init__(ticker, name)
        self.underlying = underlying
        self.coupon = coupon
        self.frequency = frequency
        self.coupon_dates = coupon_dates
        self.maturity_date = maturity_date

    def check_bond_terms(self):
        try:
            assert self.frequency or self.coupon_dates
        except AssertionError:
            raise AssertionError('Either frequency or coupon_dates must be defined')


class Derivative(Asset):
    def __init__(self, ticker, name, underlying, maturity_date=None):
        super(Derivative, self).__init__(ticker, name)
        self.underlying = underlying
        self.maturity_date = maturity_date
        self.rfr = 0.01 # TODO: this needs to be handled! can go get RFR or be provided by user but needs handled.

    def __repr__(self):
        return "<Derivative: %s>" % self.ticker

    def calc_price(self, pricer, greeks=False):
        return pricer.price(asset=self, underlying=self.underlying, rfr=self.rfr, greeks=greeks)


class Option(Derivative):
    def __init__(self, ticker, name, underlying, strike, maturity_date, call=True, American=True):
        super(Option, self).__init__(ticker, name, underlying, maturity_date)
        self.call = call
        self.strike = strike
        self.American = American

    def parity(self, price):
        if self.call:
            return max(0, price - self.strike)
        else:
            return max(0, self.strike - price)

    def __repr__(self):
        return "<Option: %s>" % self.ticker