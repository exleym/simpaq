__author__ = 'exleym'

class Asset(object):
    def __init__(self, ticker, name):
        self.ticker = ticker
        self.name = name
        self.price = None

    def set_price(self, price):
        self.price = price

    def price(self, Pricer=None):
        if not Pricer:
            return None
        else:
            return Pricer.get_price(asset=self)

class Equity(Asset):
    def __init__(self, ticker, name):
        super(Equity, self).__init__(ticker, name)
        self.vol = None
        self.dividend = None

    def __repr__(self):
        return "<Equity: %s>" % self.ticker

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

    def check_bond_terms():
        try:
            assert self.frequency or self.coupon_dates
        except AssertionError:
            raise AssertionError('Either frequency or coupon_dates must be defined')


class Derivative(Asset):
    def __init__(self, ticker, name, underlying, maturity_date=None):
        super(Derivative, self).__init__(ticker, name)
        self.underlying = underlying
        self.maturity_date = maturity_date

    def __repr__(self):
        return "<Derivative: %s>" % self.ticker


class Option(Derivative):
    def __init__(self, ticker, name, underlying, strike, maturity_date, call=True):
        super(Option, self).__init__(ticker, name, underlying, maturity_date)
        self.call = call

    def parity():
        if call:
            return max(0, underlying.price - strike)
        else:
            return max(0, strike - underlying.price)

    def __repr__(self):
        return "<Option: %s>" % self.ticker


if __name__ == '__main__':
    import datetime
    ibm = Equity('IBM', 'Intl Bsns Mchnz')
    print ibm
    
    ibm_test_opt = Option('IBM C100 12/16/2016', 'Dec 16 Call on IBM @ $100', underlying=ibm, strike=100, maturity_date=datetime.date(2016, 12, 16), call=True)
    print ibm_test_opt
