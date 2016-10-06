# simpaq
> various valuation tools for financial derivatives

`simpaq` contains valuation tools for financial derivatives. Initial support is for Options, Warrants, and Convertible Bonds. The original idea for this tool came from the fragmented and proprietary nature of quantitative financial tools. In spite of the fact that these models are widely published, bordering on commoditized, it is difficult to find well-documented packages that provide flexible, extensible, and modular valuation tools for complex derivatives.

The module consists of several key components, each extensible from its base form, designed to work together to provide a flexible set of pricing tools that operate seamlessly with one another. That said, the bespoke nature of many financial derivatives calls for bespoke pricing models, so there will always be some need for the user to adapt models to fit the features embedded in certain derivatives.

The "key components" mentioned above consist of the following, each component will maintain a common API across the sub-classes:
 1. Assets - the basic building block of all financial securities, the `Asset` class has been extended to represent a variety of financial securities, from equity to convertible bonds.
 2. Pricers - `Pricers` are the methods that can be used to determine relationships between a derivative and its underlying assets. This component includes numerical and analytic solvers for valuing assets in a risk-neutral world.
 3. Features - These are the "embedded features," legal stipulations in the derivative contracts that alter the relationship between a derivative and its underlying asset.

Shown here is an example of each component working together.

```python  
from simpaq.assets import Equity, ConvertibleBond
from simpaq.pricers import MCConvertPricer
from simpaq.features import SoftCall

intc = Equity(ticker='INTC')
intc.get_stock_info('yahoo')

intc_0_20190530 = ConvertibleBond(ticker='INTC 0 5/30/2019', coupon=0, maturity='5/30/2019', underlying=intc, par=1000, cr=50)
intc_0_20190530.add_feature(SoftCall(price=130, price_type='relative', trigger=(20, 30)))
intc_0_20190530.add_pricer(MCConvertPricer(m=10**6))
print intc_0_20190530.price(credit_spread=400, vol=35, dt=1/252., save=False)
```

This simple code would return a fair value and Greeks for the sample bond created above. The output is formatted as follows:

```
=======================================================================

    Fair Value Calculations for INTC 0 5/30/2019 Convertible Bond
    Valuation Date:	2016-10-5
    Versus Stock:	INTC
    Versus Price:	$45.55

=======================================================================

    Fair Value:		131.25		Delta:	0.75
    Gamma:		0.02		Theta:  0.01
    Vega:		0.21		Rho:	0.001

=======================================================================    
```


Additionally, there are SQLAlchemy classes that correspond to 
