#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 12:57:19 2023

@author: ericallen

Downside, unkown region without kml files are approximated with a box around them
"""
from shapely.geometry import Point
from src.read_vdatum_regions import read_vdatum_regions
from src.isrelation import is_west_of, is_east_of, is_north_of, is_south_of


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

# Unknown regions -- Defined by ChatGPT
ALASKA = (-169.5, 51.2, -129.5, 71.5)
AMERICAN_SAMOA = (-171.8, -14.5, -168.1, -10.8)
GUAM_CNMNI = (144.5, 13.3, 146.2, 20.8)
HAWAII = (-161.9, 18.7, -154.8, 22.5)
ST_GEORGE_ISLAND = (-171.8, 56.5, -169.5, 59.2)
ST_PAUL_ISLAND = (-173.3, 56.0, -169.5, 58.2)
ST_LAWRENCE_ISLAND = (-173.5, 63.0, -168.5, 65.5)


def assign_regions_vdatum(metadata):
    """
    Assign the region for each point in a dataframe

    Parameters
    ----------
    metadata : dataframe
        DESCRIPTION. any list of metadata that needs to have a VDatum Region assigned

    Returns
    -------
    region_assign : list
        DESCRIPTION. list of vdatum regions for each point in the dataframe

    """

    all_kmls = read_vdatum_regions()

    region_assign = []

    for _idx, row in metadata.iterrows():

        #Create the shapely geometry point that will be used
        point = Point((row["LONGITUDE"], row["LATITUDE"]))

        #Check if in Delaware/Chesapeake Bay specialty area
        if any(kml.geometry.iloc[0].contains(point) for kml in (
                all_kmls["New Jersey - coastal embayment - South"],
                all_kmls["Virginia/Maryland/Delaware/New Jersey - Mid-Atlantic Bight shelf"],
                all_kmls["Delaware - Delaware Bay"],
                all_kmls["Virginia/Maryland - East Chesapeake Bay"],
                all_kmls["Maryland - Northwest Chesapeake Bay"],
                all_kmls["Virginia - Southwest Chesapeake Bay"])):

            region = REGION_DICT["Chesapeake/Delaware Bay"]

        #Check if in PR/USVI specialty area
        elif any(kml.geometry.iloc[0].contains(point) for kml in (
                all_kmls["Puerto Rico and U.S. Virgin Islands - Islands"],
                all_kmls["Puerto Rico and U.S. Virgin Islands - Offshore"])):

            region = REGION_DICT["Puerto Rico and US Virgin Islands"]

        #Check if in SE Alaska specialty area
        elif any(kml.geometry.iloc[0].contains(point) for kml in (
                all_kmls["Alaska - Southeast, Yakutat to Glacier Bay"],
                all_kmls["Alaska - Southeast, Glacier Bay to Whale Bay"],
                all_kmls["Alaska - Southeast, Whale Bay to US/Canada Border"])):

            region = REGION_DICT["South East Alaska Tidal"]

        #Check if in West Coast specialty area
        elif any(kml.geometry.iloc[0].contains(point) for kml in (
                all_kmls["Washington - Coastal"],
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

        #Check if in Alaska - Other specialty area, not defined by VDatum
        elif is_west_of(point, ALASKA[0]) and is_east_of(point, ALASKA[2]) and\
                is_north_of(point, ALASKA[1]) and is_south_of(point, ALASKA[3]):
            region = REGION_DICT["Alaska"]

        #Check if in American Samoa specialty area, not defined by VDatum
        elif is_west_of(point, AMERICAN_SAMOA[0]) and is_east_of(point, AMERICAN_SAMOA[2]) and\
                is_north_of(point, AMERICAN_SAMOA[1]) and is_south_of(point, AMERICAN_SAMOA[3]):
            region = REGION_DICT["American Samoa"]

        #Check if in Guam specialty area, not defined by VDatum
        elif is_west_of(point, GUAM_CNMNI[0]) and is_east_of(point, GUAM_CNMNI[2]) and\
                is_north_of(point, GUAM_CNMNI[1]) and is_south_of(point, GUAM_CNMNI[3]):
            region = REGION_DICT["Guam and Commonwealth of Northern Mariana Islands"]

        #Check if in Hawaii specialty area, not defined by VDatum
        elif is_west_of(point, HAWAII[0]) and is_east_of(point, HAWAII[2]) and\
                is_north_of(point, HAWAII[1]) and is_south_of(point, HAWAII[3]):
            region = REGION_DICT["Hawaii"]

        #Check if in St. George Island specialty area, not defined by VDatum
        elif is_west_of(point, ST_GEORGE_ISLAND[0]) and is_east_of(point, ST_GEORGE_ISLAND[2]) and\
                is_north_of(point, ST_GEORGE_ISLAND[1]) and is_south_of(point, ST_GEORGE_ISLAND[3]):
            region = REGION_DICT["Saint George Island"]

        #Check if in St. Paul Island specialty area, not defined by VDatum
        elif is_west_of(point, ST_PAUL_ISLAND[0]) and is_east_of(point, ST_PAUL_ISLAND[2]) and\
                is_north_of(point, ST_PAUL_ISLAND[1]) and is_south_of(point, ST_PAUL_ISLAND[3]):
            region = REGION_DICT["Saint Paul Island"]

        #Check if in St. Lawrence Island specialty area, not defined by VDatum
        elif is_west_of(point, ST_LAWRENCE_ISLAND[0]) and\
                is_east_of(point, ST_LAWRENCE_ISLAND[2]) and\
                is_north_of(point, ST_LAWRENCE_ISLAND[1]) and\
                is_south_of(point, ST_LAWRENCE_ISLAND[3]):
            region = REGION_DICT["Saint Lawrence Island"]

        #Otherwise, VDatum considers the "rest" to be in the Contiguous US
        else:
            region = REGION_DICT["Contiguous United States"]

        region_assign.append(region)

    return region_assign
