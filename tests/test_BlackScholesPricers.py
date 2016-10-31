
import unittest
import datetime
from simpaq.assets.standard import Equity, Option
from simpaq.pricers import BlackScholesPricer, DCF


class TestBlackScholesOptionPricer(unittest.TestCase):

    def setUp(self):
        self.underlying = Equity(ticker='AAA', name='AAA Common', price=10, vol=0.25, div=0)
        self.valuation_date = datetime.date.today()
        self.maturity = self.valuation_date + datetime.timedelta(days=365)
        self.call = Option('AAA C12', 'CallOption', self.underlying, 12, 0.01, self.maturity, call=True, American=False)
        self.put = Option('AAA P12', 'PutOption', self.underlying, 12, 0.01, self.maturity, call=False, American=False)
        self.american = Option('AAA C12', 'AmCall', self.underlying, 12, 0.01, self.maturity, call=True, American=True)
        self.pricer = BlackScholesPricer()

    def test_underlying(self):
        """ Underlying asset's features have been set correctly via initialization """
        self.assertEqual(self.underlying.price, 10.)
        self.assertEqual(self.underlying.vol, 0.25)
        self.assertEqual(self.underlying.div, 0.)

    def test_CallPriceType(self):
        """ BlackScholesPricer returns a float for a European call option """
        self.assertTrue(type(self.call.calc_price(self.pricer))==float)

    def test_PutPriceType(self):
        """ BlackScholesPricer returns a float for a European put option """
        self.assertTrue(type(self.put.calc_price(self.pricer))==float)

    def test_AmericanFail(self):
        """ BlackScholesPricer raises a TypeError for an American option """
        with self.assertRaises(TypeError):
            self.american.calc_price(self.pricer)

    @unittest.skip("Not yet implemented")
    def test_BlackScholes_greeks(self):
        """ BlackScholesPricer returns tuple of correct types for option greeks """
        #TODO: Test greeks as correct length tuple of floats
        pass

    def test_PutCallParity(self):
        """ Put-Call Parity holds for a basket of (+1 Call, -1 Put) = Forward contract """
        parity = self.underlying.price - DCF().price(self.valuation_date, [self.call.strike], [self.maturity], 0.01)
        synthetic = self.call.calc_price(self.pricer)-self.put.calc_price(self.pricer)
        self.assertAlmostEqual(parity, synthetic, 2)
