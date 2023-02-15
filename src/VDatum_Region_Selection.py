#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 12:57:19 2023

@author: ericallen
"""
from shapely.geometry import Point

# Lookup table to get region code from region name
region_dict = {"Alaska": "ak", "South East Alaska Tidal":"seak", "American Samoa":"as",\
        "Contiguous United States":"contiguous", "Chesapeake/Delaware Bay":"chesapeak_delaware",\
         "West Coast":"westcoast", "Guam and Commonwealth of Northern Mariana Islands":"gcnmi",\
         "Hawaii":"hi", "Puerto Rico and US Virgin Islands":"prvi",\
         "Saint George Island":"sgi","Saint Paul Island":"spi",\
             "Saint Lawrence Island":"sli"}

def assign_regions_vdatum(all_kmls, metadata):
    """ Only differentiates the Chesapeake from the Contiguous United States"""

    region_assign = []
    for index, row in metadata.iterrows():
        inputlon = row["Longitude"]
        inputlat = row["Latitude"]
        point = Point((inputlon, inputlat))

        #bool_list = [DEB_bool, CBN_bool, CBE_bool, CBW_bool]
        if  all_kmls["Delaware Bay"].geometry.iloc[0].contains(point) or\
                all_kmls["Chesapeake North"].geometry.iloc[0].contains(point) or\
                all_kmls["Chesapeake East"].geometry.iloc[0].contains(point) or\
                all_kmls["Chesapeake West"].geometry.iloc[0].contains(point) or\
                all_kmls["Mid-Atlantic Bight"].geometry.iloc[0].contains(point) or\
                all_kmls["New Jersey South"].geometry.iloc[0].contains(point):

            region = region_dict["Chesapeake/Delaware Bay"]
        else:
            region = region_dict["Contiguous United States"]

        region_assign.append(region)

    return region_assign
