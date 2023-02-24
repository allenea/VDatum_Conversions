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
REGION_DICT = {"Alaska": "ak",
    "South East Alaska Tidal": "seak",
    "American Samoa": "as",
    "Contiguous United States": "contiguous",
    "Chesapeake/Delaware Bay": "chesapeak_delaware",
    "West Coast": "westcoast",
    "Guam and Commonwealth of Northern Mariana Islands": "gcnmi",
    "Hawaii": "hi",
    "Puerto Rico and US Virgin Islands": "prvi",
    "Saint George Island": "sgi",
    "Saint Paul Island": "spi",
    "Saint Lawrence Island": "sli"}

# Unknown regions
ALASKA = (-169.5, 51.2, -129.5, 71.5)
AMERICAN_SAMOA = (-171.8, -14.5, -168.1, -10.8)
GUAM_CNMNI = (144.5, 13.3, 146.2, 20.8)
HAWAII = (-161.9, 18.7, -154.8, 22.5)
ST_GEORGE_ISLAND = (-171.8, 56.5, -169.5, 59.2)
ST_PAUL_ISLAND = (-173.3, 56.0, -169.5, 58.2)
ST_LAWRENCE_ISLAND = (-173.5, 63.0, -168.5, 65.5)


def assign_regions_vdatum(metadata):
    """ Only differentiates the Chesapeake from the Contiguous United States"""

    all_kmls = read_vdatum_regions()

    region_assign = []

    for index, row in metadata.iterrows():

        point = Point((row["Longitude"], row["Latitude"]))

        if any(kml.geometry.iloc[0].contains(point) for kml in (
                    all_kmls["New Jersey - coastal embayment - South"],
                    all_kmls["Virginia/Maryland/Delaware/New Jersey - Mid-Atlantic Bight shelf"],
                    all_kmls["Delaware - Delaware Bay"],
                    all_kmls["Virginia/Maryland - East Chesapeake Bay"],
                    all_kmls["Maryland - Northwest Chesapeake Bay"],
                    all_kmls["Virginia - Southwest Chesapeake Bay"])):

            region = REGION_DICT["Chesapeake/Delaware Bay"]

        elif all_kmls["Puerto Rico and U.S. Virgin Islands"].geometry.iloc[0].contains(point):

            region = REGION_DICT["Puerto Rico and US Virgin Islands"]

        elif any(kml.geometry.iloc[0].contains(point) for kml in (
                                    all_kmls["Alaska - Southeast, Yakutat to Glacier Bay"],
                                    all_kmls["Alaska - Southeast, Glacier Bay to Whale Bay"],
                                    all_kmls["Alaska - Southeast, Whale Bay to US/Canada Border"])):

            region = REGION_DICT["South East Alaska Tidal"]


        elif any(kml.geometry.iloc[0].contains(point) for kml in (all_kmls["Washington - Coastal"],
                                            all_kmls["Washington - Strait of Juan de Fuca Inland"],
                                            all_kmls["Washington - Strait of Juan de Fuca"],
                                            all_kmls["Washington - Puget Sound"],
                                            all_kmls["Washington/Oregon/California - Offshore"],
                                            all_kmls["Oregon - Coastal Inland"],
                                            all_kmls["Oregon - Coastal"],
                                            all_kmls["California -Monterey Bay to Morro Bay"],
                                            all_kmls["California/Oregon - Coastal"],
                                            all_kmls["California - San Francisco Bay Vicinity"],
                                            all_kmls["California - San Francisco Bay Inland"],
                                            all_kmls["California - Southern California Inland"],
                                            all_kmls["California - Southern California"],
                                            all_kmls["Columbia River"])):

            region = REGION_DICT["West Coast"]

        elif is_west_of(point, ALASKA[0]) and point.y >= ALASKA[1] and point.y <= ALASKA[3]:
            region = REGION_DICT["Alaska"]

        elif is_west_of(point, AMERICAN_SAMOA[0]) and\
                point.y >= AMERICAN_SAMOA[1] and point.y <= AMERICAN_SAMOA[3]:
            region = REGION_DICT["American Samoa"]

        elif is_west_of(point, GUAM_CNMNI[0]) and\
                point.y >= GUAM_CNMNI[1] and point.y <= GUAM_CNMNI[3]:
            region = REGION_DICT["Guam and Commonwealth of Northern Mariana Islands"]

        elif not is_west_of(point, HAWAII[0]) and\
                point.y >= HAWAII[1] and point.y <= HAWAII[3]:
            region = REGION_DICT["Hawaii"]

        elif is_west_of(point, ST_GEORGE_ISLAND[0]) and\
                point.y >= ST_GEORGE_ISLAND[1] and point.y <= ST_GEORGE_ISLAND[3]:
            region = REGION_DICT["Saint George Island"]

        elif is_west_of(point, ST_PAUL_ISLAND[0]) and\
                point.y >= ST_PAUL_ISLAND[1] and point.y <= ST_PAUL_ISLAND[3]:
            region = REGION_DICT["Saint Paul Island"]

        elif is_west_of(point, ST_LAWRENCE_ISLAND[0]) and\
                point.y >= ST_LAWRENCE_ISLAND[1] and point.y <= ST_LAWRENCE_ISLAND[3]:
            region = REGION_DICT["Saint Lawrence Island"]

        else:
            region = REGION_DICT["Contiguous United States"]

        region_assign.append(region)

    return region_assign
