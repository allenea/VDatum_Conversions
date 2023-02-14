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


Ref_Datum, Ref_to_DATUM, ..., ..., Ref_to_DATUM

NAVD88_to_MLLW NAVD88_to_MHHW, ..., ..., etc.

https://vdatum.noaa.gov/vdatumweb/api/convert?s_x=-73.74&s_y=40.59&s_z=0&
region=contiguous&s_h_frame=NAD83_2011&s_coor=geo&s_v_frame=NAVD88&s_v_unit=us_ft&
s_v_elevation=height&t_h_frame=NAD83_2011&t_coor=geo&t_v_frame=MLLW&t_v_unit=us_ft&
t_v_elevation=height



inputlon = "-73.74" #Lon from spreadsheet
inputlat = "40.59" #Lat from spreadsheet
inputheight = "0" #height from spreadsheet
region = region_dict["Contiguous United States"] #come up with a way to determine if Contiguous or Chesapeake/Delaware Bay
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


api_url = "https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={0}&s_y={1}&s_z={2}&region={3}&s_h_frame={4}&s_coor={5}&s_v_frame={6}&s_v_unit={7}&s_v_elevation={8}&t_h_frame={9}&t_coor={10}&t_v_frame={11}&t_v_unit={12}&t_v_elevation={13}".format(\
             inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord, input_v_ref,\
                input_v_unit, input_v_elevation, target_h_ref, target_h_coord, target_v_ref,\
                    target_v_unit, target_v_elevation)


"""
import os
import sys
import json
import requests
import pandas as pd
import numpy as np


def chesapeak_delaware_exception(api_url_text):
    """THIS IS A REALLY BAD WAY TO DO THIS.... 
    Some weird things are happening with expected inputs"""
    for input_h_ref in ["NAD83_2011", "IGS14"]:
        for target_h_ref in["NAD83_2011", "IGS14"]:
            tmp_api = api_url_text.format(input_h_ref, target_h_ref)
            url_check = check_url(tmp_api)
            if url_check:
                return input_h_ref, target_h_ref
    else:
        print("ERROR: COULD NOT ACCESS API\n\n")
        return None, None


def check_url(url):
    try:
        response = requests.get(url)

        if response.status_code == 500:
            return False
        elif  "errorCode" in json.loads(response.text) and \
            json.loads(response.text)["errorCode"] == 412:
            return False
        else:
            return True
    except requests.exceptions.RequestException as e:
        return "Request failed: {}".format(e)


def convert_datums(metadata, input_v="NAVD88", output_v="MLLW", s_z=None):
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
        
        if s_z is None:
            s_z = row[row["Ref_Datum"]]
        else:
            s_z = s_z
        
        input_h_ref = "{0}"
        target_h_ref = "{1}"

        url = f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&t_coor={target_h_coord}&t_v_frame={target_v_ref}&t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}"

        if input_region != "chesapeak_delaware":
            input_h_ref = "NAD83_2011"
            target_h_ref = "NAD83_2011"
        else:
            input_h_ref, target_h_ref = chesapeak_delaware_exception(url)
            #print(input_h_ref, target_h_ref)
        
        url = f"https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={s_x}&s_y={s_y}&s_z={s_z}&region={input_region}&s_h_frame={input_h_ref}&s_coor={input_h_coord}&s_v_frame={input_v_ref}&s_v_unit={input_v_unit}&s_v_elevation={input_v_elevation}&t_h_frame={target_h_ref}&t_coor={target_h_coord}&t_v_frame={target_v_ref}&t_v_unit={target_v_unit}&t_v_elevation={target_v_elevation}"

        

        if check_url(url):
            result = requests.get(url).json()
        else:
            metadata.loc[index, "NAVD88_to_MLLW"] = np.nan
            continue
        
        if result["t_z"] == "-999999":
            metadata.loc[index, "NAVD88_to_MLLW"] = "-999999"
        else:
            metadata.loc[index, "NAVD88_to_MLLW"] = s_z - float(result["t_z"])
        
            
    return metadata


"""
    
