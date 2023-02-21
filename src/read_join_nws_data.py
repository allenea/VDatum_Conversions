#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 10:29:11 2023

@author: ericallen
"""
import pandas as pd
from shapely.geometry import Point

def get_nws_attributes(dict_shape, df):
    """finds and collects NWS Metadata"""
    cwa = dict_shape["CWA"]
    rfc = dict_shape["RFC"]
    marine_zones = dict_shape["MARINE_ZONES"]
    counties = dict_shape["COUNTIES"]

    # Create an empty dictionary
    wfo_dict = {}
    for index, row in cwa.iterrows():
        wfo = row["WFO"]
        region = row["REGION"]
        wfo_dict[wfo] = region

    nws_df = pd.DataFrame(index=range(len(df)), columns=["NWSLI", "WFO", "RFC", "NWS REGION",\
                                                         "COUNTYNAME", "STATE", "TIMEZONE"])
    for index, row in df.iterrows():

        point_of_interest = Point(row["Longitude"], row["Latitude"])
        isFound = False
        nws_df.loc[index]["NWSLI"] = row["NWSLI"]

        for idx, ldomain in enumerate(cwa["geometry"]):
            is_in1 = ldomain.contains(point_of_interest)
            if is_in1:
                nws_df.loc[index]["WFO"] = cwa.iloc[idx]["WFO"]
                nws_df.loc[index]["NWS REGION"] = wfo_dict[cwa.iloc[idx]["WFO"]]
                isFound = True

        for ydx, wdomain in enumerate(marine_zones["geometry"]):
            is_in3 = wdomain.contains(point_of_interest)
            if is_in3:
                if isFound:
                    print("FOUND TWICE", row["NWSLI"], point_of_interest)
                else:
                    nws_df.loc[index]["WFO"] = marine_zones.iloc[ydx]["WFO"]
                    nws_df.loc[index]["NWS REGION"] = wfo_dict[marine_zones.iloc[ydx]["WFO"]]
                    isFound = True


        for jdx, rdomain in enumerate(rfc["geometry"]):
            is_in2 = rdomain.contains(point_of_interest)
            if is_in2:
                nws_df.loc[index]["RFC"] = rfc.iloc[jdx]["SITE_ID"]


        for cdx, cdomain in enumerate(counties["geometry"]):
            is_in4 = cdomain.contains(point_of_interest)
            if is_in4:
                nws_df.loc[index]["COUNTYNAME"] = counties.iloc[cdx]["COUNTYNAME"]
                nws_df.loc[index]["STATE"] = counties.iloc[cdx]["STATE"]
                nws_df.loc[index]["TIMEZONE"] = counties.iloc[cdx]["TIME_ZONE"]

        if not isFound:
            print("ERROR: NOT FOUND - ", row["NWSLI"], point_of_interest)

    return nws_df
