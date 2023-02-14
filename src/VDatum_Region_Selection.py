#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 10 12:57:19 2023

@author: ericallen
"""
import geopandas as gpd
from shapely.geometry import Point
gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

"""

def read_kml_file(kml_file):
    return gpd.read_file(kml_file, driver='KML')


DEB_file = os.path.join(os.getcwd(),"VDatum_KML", "DEdelbay33_8301", "DEdelbay33_8301.kml")
CBN_file = os.path.join(os.getcwd(),"VDatum_KML", "MDnwchb11_8301", "MDnwchb11_8301.kml")
CBE_file = os.path.join(os.getcwd(),"VDatum_KML", "MDVAechb11_8301", "MDVAechb11_8301.kml")
CBW_file = os.path.join(os.getcwd(),"VDatum_KML", "VAswchb11_8301", "VAswchb11_8301.kml")

MAB_file = os.path.join(os.getcwd(),"VDatum_KML", "NJscstemb32_8301", "NJscstemb32_8301.kml")
NJS_file = os.path.join(os.getcwd(),"VDatum_KML", "NJVAmab33_8301", "NJVAmab33_8301.kml")


DEB = read_kml_file(DEB_file)
CBN = read_kml_file(CBN_file)
CBE = read_kml_file(CBE_file)
CBW = read_kml_file(CBW_file)
MAB = read_kml_file(MAB_file)
NJS = read_kml_file(NJS_file)

all_kmls = {"Delaware Bay": DEB, "Chesapeake North": CBN, "Chesapeake East": CBE,\
            "Chesapeake West":CBW, "Mid-Atlantic Bight":MAB, "New Jersey South":NJS}
"""

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
            #print("HERE: ", inputlon, inputlat, region)
        else:
            region = region_dict["Contiguous United States"]

        region_assign.append(region)

    return region_assign
