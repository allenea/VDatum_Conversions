#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 10:29:11 2023

@author: ericallen
"""
import pandas as pd
from shapely.geometry import Point
from src.convert_timezone import convert_tz_to_pytz

RFC_DICT_AHPS  = {"ACR":"APRFC", "ALR":"SERFC", "FWR":"WGRFC", "KRF":"MBRFC", "MSR":"NCRFC",\
                       "ORN":"LMRFC", "PTR":"NWRFC", "RHA":"MARFC", "RSA":"CNRFC", "STR":"CBRFC",\
                       "TAR":"NERFC", "TIR":"OHRFC", "TUA":"ARRFC"}

def get_nws_attributes(dict_shape, dataframe, lonlat_name=["LONGITUDE", "LATITUDE"]):
    """
    Finds and collects NWS Metadata.


    Parameters
    ----------
    dict_shape : TYPE
        DESCRIPTION. A dictionary containing geopandas dataframes with NWS shapefiles.
    dataframe : TYPE
        DESCRIPTION. A pandas dataframe containing NWS weather station information.


    Returns
    -------
    nws_df : TYPE
        DESCRIPTION.  A pandas dataframe containing metadata for each gage.

    """
    lon, lat = lonlat_name

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

    nws_df = pd.DataFrame(index=range(len(dataframe)), columns=["NWSLI", "WFO", "RFC",\
                                        "REGION", "COUNTY", "STATE", "TIME ZONE"])
    for index, row in dataframe.iterrows():

        point_of_interest = Point(row[lon], row[lat])
        is_found = False
        nws_df.at[index, "NWSLI"] = row["NWSLI"]

        for cwa_index, cwa_geometry in enumerate(cwa["geometry"]):
            if cwa_geometry.contains(point_of_interest):
                nws_df.at[index, "WFO"] = cwa.iloc[cwa_index]["WFO"]
                nws_df.at[index, "REGION"] = wfo_dict[cwa.iloc[cwa_index]["WFO"]]
                is_found = True

        for marine_index, marine_geometry in enumerate(marine_zones["geometry"]):
            if marine_geometry.contains(point_of_interest):
                if is_found:
                    if nws_df.at[index, "WFO"] == marine_zones.iloc[marine_index]["WFO"]:
                        print("FYI: FOUND TWICE", row["NWSLI"], point_of_interest)
                    else:
                        print("FYI: FOUND TWICE IN DIFFERENT WFOS", row["NWSLI"],\
                              point_of_interest, "\t", nws_df.at[index, "WFO"],\
                                  marine_zones.iloc[marine_index]["WFO"])
                else:
                    nws_df.at[index, "WFO"] = marine_zones.iloc[marine_index]["WFO"]
                    nws_df.at[index,"REGION"] = wfo_dict[marine_zones.iloc[marine_index]["WFO"]]
                    is_found = True

        for rfc_index, rfc_geometry in enumerate(rfc["geometry"]):
            if rfc_geometry.contains(point_of_interest):
                nws_df.at[index, "RFC"] = rfc.iloc[rfc_index]["SITE_ID"]

        for county_index, county_geometry in enumerate(counties["geometry"]):
            if county_geometry.contains(point_of_interest):
                nws_df.at[index, "COUNTY"] = counties.iloc[county_index]["COUNTYNAME"]
                nws_df.at[index, "STATE"] = counties.iloc[county_index]["STATE"]
                nws_df.at[index, "TIME ZONE"] = counties.iloc[county_index]["TIME_ZONE"]

        if not is_found:
            print("ERROR: NOT FOUND - ", row["NWSLI"], point_of_interest)

    print("ALL NWSLI Time Zones: ", list(set(nws_df["TIME ZONE"])))
    nws_df = convert_tz_to_pytz(nws_df, header="TIME ZONE")

    nws_df["RFC"] = nws_df["RFC"].apply(lambda x: RFC_DICT_AHPS.get(x, x))

    nws_df["COUNTY"] = nws_df["COUNTY"].str.upper()

    return nws_df
