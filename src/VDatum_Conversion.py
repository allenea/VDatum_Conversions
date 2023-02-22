#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 16:24:11 2023

@author: ericallen
"""
import os
import sys
import pandas as pd
import requests
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.check_url import check_url
from src.find_exception import find_h_ref_exception
from src.get_urls import create_hyperlink


def convert_datums(metadata, input_v="NAVD88", output_v="MLLW", input_height=None,\
                   elevation={'input_v_elevation':'height', "target_v_elevation":'height'}):
    """
    inputlon = "-73.74" #Lon from spreadsheet
    inputlat = "40.59" #Lat from spreadsheet
    inputheight = "0" #height from spreadsheet
    region = region_dict["Contiguous United States"] #come up with a way to
            determine if Contiguous or Chesapeake/Delaware Bay
    input_v_ref = "NAVD88" #Datum being converted from spreadsheet
    target_v_ref = "MLLW" #Datum your are trying to convert to

    input_h_ref = "NAD83_2011" #Should stay the same
    input_h_coord = "geo" #Should stay the same
    input_v_unit = "us_ft" #Unit should be feet
    input_v_elevation = "height" #Should stay the same
    target_h_ref = "NAD83_2011" #Should stay the same
    target_h_coord = "geo" #Should stay the same
    target_v_unit = "us_ft" #Should stay the same
    target_v_elevation = "height" #should stay the same


    api_url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?"
               f"s_x={inputlonv}&s_y={inputlat}&s_z={inputheight}&"
               f"region={region}&s_h_frame={input_h_ref}&s_coor={input_h_coord}&"
               f"s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
               f"s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&"
               f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
               f"t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}")

    Parameters
    ----------
    metadata : TYPE
        DESCRIPTION.
    input_v : TYPE, optional
        DESCRIPTION. The default is "NAVD88".
    output_v : TYPE, optional
        DESCRIPTION. The default is "MLLW".
    s_z : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    metadata : TYPE, dataframe
        DESCRIPTION. Holds all the gage information

    url_list : TYPE, list
        DESCRIPTION. Holds a list of all the url api calls for future reference

    """
    output_column_header = input_v + " to " + output_v


    input_h_coord = "geo"
    input_v_unit = "us_ft"
    target_h_coord = "geo"
    target_v_unit = "us_ft"
    #removed to shorten urls but left option to include...
    #input_v_elevation = "height"
    #target_v_elevation = "height"

    url_list = []
    for index, row in metadata.iterrows():

        input_region = row["VDatum Regions"]
        s_y = row["Latitude"]
        s_x = row["Longitude"]

        input_v_ref = input_v
        target_v_ref = output_v

        if input_height is None:
            s_z = row[row["Ref_Datum"]]
        else:
            s_z = input_height

        input_h_ref = "{0}"
        target_h_ref = "{1}"

        if elevation["input_v_elevation"]=="height" and elevation["target_v_elevation"]=="height":

            url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
                   f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
                   f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
                   f"t_h_frame={target_h_ref}&"
                   f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
                   f"t_v_unit={target_v_unit}")
        else:

            url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
                    f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
                    f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
                    f"s_v_elevation={elevation['input_v_elevation']}&t_h_frame={target_h_ref}&"
                    f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
                    f"t_v_unit={target_v_unit}&t_v_elevation={elevation['target_v_elevation']}")

        if input_region == "contiguous":
            input_h_ref = "NAD83_2011"
            target_h_ref = "NAD83_2011"
            input_v_ref = input_v

        elif input_region == "chesapeak_delaware":
            input_h_ref = "NAD83_2011"
            target_h_ref = "IGS14"
            input_v_ref = input_v

        elif input_region == "westcoast":
            input_h_ref = "NAD83_2011"
            target_h_ref = "IGS14"
            input_v_ref = input_v

        elif input_region == "prvi":
            print("WARNING: NWM Uses LMSL for Puerto Rico domain")
            input_v_ref = "LMSL"
            input_h_ref = "NAD83_2011"
            target_h_ref = "NAD83_2011"

        elif input_region == "hi":
            print("ERROR: VDatum Cannot Handle Conversion from NAVD88 to Tidal Datums for Hawaii")
            input_v_ref = "LMSL"
            input_h_ref, target_h_ref = None, None

        else:
            print("Triggering find_h_ref_exception")
            input_h_ref, target_h_ref = find_h_ref_exception(url)


        if elevation["input_v_elevation"]=="height" and elevation["target_v_elevation"]=="height":

            url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
                   f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
                   f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
                   f"t_h_frame={target_h_ref}&"
                   f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
                   f"t_v_unit={target_v_unit}")
        else:

            url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
                    f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
                    f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
                    f"s_v_elevation={elevation['input_v_elevation']}&t_h_frame={target_h_ref}&"
                    f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
                    f"t_v_unit={target_v_unit}&t_v_elevation={elevation['target_v_elevation']}")


        if check_url(url):
            result = requests.get(url).json()
        else:
            #print("PROBLEM WITH: ", url)
            metadata.loc[index, output_column_header] = np.nan
            url_list.append(create_hyperlink(url, "Error"))
            continue

        if result["t_z"] == "-999999":
            metadata.loc[index, output_column_header] = -999999
            url_list.append(create_hyperlink(url, "Missing"))

        else:
            metadata.loc[index, output_column_header] = float(result["t_z"]) - s_z
            url_list.append(create_hyperlink(url, output_column_header))


    return metadata, url_list




def convert_from_ref_datum(metadata):
    """Fill in the blanks by converting the reference datum to any un-solved datum conversions"""

    input_h_coord = "geo"
    input_v_unit = "us_ft"
    input_v_elevation = "height"

    target_h_coord = "geo"
    target_v_unit = "us_ft"
    target_v_elevation = "height"

    #Had to remove STND and MSL because those aren't Tidal Datums in VDatum -- added LMSL
    columns = ['MHHW', 'MHW', 'MTL','LMSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', "NGVD29"]

    tidal_datums = ['MHHW', 'MHW', 'MTL','LMSL', 'DTL', 'MLW', 'MLLW']

    orthometric_datums = ["NAVD88", "NGVD29", "PRVD02"]

    for index, row in metadata.iterrows():

        if pd.isna(row["Ref_Datum"]):
            continue

        if row["Ref_Datum"] == "STND":
            continue

        input_v_ref = row['Ref_Datum']

        input_region = row["VDatum Regions"]
        s_y = row["Latitude"]
        s_x = row["Longitude"]
        s_z = row[row["Ref_Datum"]]

        # Loop through the different height columns
        for column in columns:
            # Skip if the value is already available
            if column == row["Ref_Datum"]:
                continue

            if not column in row.index or pd.isna(row[column]):
                target_v_ref = column

                input_h_ref = "{0}"
                target_h_ref = "{1}"

# =============================================================================
#
# =============================================================================
                if input_region == "contiguous":
                    if input_v_ref in tidal_datums:
                        input_h_ref = "NAD83_2011"
                    elif input_v_ref in orthometric_datums:
                        input_h_ref = "NAD83_2011"
                        if input_v_ref == "NGVD29":
                            input_h_ref = "NAD27"
                    else:
                        input_h_ref = "NAD83_2011"

                    if target_v_ref in tidal_datums:
                        target_h_ref = "NAD83_2011"
                    elif target_v_ref in orthometric_datums:
                        target_h_ref = "NAD83_2011"
                        if target_v_ref == "NGVD29":
                            target_h_ref = "NAD27"
                    else:
                        target_h_ref = "NAD83_2011"


                elif input_region == "chesapeak_delaware":
                    if input_v_ref in tidal_datums:
                        input_h_ref = "IGS14"
                    elif input_v_ref in orthometric_datums:
                        input_h_ref = "NAD83_2011"
                        if input_v_ref == "NGVD29":
                            input_h_ref = "NAD27"
                    else:
                        input_h_ref = "NAD83_2011"

                    if target_v_ref in tidal_datums:
                        target_h_ref = "IGS14"
                    elif target_v_ref in orthometric_datums:
                        target_h_ref = "NAD83_2011"
                        if target_v_ref == "NGVD29":
                            target_h_ref = "NAD27"
                    else:
                        target_h_ref = "NAD83_2011"

                elif input_region == "westcoast":
                    if input_v_ref in tidal_datums:
                        input_h_ref = "IGS14"
                    elif input_v_ref in orthometric_datums:
                        input_h_ref = "NAD83_2011"
                        if input_v_ref == "NGVD29":
                            input_h_ref = "NAD27"
                    else:
                        input_h_ref = "NAD83_2011"

                    if target_v_ref in tidal_datums:
                        target_h_ref = "IGS14"
                    elif target_v_ref in orthometric_datums:
                        target_h_ref = "NAD83_2011"
                        if target_v_ref == "NGVD29":
                            target_h_ref = "NAD27"
                    else:
                        target_h_ref = "NAD83_2011"

                elif input_region == "prvi":
                    #There is no NAVD88 or NGVD29
                    #start in orthometric
                    if input_v_ref in tidal_datums:
                        input_h_ref = "NAD83_2011"
                    else:
                        input_h_ref = "NAD83_2011"

                    if target_v_ref in tidal_datums:
                        target_h_ref = "NAD83_2011"
                    else:
                        target_h_ref = "NAD83_2011"

                elif input_region == "hi":
                    print("WARNING: VDatum Does Not Have Tidal Datums for Hawaii")
                    input_h_ref, target_h_ref = None, None

                else:
                    print("WARNING: Triggering find_h_ref_exception")

                    url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
                         f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
                         f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
                         f"s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&"
                         f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
                         f"t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}")

                    input_h_ref, target_h_ref = find_h_ref_exception(url)



                url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
                    f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
                    f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
                    f"s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&"
                    f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
                    f"t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}")


                if check_url(url):
                    result = requests.get(url).json()
                else:
                    metadata.loc[index, column] = np.nan
                    continue


                t_z = result["t_z"]


                if t_z == "-999999":
                    metadata.loc[index, column] = np.nan

                elif t_z != float(np.nan):
                    metadata.loc[index, column] = t_z


    return metadata
