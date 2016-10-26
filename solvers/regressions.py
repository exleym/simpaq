
import statsmodels.api as sm
import numpy as np


class LSM(object):
    def __init__(self, lambdas):
        self.lambdas = lambdas

    def calc(self, y, x):
        X = np.zeros((len(x), len(self.lambdas)))
        for i in range(0, len(self.lambdas)):
            X[:, i] = self.lambdas[i](x)

        ols = sm.OLS(y, sm.add_constant(X, prepend=False)).fit()
        return ols.params
