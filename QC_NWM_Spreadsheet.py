#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 11:22:57 2023

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

#master_list_start.drop(columns=['SITE TYPE', 'NODE', 'CORRECTION', 'DOMAIN'], axis=1, inplace=True)
   
nwsli = pd.ExcelFile(os.path.join(path, "official_data", "NWSLI_All_Sites.xlsx"))


# Read in the two dataframes
all_sites = pd.read_excel(nwsli, "All Sites", header=0)
all_sites_programs = pd.read_excel(nwsli, "All Sites With Programs", header=0)

# Convert column names to title case
all_sites.columns = map(str.upper, all_sites.columns)
all_sites_programs.columns = map(str.upper, all_sites_programs.columns)

all_sites_programs = all_sites_programs.rename(columns={'DECLON':"DECIMAL LON",\
                         "DECLAT":"DECIMAL LAT"})

# Find columns that are only in all_sites_programs (excluding the Sid column)
additional_cols = set(all_sites_programs.columns) - set(all_sites.columns)

# create a list of columns to drop from all_sites_programs
cols_to_drop = set(all_sites_programs.columns) - {'SID'} - additional_cols

# drop the unwanted columns from all_sites_programs
all_sites_programs.drop(cols_to_drop, axis=1, inplace=True)

# Merge the two dataframes on the Sid column, keeping only the necessary columns
NWSLI_Metadata = pd.merge(all_sites, all_sites_programs, on='SID')


    
NWSLI_Metadata = NWSLI_Metadata.rename(columns={'SID':"NWSLI"})

reorder = ['STNSEQNO', 'NWSLI', 'REGION', 'WFO', 'RFC', 'CITY', 'COUNTY', 'STATE',\
           'LATITUDE', 'LONGITUDE', 'DECIMAL LAT', 'DECIMAL LON', 'STATION NAME',\
           'TYPE', 'PGMA', 'PID', 'ADM']
    
NWSLI_Metadata = NWSLI_Metadata.reindex(columns=reorder)


nwm_list_with_nwsli = pd.merge(master_list_start, NWSLI_Metadata, on="NWSLI", how="left", suffixes=('_NWC', '_NWSLI'))

reorder2 = ['NWSLI', 'STATION ID', 'DATA SOURCE', 'LONGITUDE_NWC', 'LATITUDE_NWC', 'REGION_NWC', 'RFC_NWC',
     'STNSEQNO', 'REGION_NWSLI', 'WFO', 'RFC_NWSLI', 'CITY', 'COUNTY', 'STATE', 'LATITUDE_NWSLI',
     'LONGITUDE_NWSLI', 'DECIMAL LAT', 'DECIMAL LON', 'STATION NAME', 'TYPE', 'PGMA', 'PID', 'ADM']
    
#%%
NWM_with_NWSLI = nwm_list_with_nwsli.reindex(columns=reorder2)

for index, row in NWM_with_NWSLI.iterrows():
    WFO = row["WFO"]
    nwsli_tmp = row["NWSLI"]
    if pd.isna(row["DECIMAL LAT"]) and pd.isna(row["DECIMAL LON"]):
        print(f"{WFO} : {nwsli_tmp} is not in CBITS as a valid NWSLI")
        
   
RFC_DICT_NWSLI  = {"ACR":"APRFC", "ALR":"SERFC", "FWR":"WGRFC", "KRF":"MBRFC", "MSR":"NCRFC",\
                   "ORN":"LMRFC", "PTR":"NWRFC", "RHA":"MARFC", "RSA":"CNRFC", "STR":"CBRFC",\
                   "TAR":"NERFC", "TIR":"OHRFC", "TUA":"ARRFC"}
for index, row in NWM_with_NWSLI.iterrows():
    WFO = row["WFO"]
    nwsli_tmp = row["NWSLI"]
    if not pd.isna(row["RFC_NWC"]) and not pd.isna(row["RFC_NWSLI"]):
        if row["RFC_NWC"]+"RFC" != RFC_DICT_NWSLI[row["RFC_NWSLI"].upper()]:
            print(f"{WFO} : {nwsli_tmp} the RFC Does Not Match, ", row["RFC_NWC"], RFC_DICT_NWSLI[row["RFC_NWSLI"].upper()])

REGION_DICT_NWSLI = {"1":"ER", "2":"SR", "3":"CR", "4":"WR", "5":"AR", "6":"PR", "7":"INTL", "8":"Other", "9":"ERROR"}
for index, row in NWM_with_NWSLI.iterrows():
    WFO = row["WFO"]
    nwsli_tmp = row["NWSLI"]
    if not pd.isna(row["REGION_NWC"]) and not pd.isna(row["REGION_NWSLI"]):
        if row["REGION_NWC"] != REGION_DICT_NWSLI[str(int(row["REGION_NWSLI"]))]:
            print(f"{WFO} : {nwsli_tmp} the Region Does Not Match, ", row["REGION_NWC"], REGION_DICT_NWSLI[str(int(row["REGION_NWSLI"]))])


list1 = []
for index, row in NWM_with_NWSLI.iterrows():
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

