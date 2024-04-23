#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 16:17:00 2023

@author: ericallen
"""
import geopandas as gpd

try:
    gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
except:
    raise ImportError("Check to make sure geopandas and fiona are installed")
    from fiona.drvsupport import supported_drivers
    supported_drivers['KML'] = 'rw'


def read_kml_file(kml_file):
    """simple read in kml file function with geopandas"""
    return gpd.read_file(kml_file, driver='KML')
