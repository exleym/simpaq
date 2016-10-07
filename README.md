# simpaq
> various valuation tools for financial derivatives

`simpaq` contains valuation tools for financial derivatives. Initial support is for Options, Warrants, and Convertible Bonds. The original idea for this tool came from the fragmented and proprietary nature of quantitative financial tools. In spite of the fact that these models are widely published, bordering on commoditized, it is difficult to find well-documented packages that provide flexible, extensible, and modular valuation tools for complex derivatives.

The module consists of several key components, each extensible from its base form, designed to work together to provide a flexible set of pricing tools that operate seamlessly with one another. That said, the bespoke nature of many financial derivatives calls for bespoke pricing models, so there will always be some need for the user to adapt models to fit the features embedded in certain derivatives.

The "key components" mentioned above consist of the following, each component will maintain a common API across the sub-classes:
 1. Assets - the basic building block of all financial securities, the `Asset` class has been extended to represent a variety of financial securities, from equity to convertible bonds.
 2. Pricers - `Pricers` are the methods that can be used to determine relationships between a derivative and its underlying assets. This component includes numerical and analytic solvers for valuing assets in a risk-neutral world.
 3. Features - These are the "embedded features," legal stipulations in the derivative contracts that alter the relationship between a derivative and its underlying asset.

Shown here is an example of the interaction of these components:

```python  
from simpaq.assets import Equity, ConvertibleBond
from simpaq.pricers import MCConvertPricer
from simpaq.features import SoftCall

intc = Equity(ticker='INTC')
intc.set_stock_info(source='yahoo')

intc_0_20190530 = ConvertibleBond(ticker='INTC 0 5/30/2019',
                                  coupon=0, 
                                  maturity='5/30/2019', 
                                  underlying=intc, 
                                  par=1000, 
                                  cr=50)
intc_0_20190530.add_feature(SoftCall(price=130, price_type='relative', trigger=(20, 30)))
intc_0_20190530.set_pricer(MCConvertPricer(m=10**6))
print intc_0_20190530.price(credit_spread=400, vol=35, dt=1/252., save=False)
```

This simple code would return a fair value and Greeks for the sample bond created above. The output is formatted as follows:

```
=======================================================================
    Fair Value Calculations for INTC 0 5/30/2019 Convertible Bond
    -----------------------------------------------
    Fair Value:     131.25      Delta:  0.75
    Gamma:          0.02        Theta:  0.01
    Vega:           0.21        Rho:    0.001
    -----------------------------------------------
    Valuation Date:	2016-10-5
    Versus Stock:	INTC
    Versus Price:	$45.55
=======================================================================
```

# Table of Contents

 1. [Summary](#summary)
 2. [Components](#components)
    A. [Assets](##assets) - Classes representing various types of financial securities.
    B. [Features](##features) - Classes representing non-standard features of derivatives.
    C. [Pricers](##pricers) - Actual implementation of the valuation models.
 3. [Examples](#examples)
 4. [WebService](#web-service)
 5. [SQLAlchemy Integration](#sqlalchemy)


# Summary


# Components
The valuation models contained in this package operate as linked components that
perform various aspects of the analysis. The components work together to separate 
work into logical groups based on their roles.

* `Assets` represent securities and are responsible for aggregating market data,
    storing it, and passing data to pricers.
* `Features` belong to a list-attribute of an `Asset` and serve as modifiers on
    the `Pricer` assigned to their parent asset.
* `Pricer`s are where the meat of the technical analysis lives, and serve as a means
    of calculating the fair value of derivatives.

The `Asset`-based classes represent the individual securities. 

# Examples

# Web Service
We have decided to host a running instance of these pricers on AWS and provide
access to these models through our API. See the [API Documentation](#) for more
details on interacting with the web service.

Access to the `simpaq` web service is free after registering for a token, 
subject to the following constraints:
1. We will not provide inputs or security terms, just models
2. Calls to value securities with resource-intensive `Pricer` models will 
    be throttled to keep us from burning though our budget.
3. This service is provided under the [MIT License](./LICENSE), and thus is 
    provided "as is", without warranty of any kind.

# SQLAlchemy
Additionally, there are SQLAlchemy classes that correspond to 
