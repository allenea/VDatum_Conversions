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
#import os
import json
import requests
#import pandas as pd
import numpy as np

def convert_datums(metadata):
    
    api_url = "https://vdatum.noaa.gov/vdatumweb/api/convert?s_x={0}&s_y={1}&s_z={2}&region={3}&s_h_frame={4}&s_coor={5}&s_v_frame={6}&s_v_unit={7}&s_v_elevation={8}&t_h_frame={9}&t_coor={10}&t_v_frame={11}&t_v_unit={12}&t_v_elevation={13}"
        
    input_h_coord = "geo" #Should stay the same 
    input_v_unit = "us_ft" #Unit should be feet
    input_v_elevation = "height" #Should stay the same 
    target_h_ref = "NAD83_2011" #Should stay the same 
    target_h_coord = "geo" #Should stay the same 
    target_v_unit = "us_ft" #Should stay the same
    target_v_elevation = "height" #should stay the same
    
    columns = ['MHHW', 'MHW', 'MTL','MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', "NGVD29"]
    
    for index, row in metadata.iterrows():
        
        region = row['VDatum Regions']
        inputlon = row['Longitude']
        inputlat = row['Latitude']
        
        if not region == "chesapeak_delaware":
            #Should stay the same unless DE Bay/CBay
            input_h_ref = "NAD83_2011" 
            target_h_ref = "NAD83_2011" #Should stay the same 

        else:
            input_h_ref = "IGS14"
            target_h_ref = "NAD83_2011" #Should stay the same 
                
        
        if row["Ref_Datum"] is np.nan:

            input_v_ref = "NAVD88"
            target_v_ref = "MLLW"
            inputheight = "1.0"
            
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
            
            vdatum_data = json.loads(requests.get(tmp_api).text)

            try:
                metadata.loc[index, 'NAVD88_to_MLLW'] = vdatum_data["t_z"]
            except:
                print(tmp_api)
                print("1-", vdatum_data["message"])
                metadata.loc[index, 'NAVD88_to_MLLW'] = np.nan
    
        else:
            input_v_ref = row['Ref_Datum']
            #input_v_ref = "NAVD88" #Datum being converted from spreadsheet
            inputheight = row[row["Ref_Datum"]]
            
            if not region == "chesapeak_delaware":
                #Should stay the same unless DE Bay/CBay
                input_h_ref = "NAD83_2011" 
                target_h_ref = "NAD83_2011" #Should stay the same 
    
            else:
                input_h_ref = "IGS14"
                target_h_ref = "NAD83_2011" #Should stay the same 
            
    
        for col in columns:
            
            if row["Ref_Datum"] is np.nan:
                break                

            if row[col] is np.nan:
                target_v_ref = col
                
                tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                       input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                           target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
                
                vdatum_data = json.loads(requests.get(tmp_api).text)
                
                try:
                    metadata.loc[index, target_v_ref] = vdatum_data["t_z"]
                except:
                    print(tmp_api)
                    print("1-", vdatum_data["message"])
                    continue
        

               

         
        """
        #print(index)
        
        if row["Ref_Datum"] is np.nan:
            continue
        else:
            input_v_ref = row['Ref_Datum']
            #input_v_ref = "NAVD88" #Datum being converted from spreadsheet
            inputlon = row['Longitude']
            inputlat = row['Latitude']
            inputheight = row[row["Ref_Datum"]]
            region = row['VDatum Regions']
            
            if not region == "chesapeak_delaware":
                #Should stay the same unless DE Bay/CBay
                input_h_ref = "NAD83_2011" 
                target_h_ref = "NAD83_2011" #Should stay the same 

            else:
                input_h_ref = "IGS14"
                target_h_ref = "NAD83_2011" #Should stay the same 


        # Check if the reference datum is NGVD29 and no NAVD88
        if row['Ref_Datum'] == 'NGVD29' and row["NAVD88"] is np.nan:
            # Convert NGVD29 to NAVD88
            target_v_ref = 'NAVD88'
            
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
            
            vdatum_data = json.loads(requests.get(tmp_api).text)
            
            try:
                metadata.loc[index, target_v_ref] = vdatum_data["t_z"]
            except:
                continue
            
            input_v_ref = target_v_ref
            
            target_v_ref = "MLLW"
            
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
            
            vdatum_data = json.loads(requests.get(tmp_api).text)
            
            metadata.loc[index, 'NAVD88_to_MLLW'] = vdatum_data["t_z"]

        # Check if the reference datum is NAVD88 and there is no MLLW
        elif row['Ref_Datum'] == 'NAVD88' and row["MLLW"] is np.nan:
            target_v_ref = "MLLW"
            
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
            
            vdatum_data = json.loads(requests.get(tmp_api).text)
            
            try:
                metadata.loc[index, target_v_ref] = vdatum_data["t_z"]
                metadata.loc[index, 'NAVD88_to_MLLW'] = vdatum_data["t_z"]

            except:
                print(tmp_api)
                print("1-", vdatum_data["message"])
                continue
            

        
        elif row['Ref_Datum'] == 'NAVD88' and not row["MLLW"] is np.nan:
            metadata.loc[index, 'NAVD88_to_MLLW'] = row["MLLW"]
  
        elif row['Ref_Datum'] == 'MLLW' and row["NAVD88"] is np.nan:
            target_v_ref = "NAVD88"
            
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
            
            vdatum_data = json.loads(requests.get(tmp_api).text)
            
            metadata.loc[index, target_v_ref] = vdatum_data["t_z"]
            
            
            input_v_ref = target_v_ref
            
            target_v_ref = "MLLW"
            
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
            
            vdatum_data = json.loads(requests.get(tmp_api).text)
            
            metadata.loc[index, 'NAVD88_to_MLLW'] = -1 * vdatum_data["t_z"]
        
        else:
            target_v_ref = "NAVD88"
            
            tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                   input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                       target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
                        
            vdatum_data = json.loads(requests.get(tmp_api).text)
            
            try:
                metadata.loc[index, target_v_ref] = vdatum_data["t_z"]
            except:
                print(tmp_api)
                print("2-", vdatum_data["message"])
                continue
            
                        
            input_v_ref = target_v_ref
            
            target_v_ref = "MLLW"
            

            try:
                tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                       input_v_ref, input_v_unit, input_v_elevation, target_h_ref,\
                                           target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
                
                
                vdatum_data = json.loads(requests.get(tmp_api).text)

                metadata.loc[index, 'NAVD88_to_MLLW'] = vdatum_data["t_z"]
            except:
                print(tmp_api)
                print("3a-", vdatum_data["message"])
                print("---------")
                tmp_api = api_url.format(inputlon, inputlat,inputheight, region, input_h_ref, input_h_coord,\
                                       input_v_ref, input_v_unit, input_v_elevation, "IGS14",\
                                           target_h_coord, target_v_ref, target_v_unit, target_v_elevation)
                
                print(tmp_api)
                print()
                vdatum_data = json.loads(requests.get(tmp_api).text)

                metadata.loc[index, 'NAVD88_to_MLLW'] = vdatum_data["t_z"]
                
                print("3b-", vdatum_data["message"])
                continue
            
        """
            


    return metadata


