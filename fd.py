__author__ = 'exley'

"""
    Finite Difference Models included in the SimPack library
    -----------------------------------------------------------
    Exley
    9/29/2016

    Classes representing different finite-difference approximations to
    differential equation solutions for pricing option-like securities.
"""

import numpy as np


class FiniteDifference(object):
    def __init__(self, Asset, T, dt=1/252., s0=None, vol=None, rfr=None):
        self.Asset = Asset
        self.T = T
        self.dt = dt
        self.num_nodes = int(np.floor(float(T) / float(dt)))
        self.vol = vol
        self.rfr = rfr

    # TODO: Figure out how this is done in a properly calibrated FD model.
    def initialize(self, M=100, N=None, dS=0.05):
        """ Initialize creates a rectangular lattice of M*N nodes, where rows represent
            a stock level and columns represent a point in time.
            :param M:   <int>   Number of rows in lattice
            :param N:   <int>   Number of columns in lattice, will default to T / dt
            :param dS:  <float> Size of stock jump between nodes as % of stock price.
        """
        if not N:
            N = self.num_nodes
        self.lattice = np.zeros((M, N))
        self.prices = None

        # TODO: create array of stock prices and array of future dates
        # TODO: define boundary conditions for lattice
        # TODO: populate interior nodes
        
        