def convert_datums(metadata):

    api_url = "https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={0}&s_y={1}&s_z={2}&region={3}&s_h_frame={4}&s_coor={5}&s_v_frame={6}&s_v_unit={7}&s_v_elevation={8}&t_h_frame={9}&t_coor={10}&t_v_frame={11}&t_v_unit={12}&t_v_elevation={13}"

    input_h_coord = "geo" #Should stay the same
    input_v_unit = "us_ft" #Unit should be feet
    input_v_elevation = "height" #Should stay the same
    target_h_coord = "geo" #Should stay the same
    target_v_unit = "us_ft" #Should stay the same
    target_v_elevation = "height" #should stay the same

    #columns = ['MHHW', 'MHW', 'MTL','MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', "NGVD29"]

    for index, row in metadata.iterrows():

        inputlon = row['Longitude']
        inputlat = row['Latitude']
        region = row['VDatum Regions']

        inputheight = "0.0"
        
        input_v_ref = "NAVD88"
        target_v_ref = "MLLW"


        if region != "chesapeak_delaware":
            #Should stay the same unless DE Bay/CBay
            input_h_ref = "NAD83_2011"
            target_h_ref = "NAD83_2011" #Should stay the same
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)

        else:
            #THESE H_REF WILL CHANGE TO WHATEVER COMBINATION WORKS
            input_h_ref = "IGS14"
            target_h_ref = "NAD83_2011" #Should stay the same
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, "{0}", input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, "{1}",\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
            tmp_api = chesapeak_delaware_exception(tmp_api)
            if tmp_api is None:
                sys.exit(0)
            
        
        vdatum_data = json.loads(requests.get(tmp_api).text)
        
        offset = 0 - float(vdatum_data["t_z"])
        metadata.loc[index, 'NAVD88_to_MLLW'] = offset


        del target_v_ref

        for col in columns:

            if row["Ref_Datum"] is np.nan:
                break
            else:
                input_v_ref = row['Ref_Datum']
                inputheight = row[row["Ref_Datum"]]
                if input_v_ref == "NGVD29":
                    target_h_ref = "NAD83_2011" #Should stay the same


            if col == row["Ref_Datum"] or col == 0.0:
                continue
            elif row[col] is np.nan:
                target_v_ref = col

                if region == "chesapeak_delaware":
                    tmp_api = api_url.format(inputlon, inputlat,inputheight, region, "{0}", input_h_coord,\
                                       input_v_ref, input_v_unit, input_v_elevation, "{1}",\
                                           target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
                    tmp_api = chesapeak_delaware_exception(tmp_api)
                    
                    if tmp_api is None:
                        continue

                else:
                    tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                           input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                               target_h_coord, target_v_ref, target_v_unit, target_v_elevation)

                    url_check = check_url(tmp_api)

                    if not url_check:
                        print("FAILURE: ", tmp_api)
                        continue

                vdatum_data = json.loads(requests.get(tmp_api).text)
                metadata.loc[index, target_v_ref] = vdatum_data["t_z"]
                
        
    return metadata
    """

# =============================================================================
# all_metadata = pd.read_csv(os.path.join(os.getcwd(), "Test_Conversion_Datum_today.csv"), header=0)
# 
# all_converted_data = convert_datums(all_metadata)
# 
# reindex_metadata2 = ['NWS HAS', 'rfc', 'state', 'county','VDatum Regions', 'river/water-body name',\
#                     'wrr', 'timezone','NWSLI', 'Station ID', 'Location', 'location name',\
#          'Longitude', 'Latitude', 'Site Type', 'Data Source', 'Node', 'Correction',
#          'Ref_Datum', 'MHHW', 'MHW', 'MTL', 'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',
#          "NAVD88_to_MLLW",
#          'nrldb vertical datum name', 'nrldb vertical datum', 'navd88 vertical datum',
#          'ngvd29 vertical datum', 'msl vertical datum', 'other vertical datum',
#          'elevation', 'action stage', 'flood stage', 'moderate flood stage',
#          'major flood stage', 'flood stage unit', 'hydrograph page']
# all_converted_data = all_converted_data.reindex(columns=reindex_metadata2)
# all_converted_data.to_csv("Test_Conversion_Datum-2.csv", index=False)
# 
# =============================================================================
