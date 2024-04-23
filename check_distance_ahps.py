#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  2 15:06:11 2023

@author: ericallen
"""
import os
import sys
import math
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.haversine import haversine

path = os.getcwd()
master_list_start = pd.read_excel(os.path.join(path, "official_data", "Obs Location Requests All.xlsx"),\
                                                                                  header=0)
master_list_start.columns = map(str.upper, master_list_start.columns)


url_ahps_cms = "https://water.weather.gov/monitor/ahps_cms_report.php?type=csv"
df_cms = pd.read_csv(url_ahps_cms)
df_cms = df_cms.rename(columns={"nws shef id": "NWSLI"})
df_cms["NWSLI"] = df_cms["NWSLI"].str.upper()

cols_to_drop = ['location name', 'proximity', 'river/water-body name',
       'location type', 'state', 'county', 'wrr', 'timezone', 'inundation', 'elevation',
       'action stage', 'flood stage', 'moderate flood stage',
       'major flood stage', 'flood stage unit', 'coeid', 'hydrograph page',
       'pedts', 'in service', 'hemisphere',
       'low water threshold value / units', 'forecast status',
       'display low water impacts', 'low flow display',
       'give data attribution', 'attribution wording', 'fema wms',
       'probabilistic site', 'weekly chance probabilistic enabled',
       'short-term probabilistic enabled',
       'chance of exceeding probabilistic enabled',
       'nrldb vertical datum name', 'nrldb vertical datum',
       'navd88 vertical datum', 'ngvd29 vertical datum', 'msl vertical datum',
       'other vertical datum']

df_cms.drop(labels=cols_to_drop, axis=1, inplace=True)

df_cms.columns = map(str.upper, df_cms.columns)


nwm_list_with_ahps = pd.merge(master_list_start, df_cms, on="NWSLI", how="left", suffixes=('_NWC', '_AHPS'))



for index, row in nwm_list_with_ahps.iterrows():
    WFO = row["WFO"]
    nwsli_tmp = row["NWSLI"]
    if pd.isna(row["LATITUDE_AHPS"]) and pd.isna(row["LONGITUDE_AHPS"]) and row["STATION ID"] == "None":
        print(f"{WFO} : {nwsli_tmp} there is no AHPS page for this NWSLI")
        
        
for index, row in nwm_list_with_ahps.iterrows():
    WFO = row["WFO"]
    nwsli_tmp = row["NWSLI"]
    if not pd.isna(row["RFC_NWC"]) and not pd.isna(row["RFC_AHPS"]):
        if row["RFC_NWC"]+"RFC" != row["RFC_AHPS"].upper():
            print(f"{WFO} : {nwsli_tmp} the RFC Does Not Match, ", row["RFC_NWC"], row["RFC_AHPS"])

"""
list1 = []
for index, row in master_list_start.iterrows():
    WFO = row["WFO"]
    nwsli_tmp = row["NWSLI"]
    if pd.isna(row["DECIMAL LAT"]) and pd.isna(row["DECIMAL LON"]):
        NWM_with_NWSLI.at[index,"Distance Error"] = -99999.99
    else:
        distance = haversine(row["LATITUDE_NWC"], row["LONGITUDE_NWC"], row["DECIMAL LAT"], row["DECIMAL LON"])
        if distance/1000 > 10:
            in_km = distance/1000
            print(f"{WFO} : {nwsli_tmp} distance between NWC List and NWSLI is {in_km} - Greater than 10 km")
            list1.append(list(row.values))
        elif distance/1000 > 1:
            in_km = distance/1000
            print(f"{WFO} : {nwsli_tmp} distance between NWC List and NWSLI is {in_km} - Greater than 1 km")
            list1.append(list(row.values))

        NWM_with_NWSLI.at[index,"Distance Error"] = distance
        
"""

list1 = []
for index, row in nwm_list_with_ahps.iterrows():
    WFO = row["WFO"]
    nwsli_tmp = row["NWSLI"]
    if pd.isna(row["LATITUDE_AHPS"]) and pd.isna(row["LONGITUDE_AHPS"]):
        nwm_list_with_ahps.at[index,"Distance Error"] = -99999.99
    else:
        if row["LONGITUDE_AHPS"] > 0:
            ahps_lon = -1 * row["LONGITUDE_AHPS"]
        else:
            ahps_lon = row["LONGITUDE_AHPS"]

        distance = haversine(row["LATITUDE_NWC"], row["LONGITUDE_NWC"], row["LATITUDE_AHPS"], ahps_lon)
        if distance/1000 > 10:
            in_km = distance/1000
            print(f"{WFO} : {nwsli_tmp} distance between NWC List and AHPS is {in_km} - Greater than 10 km")
            list1.append(list(row.values))
        elif distance/1000 > 1:
            in_km = distance/1000
            print(f"{WFO} : {nwsli_tmp} distance between NWC List and AHPS is {in_km} - Greater than 1 km")
            list1.append(list(row.values))

        nwm_list_with_ahps.at[index,"Distance Error"] = distance