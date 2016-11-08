# simpaq
> python-based valuation tools for financial derivatives

`simpaq` contains valuation tools for financial derivatives. Initialy conceived as an Open-Source pricing tool for 
 convertible bonds, support is for Options, Warrants, and Convertible Bonds. The original idea for this tool came from the fragmented and proprietary nature of quantitative financial tools. In spite of the fact that these models are widely published, bordering on commoditized, it is difficult to find well-documented packages that provide flexible, extensible, and modular valuation tools for complex derivatives.

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

equity = Equity(ticker='XYZ', name='Xylophone Group', price=10, vol=0.25, div=0)
cvt = ConvertibleBond(ticker='XYZ 0 5/30/2019',
                      coupon=0, 
                      maturity='5/30/2019', 
                      underlying=intc, 
                      par=1000, 
                      cr=50)
cvt.add_feature(SoftCall(price=130, price_type='relative', trigger=(20, 30)))
mcpricer = MCConvertPricer(m=10**6, n=500)
print cvt.calc_price(mcpricer, credit_spread=400, vol=35, dt=1/252., save=False, pretty=True)
```

Using the flag `pretty=False`, this simple code would return fair value and Greeks for the sample bond created above, 
formatted for human reading. By leaving `pretty` to its default value of `True`, the output can be returned as a tuple 
with value, greeks, and model parameters.

```
=======================================================================
    Fair Value Calculations for ABC 0 5/30/2019 Convertible Bond
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

### Assets  
The `Asset`-based classes represent the various securities. Securities - both derivatives and primary - are represented 
by subclasses of the `Asset` class. Each sub-class inherits its key features from the more generic classes, and contains 
a from the basic `Asset` class,  Starting with the most basic security type `Equity`, `Bond`, and `Derivative` we 
combine classes to create derivative securities (`Option`, `ConvertibleBond`, etc)  

Each asset has a list attribute called `Features`, which holds a list of `Feature` objects. These objects are discussed 
below, but the skinny is that they add functionality to base 

### Features  
Features are modifiers on Assets that operate on both the pricer methods and the asset methods to create altered 
behavior. For example, adding a `SoftCall` feature to a `ConvertibleBond` being priced with a `MonteCarlo` bond pricer 
will enforce early conversion on Convertible Bonds when the soft-call provisions have been met. These features 
handle the complex and unique features that require special model design. A comprehensive list of Features and their 
respective APIs can be found in the [Features](./documentation/features.md) page of this documentation.

### Pricers  
Long story short, pricers are the guts of this operation. Ranging from simple BlackScholes option pricers that can only 
handle a simple European option, to MonteCarlo simulations capable of pricing complex Options or ConvertibleBonds with 
path-dependent features. The following pricers are currently supported by this package: 
 * BlackScholesPricer  
 * BlackScholesMandyPricer  
 * LatticeOptionPricer  
 * FDOptionPricer  
 * MCOptionPricer  
These pricers (especially the MonteCarlo pricers) support a variety of assets, and should be passed into the 
`calc_price()` methods of each an asset. A list of assets and their supported pricers can be found in the 
[Assets](./documentation/assets.md) documentation.  


# Examples

# Web Service
We plan to eventually host a running instance of these pricers on AWS and provide
access to these models through our API. See the [API Documentation](#) for more
details on interacting with the web service. This is a "down-the-road" todo, though, and

Access to the `simpaq` web service is free after registering for a token, 
subject to the following constraints:
1. We will not provide inputs or security terms, just models
2. Calls to value securities with resource-intensive `Pricer` models will 
    be throttled to keep us from burning though our budget.
3. This service is provided under the [MIT License](./LICENSE), and thus is 
    provided "as is", without warranty of any kind.

# SQLAlchemy
Additionally, this package contains a set of SQLAlchemy classes that can be mapped to a relational database and used to 
are SQLAlchemy classes that correspond to 
