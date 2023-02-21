#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 12:57:19 2023

@author: ericallen
"""
import os
import sys
from shapely.geometry import Point
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.read_vdatum_regions import read_vdatum_regions
from src.isrelation import is_west_of#, is_north_of


# Lookup table to get region code from region name
region_dict = {"Alaska": "ak", "South East Alaska Tidal":"seak", "American Samoa":"as",\
        "Contiguous United States":"contiguous", "Chesapeake/Delaware Bay":"chesapeak_delaware",\
         "West Coast":"westcoast", "Guam and Commonwealth of Northern Mariana Islands":"gcnmi",\
         "Hawaii":"hi", "Puerto Rico and US Virgin Islands":"prvi",\
         "Saint George Island":"sgi","Saint Paul Island":"spi",\
             "Saint Lawrence Island":"sli"}


def assign_regions_vdatum(metadata):
    """ Only differentiates the Chesapeake from the Contiguous United States"""

    all_kmls = read_vdatum_regions()

# =============================================================================
#   UNKNOWN REGIONS
# =============================================================================
#   West Longitude, South Latitude, East Longitude, North Latitude
    alaska = (-169.5, 51.2, -129.5, 71.5)
    american_samoa = (-171.8, -14.5, -168.1, -10.8)
    guam_cnmni = (144.5, 13.3, 146.2, 20.8)
    hawaii = (-161.9, 18.7, -154.8, 22.5)
    st_george_island = (-171.8, 56.5, -169.5, 59.2)
    st_paul_island = (-173.3, 56.0, -169.5, 58.2)
    st_lawrence_island = (-173.5, 63.0, -168.5, 65.5)
# =============================================================================

    region_assign = []
    for index, row in metadata.iterrows():

        point = Point((row["Longitude"], row["Latitude"]))

        if all_kmls["New Jersey - coastal embayment - South"].geometry.iloc[0].contains(point) or\
            all_kmls["Virginia/Maryland/Delaware/New Jersey - Mid-Atlantic Bight shelf"].geometry.iloc[0].contains(point) or\
            all_kmls["Delaware - Delaware Bay"].geometry.iloc[0].contains(point) or\
            all_kmls["Virginia/Maryland - East Chesapeake Bay"].geometry.iloc[0].contains(point) or\
            all_kmls["Maryland - Northwest Chesapeake Bay"].geometry.iloc[0].contains(point) or\
            all_kmls["Virginia - Southwest Chesapeake Bay"].geometry.iloc[0].contains(point):

            region = region_dict["Chesapeake/Delaware Bay"]

        elif all_kmls["Puerto Rico and U.S. Virgin Islands"].geometry.iloc[0].contains(point):

            region = region_dict["Puerto Rico and US Virgin Islands"]

        elif all_kmls["Alaska - Southeast, Yakutat to Glacier Bay"].geometry.iloc[0].contains(point) or\
            all_kmls["Alaska - Southeast, Glacier Bay to Whale Bay"].geometry.iloc[0].contains(point) or\
            all_kmls["Alaska - Southeast, Whale Bay to US/Canada Border"].geometry.iloc[0].contains(point):

            region = region_dict["South East Alaska Tidal"]


        elif all_kmls["Washington - Coastal"].geometry.iloc[0].contains(point) or\
            all_kmls["Washington - Strait of Juan de Fuca Inland"].geometry.iloc[0].contains(point) or\
            all_kmls["Washington - Strait of Juan de Fuca"].geometry.iloc[0].contains(point) or\
            all_kmls["Washington - Puget Sound"].geometry.iloc[0].contains(point) or\
            all_kmls["Washington/Oregon/California - Offshore"].geometry.iloc[0].contains(point) or\
            all_kmls["Oregon - Coastal Inland"].geometry.iloc[0].contains(point) or\
            all_kmls["Oregon - Coastal"].geometry.iloc[0].contains(point) or\
            all_kmls["California -Monterey Bay to Morro Bay"].geometry.iloc[0].contains(point) or\
            all_kmls["California/Oregon - Coastal"].geometry.iloc[0].contains(point) or\
            all_kmls["California - San Francisco Bay Vicinity"].geometry.iloc[0].contains(point) or\
            all_kmls["California - San Francisco Bay Inland"].geometry.iloc[0].contains(point) or\
            all_kmls["California - Southern California Inland"].geometry.iloc[0].contains(point) or\
            all_kmls["California - Southern California"].geometry.iloc[0].contains(point) or\
            all_kmls["Columbia River"].geometry.iloc[0].contains(point):

            region = region_dict["West Coast"]

        elif is_west_of(point, alaska[0]) and point.y >= alaska[1] and point.y <= alaska[3]:
            region = region_dict["Alaska"]
        elif is_west_of(point, american_samoa[0]) and\
                point.y >= american_samoa[1] and point.y <= american_samoa[3]:
            region = region_dict["American Samoa"]
        elif is_west_of(point, guam_cnmni[0]) and\
                point.y >= guam_cnmni[1] and point.y <= guam_cnmni[3]:
            region = region_dict["Guam and Commonwealth of Northern Mariana Islands"]
        elif not is_west_of(point, hawaii[0]) and\
                point.y >= hawaii[1] and point.y <= hawaii[3]:
            region = region_dict["Hawaii"]
        elif is_west_of(point, st_george_island[0]) and\
                point.y >= st_george_island[1] and point.y <= st_george_island[3]:
            region = region_dict["Saint George Island"]
        elif is_west_of(point, st_paul_island[0]) and\
                point.y >= st_paul_island[1] and point.y <= st_paul_island[3]:
            region = region_dict["Saint Paul Island"]
        elif is_west_of(point, st_lawrence_island[0]) and\
                point.y >= st_lawrence_island[1] and point.y <= st_lawrence_island[3]:
            region = region_dict["Saint Lawrence Island"]
        else:
            region = region_dict["Contiguous United States"]

        region_assign.append(region)

    return region_assign
