#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  3 12:40:42 2023

@author: ericallen

https://tidesandcurrents.noaa.gov/api-helper/url-generator.html

https://api.tidesandcurrents.noaa.gov/mdapi/prod/#Stations


reindex = ['Data Source','Station ID', 'name', 'state', 'lat', 'lng',\
           'type', 'timemeridian',  'timezonecorr', 'reference_id', 'affiliations',\
           'Start Date', 'End Date', 'nos_minor', 'nos_moderate','nos_major',\
           'nws_minor', 'nws_moderate', 'nws_major', 'action', 'Tide Predictions',\
           'Water Levels', 'Datums', 'Harmonic', 'Benchmarks', 'Reports',\
           'Extreme Water Levels', 'Meteorological',  'Conductivity', 'Sea Level Trends',\
           'OFS', 'OFS Code', 'OFS Name', 'PORTS', 'PORT Code', 'PORT Name']
"""
import os
import sys
import requests
import pandas as pd
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.tnc_metadata import get_station_start_end, get_station_flood_levels, get_station_products
from src.excel_formatting import init_styles, format_excel

tides_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?"+\
                                        "type=tidepredictions&units=english"

# Send a GET request to the NOAA API to get the station data
tides_response = requests.get(tides_url)

# Load the JSON data from the response into a list of dictionaries
tides_data = tides_response.json()['stations']

# Create an empty list to store the station data
tides_list = []

# Iterate over each dictionary in the list of station data
for tides in tides_data:
    # Remove keys that we don't care about
    tides.pop('count', None)
    tides.pop('units', None)
    tides.pop('self', None)
    # Append the modified dictionary to the list of station data
    tides_list.append(tides)

# Convert the list of station data to a pandas dataframe
tides_df = pd.DataFrame(tides_list)
tides_df = tides_df.drop(labels=['tidepredoffsets', 'products', 'disclaimers', 'tideType',
                                       'notices', 'expand', 'affiliations','portscode'], axis=1)


tides_df = tides_df.rename(columns={"id":"Station ID"})

tidalpredictions_ids = tides_df['Station ID'].tolist()



# Load the "waterlevels" and "tidalpredictions" endpoints into separate dataframes
waterlevels_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json?"+\
                    "type=waterlevels&units=english"

waterlevels_response = requests.get(waterlevels_url)

# Load the JSON data from the response into a list of dictionaries
waterlevels_df = waterlevels_response.json()['stations']

# Create an empty list to store the station data
waterlevels_list = []

# Iterate over each dictionary in the list of station data
for waterlevel in waterlevels_df:
    # Remove keys that we don't care about
    waterlevel.pop('count', None)
    waterlevel.pop('units', None)
    waterlevel.pop('self', None)
    # Append the modified dictionary to the list of station data
    waterlevels_list.append(waterlevel)

# Convert the list of station data to a pandas dataframe
waterlevels_df = pd.DataFrame(waterlevels_list)
waterlevels_df = waterlevels_df.rename(columns={"id":"Station ID"})

waterlevels_df = waterlevels_df.drop(labels=['details', 'sensors', 'floodlevels',
       'datums', 'supersededdatums', 'harmonicConstituents', 'benchmarks', 'nearby',
       'tidePredOffsets', 'ofsMapOffsets', 'products', 'disclaimers', 'notices',\
           'expand','portscode'], axis=1)

    # Extract the "id" column from each dataframe
waterlevels_ids = waterlevels_df['Station ID'].tolist()


# Find the stations in the "waterlevels" endpoint that are not present in the "tidalpredictions" endpoint
waterlevels_only_ids = list(set(waterlevels_ids) - set(tidalpredictions_ids))

subset_df_exists = waterlevels_df[waterlevels_df['Station ID'].isin(tides_df['Station ID'])]


subset_df_exists = subset_df_exists.drop(labels=['state', 'timezonecorr', 'name', 'lat', 'lng'], axis=1)

tmp_df = pd.merge(tides_df, subset_df_exists, on='Station ID', how='outer')

subset_df_extend = waterlevels_df[~ waterlevels_df['Station ID'].isin(tides_df['Station ID'])]



stations_df = pd.concat([tmp_df.set_index(['Station ID', 'name']), subset_df_extend.set_index(['Station ID', 'name'])], sort=False).reset_index()
stations_df["Data Source"] = "Tide"


print("Number of Stations: ", len(stations_df))


start_end_df = get_station_start_end(stations_df)
print(start_end_df.columns)
flood_levels_df = get_station_flood_levels(start_end_df)
print(flood_levels_df.columns)

df_station_products = get_station_products(flood_levels_df)
print(df_station_products.columns)


reindex = ['Data Source', 'Station ID',  'shefcode', 'name', 'state', 'lat', 'lng',\
           'timezonecorr','timezone', 'timemeridian', \
            'type', 'reference_id', 'tidal', 'tideType', 'greatlakes', 'observedst', 'stormsurge',\
            'forecast', 'outlook', 'nonNavigational',
            'Start Date', 'End Date', 'nos_minor', 'nos_moderate','nos_major',\
            'nws_minor', 'nws_moderate', 'nws_major', 'action', 'Tide Predictions',\
            'Water Levels', 'Datums', 'Harmonic', 'Benchmarks', 'Reports',\
            'Extreme Water Levels', 'Meteorological',  'Conductivity', 'Sea Level Trends',\
            'OFS', 'OFS Code', 'OFS Name', 'PORTS', 'PORT Code', 'PORT Name', 'affiliations']

df_station_products = df_station_products.reindex(columns=reindex)

renames = {"name":"Name", "state":"State", "lat":"Latitude", "lng":"Longitude", "type":"Station Type",\
           'shefcode':'NWSLI', "timezone":"Time Zone", "timemeridian":"Time Meridian",\
           "timezonecorr":"Time Zone Offset", "tideType":"Tide Type",
           "reference_id":"Subordinate ID", 'nos_minor':'NOS Minor (STND)', 'nos_moderate':"NOS Moderate (STND)",
          'nos_major':"NOS Major (STND)", 'nws_minor':"NWS Minor (STND)", 'nws_moderate':"NWS Moderate (STND)",\
          'nws_major':"NWS Major (STND)", 'action':"Action Water Level (STND)", "affiliations":"Affiliations",\
          'tidal':"isTidal", 'greatlakes':"isGreatLakes",'observedst':"usesDST", 'stormsurge':"isStormSurgeMode",\
          'forecast':"displayForcast", 'outlook':"hasHTF"}

all_nos_data = df_station_products.rename(columns=renames)

dt = datetime.now()
timestamp = dt.strftime("%Y-%m-%d_%H%M")

# =============================================================================
# SETUP Excel Spreadsheet and Workbook Objects
# =============================================================================
writer = pd.ExcelWriter(f"All_Tides_And_Currents_Observations_{timestamp}.xlsx", engine='xlsxwriter')
workbook, styles  = init_styles(writer.book)

#SAVE DATA -- NWM List of Stations
all_nos_data.to_excel(writer, index=False, sheet_name='NOS Stations')
NOS_List_Excel = writer.sheets['NOS Stations']
NOS_List_Excel = format_excel(all_nos_data, NOS_List_Excel, styles, hyper_id=False)
writer.save()


