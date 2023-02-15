#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  9 16:24:11 2023

@author: ericallen

IF REF_DATUM is NGVD29 and no NAVD88, convert NGVD29 to NAVD88,
        use the original table to store that,
    then new column?? used to convert NAVD88 to MLLW...
    We don't want ref_column to be one thing then have MLLW reference NAVD88//something else'

IF REF DATUM is NAVD88 and there is no MLLW, convert NAVD88 to MLLW

ELSE, store the conversion in the new column going from NAVD88 to MLLW

If REF_DATUM is MLLW - there shouldn't be a NAVD88, so convert to NAVD88
    - The only way to then go from NAVD88 to MLLW is to use the inverse.
    We don't want ref_columns to be one thing then have MLLW reference something else
        Therefore, store in a new column

ELSE OTHER DATUM THAN LISTED, convert to NAVD88 then convert NAVD88 to MLLW using that new column
"""
#import os
#import sys
import pandas as pd
import json
import requests
import numpy as np


def chesapeak_delaware_exception(api_url_text):
    """THIS IS A REALLY BAD WAY TO DO THIS....
    Some weird things are happening with expected inputs"""

    for input_h_ref in ["NAD83_2011", "IGS14", "NAD27"]:
        for target_h_ref in["NAD83_2011", "IGS14", "NAD27"]:
            tmp_api = api_url_text.format(input_h_ref, target_h_ref)
            url_check = check_url(tmp_api)
            if url_check:
                return input_h_ref, target_h_ref

    print("ERROR: COULD NOT ACCESS API")
    return None, None


def check_url(url):
    """Checks to make sure the URL is valid and doesn't contain an error code"""
    try:
        response = requests.get(url)
        if response.status_code == 500:
            return False
        if response.status_code == 403:
            return False
        if  "errorCode" in json.loads(response.text) and \
            json.loads(response.text)["errorCode"] == 412:
            return False
        return True
    except requests.exceptions.RequestException as err:
        return f"Request failed: {err}"


def convert_datums(metadata, input_v="NAVD88", output_v="MLLW", input_height=None):
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

    """
    output_column_header = input_v+"_to_"+output_v

    input_h_coord = "geo"
    input_v_unit = "us_ft"
    input_v_elevation = "height"
    target_h_coord = "geo"
    target_v_unit = "us_ft"
    target_v_elevation = "height"

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

        url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
               f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
               f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
               f"s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&"
               f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
               f"t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}")

        if input_region != "chesapeak_delaware":
            input_h_ref = "NAD83_2011"
            target_h_ref = "NAD83_2011"
        else:
            input_h_ref, target_h_ref = chesapeak_delaware_exception(url)

        url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
               f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
               f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
               f"s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&"
               f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
               f"t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}")


        if check_url(url):
            result = requests.get(url).json()
        else:
            metadata.loc[index, output_column_header] = np.nan
            continue

        if result["t_z"] == "-999999":
            metadata.loc[index, output_column_header] = "-999999"
        else:
            metadata.loc[index, output_column_header] = float(result["t_z"]) - s_z

    return metadata




def convert_from_ref_datum(metadata):
    """Fill in the blanks by converting the reference datum to any un-solved datum conversions"""
    input_h_coord = "geo"
    input_v_unit = "us_ft"
    input_v_elevation = "height"
    target_h_coord = "geo"
    target_v_unit = "us_ft"
    target_v_elevation = "height"

    columns = ['MHHW', 'MHW', 'MTL','MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', "NGVD29"]
    ##TODO REMOVED MSL and STND

    for index, row in metadata.iterrows():

        if pd.isna(row["Ref_Datum"]):
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

            if pd.isna(row[column]):
                target_v_ref = column

                input_h_ref = "{0}"
                target_h_ref = "{1}"

                if input_region != "chesapeak_delaware":
                    input_h_ref = "NAD83_2011"
                    target_h_ref = "NAD83_2011"

                    if target_v_ref == "NGVD29":
                        target_h_ref = "NAD27"

                    if input_v_ref == "NGVD29":
                        input_h_ref = "NAD27"

                else:
                    url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
                        f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
                        f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
                        f"s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&"
                        f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
                        f"t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}")

                    input_h_ref, target_h_ref = chesapeak_delaware_exception(url)


                url = (f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}"
                        f"&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&"
                        f"s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&"
                        f"s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&"
                        f"t_coor={target_h_coord}&t_v_frame={target_v_ref}&"
                        f"t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}")


                if check_url(url):
                    result = requests.get(url).json()
                else:
                    # try:
                    #     if input_region == "chesapeak_delaware":
                    #         print("CBE ERROR")
                    #     else:
                    #         print("REG ERROR")
                    #     response = requests.get(url)
                    #     print("ERROR : ", json.loads(response.text)["message"])
                    # except:
                    #     pass

                    metadata.loc[index, column] = np.nan
                    continue

                t_z = result["t_z"]

                if t_z != float(np.nan):
                    metadata.loc[index, column] = t_z


    return metadata

# =============================================================================
# all_metadata = pd.read_csv(os.path.join(os.getcwd(), "Test_Conversion_Datum_today.csv"), header=0)
#
# all_converted_data = convert_datums(all_metadata)
#
# reindex_metadata2 = ['NWS HAS', 'rfc', 'state', 'county','VDatum Regions',
#    'river/water-body name', 'wrr', 'timezone','NWSLI', 'Station ID', 'Location',
#    'location name', 'Longitude', 'Latitude', 'Site Type', 'Data Source', 'Node', 'Correction',
#          'Ref_Datum', 'MHHW', 'MHW', 'MTL', 'MSL', 'DTL', 'MLW', 'MLLW',
#          'NAVD88', 'STND', 'NGVD29', "NAVD88_to_MLLW",
#          'nrldb vertical datum name', 'nrldb vertical datum', 'navd88 vertical datum',
#          'ngvd29 vertical datum', 'msl vertical datum', 'other vertical datum',
#          'elevation', 'action stage', 'flood stage', 'moderate flood stage',
#          'major flood stage', 'flood stage unit', 'hydrograph page']
# all_converted_data = all_converted_data.reindex(columns=reindex_metadata2)
# all_converted_data.to_csv("Test_Conversion_Datum-2.csv", index=False)
#
# =============================================================================
