__author__ = 'exley'

"""
    SimPack - Tree Package 
    --------------------------------
    Classes representing different types of trees / lattices
    - Simple Binomial Tree
    - Cox-Ross-Rubenstein Tree
    - Potentially a trinomial tree of some type
"""

# imports
import pandas as pd
import numpy as np
import math


class Tree(object):
    """ Tree class representing a lattice-type valuation model for derivatives """
    def __init__(self, asset, T, dt=1/252., rfr=None):
        self.asset = asset
        self.T = T
        self.rfr = rfr
        self.dt = dt
        self.num_nodes = int(np.floor(float(T) / float(dt)))
        self.u = np.exp(self.vol * np.sqrt(self.dt))
        self.d = 1 / self.u
        self.p = (np.exp(self.rfr * self.dt) - self.d) / (self.u - self.d)

    def initialize(self):
        self.lattice = np.zeros((self.num_nodes, self.num_nodes))
        self.lattice[0,0] = self.asset.price

        for i in range(1, self.num_nodes):
            for j in range(i+1):
                if j == 0:
                    self.lattice[j, i] = self.lattice[j, i-1] * self.u
                else:
                    self.lattice[j, i] = self.lattice[j-1, i-1] * self.d
   
    def show_tree(self):
        print self.lattice

