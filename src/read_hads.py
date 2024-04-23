#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:22:11 2023

@author: ericallen
"""
import os
import requests
import pandas as pd


def retrieve_hads():
    """Pull the hads complete metadata file from online and format into a spreadsheet"""

    # Retrieve file from URL and save in local directory
    url = 'https://hads.ncep.noaa.gov/compressed_defs/all_dcp_defs.txt'
    response = requests.get(url)

    output_file = os.path.join(os.path.abspath("./"),"official_data", "all_dcp_defs.csv")

    # Define the column names for the dataframe
    column_names = ['goes_id', 'nwsli', 'dcp_owner', 'state', 'hydrologic_area',
                    'latitude', 'longitude', 'transmission_time', 'transmission_interval',
                    'location_name', 'decoding_mode'] + ["PE_"+str(i) for i in range(1, 41)]

    # Read the data from the file and create a list of dictionaries with the parsed data
    data = []
    for line in response.content.decode().splitlines():
        line = line.strip().split('|')
        # Convert latitude and longitude from degrees minutes seconds to decimal degrees
        if "-" in line[5]:
            degrees_lat, minutes_lat, seconds_lat = line[5].strip().split(' ')
            latitude = -1 * (abs(float(degrees_lat)) + float(minutes_lat)/float(60) +
                             float(seconds_lat)/float(3600))
        else:
            degrees_lat, minutes_lat, seconds_lat = line[5].strip().split(' ')
            latitude = 1 * (abs(float(degrees_lat)) + float(minutes_lat)/float(60) +
                            float(seconds_lat)/float(3600))

        if "-" in line[6]:
            degrees_lon, minutes_lon, seconds_lon = line[6].strip().split(' ')
            longitude = -1 * (abs(float(degrees_lon)) + float(minutes_lon)/float(60) +
                              float(seconds_lon)/float(3600))
        else:
            degrees_lon, minutes_lon, seconds_lon = line[6].strip().split(' ')
            longitude = 1 * (abs(float(degrees_lon)) + float(minutes_lon)/float(60) +
                             float(seconds_lon)/float(3600))

        dicts = {
            'goes_id': line[0],
            'nwsli': line[1],
            'dcp_owner': line[2],
            'state': line[3],
            'hydrologic_area': line[4],
            'latitude': latitude,
            'longitude': longitude,
            'transmission_time': line[7],
            'transmission_interval': line[8],
            'location_name': line[9].strip(),
            'decoding_mode': line[10]
        }
        # Add the SHEF parameter fields to the dictionary
        count = 1
        for i, param in enumerate(line[11:], start=1):
            if i % 5 == 1:
                param_code = param
            elif i % 5 == 2:
                interval = param
            elif i % 5 == 3:
                offsets = param
            elif i % 5 == 4:
                base_elevation = param
            elif i % 5 == 0:
                gage_correction = param
                if param != "       ":
                    param_string = param_code+"|"+interval+"|"+offsets+"|"+base_elevation+"|" +\
                        gage_correction
                    dicts["PE_"+str(count)] = param_string
                    count += 1

        data.append(dicts)

    hads_metadata = pd.DataFrame(data, columns=column_names)
    hads_metadata.columns = map(str.upper, hads_metadata.columns)

    #Save the file when this function is run
    print(output_file)
    hads_metadata.to_csv(output_file, index=False)

    # Create the dataframe from the list of dictionaries
    return hads_metadata
