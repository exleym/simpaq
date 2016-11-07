
import unittest
import datetime
from simpaq.assets.standard import Equity, Option
from simpaq.pricers import BlackScholesPricer, MCOptionPricer, LatticeOptionPricer


class TestMCOptionPricer(unittest.TestCase):

    def setUp(self):
        self.underlying = Equity(ticker='AAA', name='TestAAA', price=10, vol=0.25, div=0.)
        self.valuation_date = datetime.date.today()
        self.maturity = self.valuation_date + datetime.timedelta(days=365)
        self.call_eur = Option(ticker='AAA C12', name='TestOption', underlying=self.underlying, strike=12, rfr=0.01,
                               maturity=self.maturity, call=True, American=False)
        self.call_amer = Option(ticker='BBB C12', name='TestOption', underlying=self.underlying, strike=12, rfr=0.01,
                                maturity=self.maturity, call=True, American=True)

    def test_european_options(self):
        """ Lattice and MC return same price for European Call """
        bspricer = BlackScholesPricer()
        mcpricer = MCOptionPricer(m=500000, n=2)
        bsprice = self.call_eur.calc_price(bspricer)
        mcprice = self.call_eur.calc_price(mcpricer)
        self.assertAlmostEqual(bsprice, mcprice, 2)

    def test_american_options(self):
        """ Lattice and MC return same price for American Call """
        latticepricer = LatticeOptionPricer(n=252)
        mcpricer = MCOptionPricer(m=500000, n=252)
        lprice = self.call_amer.calc_price(latticepricer)
        mcprice = self.call_amer.calc_price(mcpricer)
        self.assertAlmostEqual(lprice, mcprice, 2)

if __name__ == '__main__':
    unittest.main()
