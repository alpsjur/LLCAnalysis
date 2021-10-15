#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 08:18:08 2021

@author: alpsjur
"""

import xarray as xr
import xgcm
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import sys

path_in = '/projects/NS9869K/LLC2160/'

# read in day as command line argument
day = int(sys.argv[1])

# eta not corrected for ice thicknes, contains ice inprint
eta_uncor = xr.open_dataset(f'/LLC2160_Eta_Arctic_day_{day:04n}_mean.nc')

# ice thickness
iceh = xr.open_dataset(f'/LLC2160_SIheff_Arctic_day_{day:04n}_mean.nc')

# SSH corrected for ice imprint
eta = eta_uncor + 0.93*iceh 

print(eta)

fig, ax = plt.subplots()

 