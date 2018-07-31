#!env/bin python
# Marek Slipski
# 20170629

import pandas as pd
import numpy as np


################################################################################
# Functions to compute temperature and pressure from density profiles
# ***** add a tempeature parser that takes species, snowden args, etc -
# then I think the function arguments can be removed and those parsed values
# will be global...
################################################################################

#Some constants
g = 3.81 #m/s^2 surface gravity
M_Mars =  0.64171e+24 #kg
R_Mars = 3396.2e+3 #m
Grav = 6.67408e-11 #m^3 kg^-1 s^-2
amu = 1.660539040e-27 #kg
kboltz = 1.38064852e-23 #J/K


################################################################################
# Static Stability functions
################################################################################
def cp(T):
    '''
    Calculate specific heat in Mars' upper atmosphere via
    Magalhaes et al. 1999.
    cp in J/(kg K)
    '''
    return 0.0033 * T**2 -  0.2716 * T + 656.3 #from Magalhaes et al. 1999

def static_stability(alt,temp):
    '''
    Compute (dT/dz + g/cp) from a given temperature profile
    SS in K/m
    '''
    #dz = np.gradient(alt)
    #dTdz = np.gradient(temp,dz)
    dTdz = np.gradient(temp,alt)
    cpz = cp(temp)

    return dTdz + g_alt(alt)/cpz

def wB_freq(alt,temp):
    '''
    N^2, enter alt in meters!
    '''
    # N^2
    # K/m * m/(s2 K) = s^-2
    return static_stability(alt,temp)*g_alt(alt)/temp

def g_alt(alt):
    return Grav*M_Mars/(R_Mars+alt)**2

