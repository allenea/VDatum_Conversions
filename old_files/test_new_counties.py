#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 11:45:09 2023

@author: ericallen
"""
import os
import sys
import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

df = pd.read_excel(os.path.join(os.path.abspath("./.."), "Obs_Locations_Request.xlsx"), header=0)


#counties = gpd.read_file(os.path.join(os.getcwd(), "NWS_GIS_Data", "c_08mr23", "c_08mr23.shp"))
counties = gpd.read_file(os.path.join(os.path.abspath("./.."), "NWS_GIS_Data", "c_08mr23", "c_08mr23.shp"))
cwa = gpd.read_file(os.path.join(os.path.abspath("./.."), "NWS_GIS_Data", "w_08mr23", "w_08mr23.shp"))


count = 0
nws_df = pd.DataFrame(index=range(len(df)), columns=["NWSLI", "COUNTYNAME", "STATE", "TIME_ZONE", "CWA", "WFO"])
for index, row in df.iterrows():
    
    point_of_interest = Point(row["Longitude"], row["Latitude"])
    
    nws_df.loc[index]["NWSLI"] = row["NWSLI"]
    
    
    for cdx, cdomain in enumerate(counties["geometry"]):
        is_in4 = cdomain.contains(point_of_interest)
        if is_in4:
            nws_df.loc[index]["COUNTYNAME"] = counties.iloc[cdx]["COUNTYNAME"]
            nws_df.loc[index]["STATE"] = counties.iloc[cdx]["STATE"]
            nws_df.loc[index]["TIME_ZONE"] = counties.iloc[cdx]["TIME_ZONE"]
            isFound = True
                
    for idx, ldomain in enumerate(cwa["geometry"]):
        is_in1 = ldomain.contains(point_of_interest)
        if is_in1:
            nws_df.loc[index]["WFO"] = cwa.iloc[idx]["WFO"]
    
    if not isFound:
        print("ERROR: NOT FOUND - ", row["NWSLI"], point_of_interest)

for index, row in nws_df.iterrows():
    
    if nws_df.loc[index]["WFO"] != nws_df.loc[index]["CWA"]:
        print("DOES NOT MATCH: ", index, "\t\t", nws_df.loc[index]["WFO"], nws_df.loc[index]["CWA"])

