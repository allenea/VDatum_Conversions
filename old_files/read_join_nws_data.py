#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 10:29:11 2023

@author: ericallen
"""
import os
import geopandas as gpd

# Read in Coastal, Offshore and High Seas Marine Zones shapefile
marine_zones = gpd.read_file(os.path.join(os.getcwd(), "NWS_GIS_Data", "mz08mr23", "mz08mr23.shp"))
                             # Read in County Warning Areas shapefile

cwa = gpd.read_file(os.path.join(os.getcwd(), "NWS_GIS_Data", "w_08mr23", "w_08mr23.shp"))



# =============================================================================
# # Read in Coastal, Offshore and High Seas Marine Zones KML
# marine_zones = gpd.read_file('path/to/marine_zones.kml', driver='KML')
# 
# # Read in County Warning Areas KML
# cwa = gpd.read_file('path/to/cwa.kml', driver='KML')
# =============================================================================
