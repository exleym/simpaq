
import unittest
import datetime
from simpaq.assets.standard import Equity, Option
from simpaq.pricers import BlackScholesPricer, MCOptionPricer, LatticeOptionPricer


class TestMCOptionPricer(unittest.TestCase):

    def test_european_options(self):
        underlying = Equity(ticker='AAA', name='TestAAA')
        underlying.set_price(10)
        underlying.set_vol(0.25)
        underlying.set_dividend(0)
        valuation_date = datetime.date.today()
        maturity = valuation_date + datetime.timedelta(days=365)
        option = Option(ticker='AAA C12', name='TestOption', underlying=underlying, strike=12, maturity_date=maturity,
                        call=True, American=False)
        bspricer = BlackScholesPricer()
        mcpricer = MCOptionPricer(m=500000, n=252)

        bsprice = option.calc_price(bspricer)
        mcprice = option.calc_price(mcpricer)

        self.assertAlmostEqual(bsprice, mcprice, 2)

    def test_american_options(self):
        underlying = Equity(ticker='BBB', name='TestBBB')
        underlying.set_price(10)
        underlying.set_vol(0.25)
        underlying.set_dividend(0)
        valuation_date = datetime.date.today()
        maturity = valuation_date + datetime.timedelta(days=365)
        option = Option(ticker='BBB C12', name='TestOption', underlying=underlying, strike=12, maturity_date=maturity,
                        call=True, American=True)
        latticepricer = LatticeOptionPricer(n=252)
        mcpricer = MCOptionPricer(m=500000, n=252)
        lprice = option.calc_price(latticepricer)
        mcprice = option.calc_price(mcpricer)

        self.assertAlmostEqual(lprice, mcprice, 2)

if __name__ == '__main__':
    unittest.main()
