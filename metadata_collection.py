#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:22:11 2023

@author: ericallen

"""
import os
import sys
import numpy as np
import pandas as pd
import geopandas as gpd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.read_ahps import read_ahps
from src.read_hads import retrieve_hads
from src.read_nwsli import read_in_nwsli
from src.read_awips import get_nws_attributes
from src.unique_twl import create_unique_twl_list, unique_station_id
from src.excel_formatting import init_styles, format_excel_stoplight, format_excel_stoplight_meta


# =============================================================================
# Establish the path
# =============================================================================
path = os.getcwd()
#path = os.path.abspath("./..")
# =============================================================================
writer = pd.ExcelWriter('TWL_Locations_MasterList-Mar21.xlsx', engine='xlsxwriter')
workbook, styles  = init_styles(writer.book)
# =============================================================================
# =============================================================================
# =============================================================================
# READ IN NWSLI MASTER LIST
# =============================================================================
cbits_metadata = read_in_nwsli(os.path.join(path, "official_data", "NWSLI_All_Sites.xlsx"))
print()
print("CBITS Duplicates for NWSLI: ",\
      list(set(cbits_metadata[cbits_metadata.duplicated(["NWSLI"])]["NWSLI"])))
print()
cbits_metadata = cbits_metadata.drop_duplicates(subset=['NWSLI'])
cbits_list = cbits_metadata.copy()

# =============================================================================
# READ IN AHPS MASTER LIST
# =============================================================================
ahps_metadata = read_ahps()

print("AHPS Duplicates for NWSLI: ",\
      list(set(ahps_metadata[ahps_metadata.duplicated(["NWSLI"])]["NWSLI"])))
print("AHPS Duplicates for USGS ID: ",\
      list(set(ahps_metadata[ahps_metadata.duplicated(["USGS ID"])]["USGS ID"])))
print()
ahps_metadata = ahps_metadata.drop_duplicates(subset=['NWSLI'])
ahps_list = ahps_metadata.copy()

# =============================================================================
# Additional NRLDB Attributes
# =============================================================================
# Step 1: Load the new dataset
nrldb_metadata = pd.read_excel(os.path.join(path, "official_data", "Riverstat_Tide.xlsx"),\
                                                                                  header=0)

nrldb_metadata.columns = map(str.upper, nrldb_metadata.columns)

nrldb_metadata = nrldb_metadata.rename(columns={'LID': 'NWSLI', 'WFO':"WFO NRLDB",\
                                        'GSNO':"USGS ID NRLDB", 'OWNER':'OWNER NRLDB'})

# Check if "OWNER NRLDB" contains "USGS" and prepend "US0" to "USGS ID NRLDB"
nrldb_metadata['USGS ID NRLDB'] = nrldb_metadata['USGS ID NRLDB'].fillna('')
# Adjusted code to prepend "US0" only when "USGS ID NRLDB" is not blank and "OWNER NRLDB" contains "USGS"
nrldb_metadata['USGS ID NRLDB'] = nrldb_metadata.apply(
    lambda row: 'US0' + str(row['USGS ID NRLDB']) if 'USGS' in row['OWNER NRLDB'] and pd.notna(row['USGS ID NRLDB']) and row['USGS ID NRLDB'] != '' else str(row['USGS ID NRLDB']),
    axis=1
)


# Ensure the whole "USGS ID NRLDB" column is treated as strings
nrldb_metadata['USGS ID NRLDB'] = nrldb_metadata['USGS ID NRLDB'].astype(str)
print("NRLDB Duplicates for NWSLI: ",\
      list(set(nrldb_metadata[nrldb_metadata.duplicated(["NWSLI"])]["NWSLI"])))
print("NRLDB Duplicates for STATION ID: ",\
      list(set(nrldb_metadata[nrldb_metadata.duplicated(["USGS ID NRLDB"])]["USGS ID NRLDB"])))
print()
riverstat_tide_metadata = nrldb_metadata.drop_duplicates(subset=['NWSLI'])
nrldb_list = nrldb_metadata.copy()
# =============================================================================
# READ IN HADS MASTER LIST
# =============================================================================
hads_metadata = retrieve_hads()
print("HADS Duplicates for NWSLI: ",\
      list(set(hads_metadata[hads_metadata.duplicated(["NWSLI"])]["NWSLI"])))
print("HADS Duplicates for GOED ID: ",\
      list(set(hads_metadata[hads_metadata.duplicated(["GOES_ID"])]["GOES_ID"])))
print()
hads_metadata = hads_metadata.drop_duplicates(subset=['NWSLI'])
hads_list = hads_metadata.copy()
# =============================================================================
# READ IN NWC/NWM's TWL OUTPUT LOCATION MASTER LIST
# =============================================================================
nwc_metadata = pd.read_excel(os.path.join(path, "official_data", "Obs Location Requests All.xlsx"),\
                                                                                  header=0)
nwc_metadata.columns = map(str.upper, nwc_metadata.columns)

nwc_duplicates = nwc_metadata.groupby('NWSLI').filter(lambda x: len(x) > 1)

print("NWC Duplicates for NWSLI: ",\
      list(set(nwc_metadata[nwc_metadata.duplicated(["NWSLI"])]["NWSLI"])))
print("NWC Duplicates for STATION ID: ",\
      list(set(nwc_metadata[nwc_metadata.duplicated(["STATION ID"])]["STATION ID"])))
print()
nwc_metadata = nwc_metadata.drop_duplicates(subset=['NWSLI'])
nwc_list = nwc_metadata.copy()
nwc_list = nwc_list.drop(['NODE', 'CORRECTION'], axis=1)
# =============================================================================
# READ IN MDL's ETSS/PETSS TWL OUTPUT LOCATION MASTER LIST
# =============================================================================
mdl_metadata = pd.read_excel(os.path.join(path, "official_data", "MDL_ETSS_PETSS_List.xlsx"),\
                                                                                 header=0)
mdl_metadata.columns = map(str.upper, mdl_metadata.columns)

mdl_metadata = mdl_metadata.rename(columns={'CO-OPS ID':"STATION ID",\
                                        'NWLI':"NWSLI", 'LAT':"LATITUDE", 'LON':"LONGITUDE"})

mdl_duplicates = mdl_metadata.groupby('NWSLI').filter(lambda x: len(x) > 1)

print("MDL Duplicates for NWSLI: ",\
      list(set(mdl_metadata[mdl_metadata.duplicated(["NWSLI"])]["NWSLI"])))
print("MDL Duplicates for STATION ID: ",\
      list(set(mdl_metadata[mdl_metadata.duplicated(["STATION ID"])]["STATION ID"])))
print()
mdl_metadata = mdl_metadata.drop_duplicates(subset=['NWSLI'])
mdl_list = mdl_metadata.copy()
# =============================================================================
# READ IN NOS's STOFS TWL OUTPUT LOCATION MASTER LIST
# =============================================================================
nos_metadata = pd.read_excel(os.path.join(path, "official_data", "NOS_STOFS_List.xlsx"), header=0)
nos_metadata.columns = map(str.upper, nos_metadata.columns)

nos_duplicates = nos_metadata.groupby('NWSLI').filter(lambda x: len(x) > 1)

print("NOS Duplicates for NWSLI: ",\
      list(set(nos_metadata[nos_metadata.duplicated(["NWSLI"])]["NWSLI"])))
print("NOS Duplicates for STATION ID: ",\
      list(set(nos_metadata[nos_metadata.duplicated(["STATION ID"])]["STATION ID"])))
print()
nos_metadata = nos_metadata.drop_duplicates(subset=['NWSLI'])
nos_list = nos_metadata.copy()
# =============================================================================
# Find unique values in each dataframe
# =============================================================================
unique_to_NWC = sorted(set(nwc_metadata['NWSLI']) -\
                       (set(mdl_metadata['NWSLI']).union(set(nos_metadata['NWSLI']))))

unique_to_MDL = sorted(set(mdl_metadata['NWSLI']) -\
                       (set(nwc_metadata['NWSLI']).union(set(nos_metadata['NWSLI']))))

unique_to_NOS = sorted(set(nos_metadata['NWSLI']) -\
                       (set(nwc_metadata['NWSLI']).union(set(mdl_metadata['NWSLI']))))

# Print the results
print("\n\nUnique to NWC Station List (no Alaska):")
print(unique_to_NWC)

print("\nUnique to ETSS/PETSS Station List:")
print(unique_to_MDL)

print("\nUnique to NOS Station List (Global):")
print(unique_to_NOS)
#%%
# =============================================================================
# Get all unique location values and form the metadata dictionary
# =============================================================================
unique_twl_locations = set(nwc_metadata['NWSLI']).union(set(mdl_metadata['NWSLI'])\
                                                ).union(set(nos_metadata['NWSLI']))

metadata_dict = {"nwc_metadata":nwc_metadata, "mdl_metadata": mdl_metadata,\
                 "nos_metadata":nos_metadata}

ground_truth_dict = {"cbits_metadata":cbits_metadata, "ahps_metadata":ahps_metadata,\
                     "hads_metadata":hads_metadata}
# =============================================================================
#Create the unique dataframe
unique_df = create_unique_twl_list(unique_twl_locations, metadata_dict, ground_truth_dict,\
                                   ["CBITS", "AHPS", "HADS"])

# select rows to drop based on pattern
pattern = '^(?:UH|UJ|MIC|PAC)\d+'
rows_to_drop = unique_df['NWSLI'].str.contains(pattern, regex=True)

## Save the stations we are removing from the unique df, drop empty columns
removed_df = unique_df[rows_to_drop]
removed_df = removed_df.sort_values(['IN USE', 'NWSLI'], ascending=[False, True])
removed_df = removed_df.dropna(axis=1, how='all')

# Remove those rows_to_drop then
# sort dataframe by # in use then alphabetically from there
unique_df = unique_df.drop(unique_df[rows_to_drop].index, axis=0)
unique_df = unique_df.sort_values(['IN USE', 'NWSLI'], ascending=[False, True])

# =============================================================================
cbits_list = cbits_list.rename(columns={'REGION': 'REGION CBITS', 'WFO':"WFO CBITS",\
                                        'RFC':"RFC CBITS", 'COUNTY':'COUNTY CBITS',\
                                        'STATE':'STATE CBITS', 'LATITUDE':'LATITUDE CBITS',\
                                        'LONGITUDE':'LONGITUDE CBITS'})

unique_dfx = pd.merge(unique_df, cbits_list[['NWSLI', 'REGION CBITS', 'WFO CBITS', 'RFC CBITS',\
                                         'COUNTY CBITS', 'STATE CBITS', 'LATITUDE CBITS',\
                                         'LONGITUDE CBITS']], on='NWSLI', how='left')

# =============================================================================
# CHECK AGAINST AWIPS SHAPE FILES
# =============================================================================
all_shp = {}
shp_files = {"CWA":"w_05mr24.shp", "RFC":"rf05mr24.shp", "MARINE_ZONES":"mz05mr24.shp",\
             "COUNTIES":"c_05mr24.shp"}
for key, value in shp_files.items():
    all_shp[key] = gpd.read_file(os.path.join(path, "NWS_GIS_Data", value.split(".shp",\
                                                                maxsplit=1)[0], value))

lonlat_name = ['LONGITUDE CBITS', 'LATITUDE CBITS']
nws_data = get_nws_attributes(all_shp, unique_dfx, lonlat_name)
nws_data = nws_data.rename(columns={"WFO":'WFO AWIPS', "RFC":'RFC AWIPS',\
 "REGION":'REGION AWIPS', "COUNTY":'COUNTY AWIPS', "STATE":'STATE AWIPS',\
    "TIME ZONE":'TIME ZONE AWIPS'})

unique_dfx = pd.merge(unique_dfx, nws_data[['NWSLI', 'WFO AWIPS', 'RFC AWIPS', 'REGION AWIPS']],
                     on='NWSLI', how='left')
# =============================================================================
# =============================================================================
# =============================================================================
# Reorder columns in unique_df_meta
column_order_dfx = ['NWSLI', 'IN USE', 'CBITS', 'AHPS', 'HADS', '|CBITS - AHPS|',
       '|CBITS - HADS|', '|AHPS - HADS|', 'NWC', 'ETSS', 'STOFS',
       '|CBITS-NWC|', '|CBITS-NOS|', '|CBITS-MDL|', '|AHPS-NWC|', '|AHPS-NOS|',
       '|AHPS-MDL|', '|NWC-NOS|', '|NWC-MDL|', '|NOS-MDL|', 'REGION CBITS',
       'REGION AWIPS', 'WFO CBITS', 'WFO AWIPS', 'RFC CBITS', 'RFC AWIPS',
       'COUNTY CBITS', 'STATE CBITS', 'LATITUDE CBITS', 'LONGITUDE CBITS',
       'Greatest ∆X Value']

unique_dfx = unique_dfx.reindex(columns=column_order_dfx)
# =============================================================================
# ADD OTHER METADATA FOR REFERENCE
# =============================================================================
ahps_list = ahps_list.rename(columns={'WFO':"WFO AHPS", 'RFC':"RFC AHPS",\
                                        'COUNTY':'COUNTY AHPS', 'STATE':'STATE AHPS',\
                                        'LATITUDE':'LATITUDE AHPS', 'LONGITUDE':'LONGITUDE AHPS'})

#For some reason there are strings or other objects causing pandas not to recognize these as floats
ahps_list['LATITUDE AHPS'] = ahps_list['LATITUDE AHPS'].str.strip()
ahps_list['LONGITUDE AHPS'] = ahps_list['LONGITUDE AHPS'].str.strip()
ahps_list["LATITUDE AHPS"] = pd.to_numeric(ahps_list["LATITUDE AHPS"], errors='coerce')
ahps_list["LONGITUDE AHPS"] = pd.to_numeric(ahps_list["LONGITUDE AHPS"], errors='coerce')


unique_df_meta = pd.merge(unique_dfx, ahps_list[['NWSLI', 'WFO AHPS', 'RFC AHPS', 'COUNTY AHPS',\
                                 'STATE AHPS', 'LATITUDE AHPS', 'LONGITUDE AHPS']],\
                                  on='NWSLI', how='left')

hads_list = hads_list.rename(columns={'HYDROLOGIC_AREA':"WFO HADS", 'STATE':'STATE HADS',\
                                        'LATITUDE':'LATITUDE HADS', 'LONGITUDE':'LONGITUDE HADS'})

unique_df_meta = pd.merge(unique_df_meta, hads_list[['NWSLI', 'WFO HADS', 'STATE HADS',\
                                   'LATITUDE HADS', 'LONGITUDE HADS']], on='NWSLI', how='left')


nwc_list = nwc_list.rename(columns={'REGION': 'REGION NWC', 'RFC':"RFC NWC",\
                                    'LATITUDE':'LATITUDE NWC', 'LONGITUDE':'LONGITUDE NWC'})

unique_df_meta = pd.merge(unique_df_meta, nwc_list[['NWSLI', 'REGION NWC', 'RFC NWC',\
                                'LATITUDE NWC', 'LONGITUDE NWC']], on='NWSLI', how='left')

unique_df_meta['RFC NWC'] =  unique_df_meta['RFC NWC'] + "RFC"

nos_list = nos_list.rename(columns={'STATE':"STATE NOS", 'LATITUDE':'LATITUDE NOS',\
                                    'LONGITUDE':'LONGITUDE NOS'})

unique_df_meta = pd.merge(unique_df_meta, nos_list[['NWSLI', 'STATE NOS', 'LATITUDE NOS',\
                                           'LONGITUDE NOS']], on='NWSLI', how='left')

mdl_list = mdl_list.rename(columns={'STATE':"STATE MDL", 'LATITUDE':'LATITUDE MDL',\
                                    'LONGITUDE':'LONGITUDE MDL'})

unique_df_meta = pd.merge(unique_df_meta, mdl_list[['NWSLI', 'LATITUDE MDL', 'LONGITUDE MDL']],\
                     on='NWSLI', how='left')


unique_df_meta = unique_df_meta.drop(['|CBITS-NWC|', '|CBITS-NOS|', '|CBITS-MDL|', '|AHPS-NWC|',\
                           '|AHPS-NOS|', '|AHPS-MDL|', '|NWC-NOS|', '|NWC-MDL|',\
                           '|NOS-MDL|', '|CBITS - AHPS|', '|CBITS - HADS|',\
                           '|AHPS - HADS|'], axis=1)


columns_to_compare = ['|CBITS - AHPS|', '|CBITS - HADS|', '|AHPS - HADS|', '|CBITS-NWC|',
                      '|CBITS-NOS|', '|CBITS-MDL|', '|AHPS-NWC|', '|AHPS-NOS|', '|AHPS-MDL|',
                      '|NWC-NOS|', '|NWC-MDL|', '|NOS-MDL|']

# Find the column with the maximum value for each row
unique_dfx['Greatest ∆X'] = unique_dfx[columns_to_compare].idxmax(axis=1)

# Add the maximum value to the new column

unique_dfx['Greatest ∆X Value'] = unique_dfx.apply(lambda row: row[row['Greatest ∆X']]\
                                   if not pd.isnull(row['Greatest ∆X']) else pd.NA, axis=1)
unique_df_meta['Greatest ∆X Value'] = unique_dfx.apply(lambda row: row[row['Greatest ∆X']]\
                                   if not pd.isnull(row['Greatest ∆X']) else pd.NA, axis=1)


ahps_list['USGS ID'] = ahps_list['USGS ID'].str.strip().astype(str)
ahps_list = ahps_list.rename(columns={'USGS ID': 'USGS ID AHPS'})
nwc_list['STATION ID'] = nwc_list['STATION ID'].str.strip().astype(str)
nrldb_list['USGS ID NRLDB'] = nrldb_list['USGS ID NRLDB'].str.strip().astype(str)

# Strip leading and trailing spaces from column names and string values
unique_dfx = unique_dfx.applymap(lambda x: x.strip() if isinstance(x, str) else x)
unique_df_meta = unique_df_meta.applymap(lambda x: x.strip() if isinstance(x, str) else x)


## Add data source information stuff
unique_df_meta = pd.merge(unique_df_meta, nwc_list[['NWSLI', 'DATA SOURCE', 'STATION ID']],\
                         on='NWSLI', how='left')
unique_df_meta = pd.merge(unique_df_meta, ahps_list[['NWSLI', 'USGS ID AHPS']],\
                         on='NWSLI', how='left')
    
unique_df_meta = pd.merge(unique_df_meta, nrldb_list[['NWSLI', 'WFO NRLDB', 'USGS ID NRLDB', 'TIDE', 'OWNER NRLDB']], on='NWSLI', how='left')



# Drop 'Greatest ∆X' column from unique_dfx
unique_dfx.drop(columns=['Greatest ∆X'], inplace=True)

# Reorder columns in unique_df_meta
column_order = ['NWSLI', 'IN USE', 'TIDE', 'CBITS', 'AHPS', 'HADS', 'NWC', 'ETSS', 'STOFS',
                'Greatest ∆X Value',
                'LATITUDE CBITS', 'LONGITUDE CBITS', 'LATITUDE AHPS', 'LONGITUDE AHPS',
                'LATITUDE HADS', 'LONGITUDE HADS', 'LATITUDE NWC', 'LONGITUDE NWC',
                'LATITUDE NOS', 'LONGITUDE NOS', 'LATITUDE MDL', 'LONGITUDE MDL',
                'REGION CBITS', 'REGION AWIPS', 'REGION NWC', 'WFO CBITS', 'WFO AWIPS',
                'WFO AHPS', 'WFO NRLDB', 'WFO HADS', 'RFC CBITS', 'RFC AWIPS', 'RFC AHPS',
                'RFC NWC', 'STATE CBITS', 'STATE AHPS',
                'STATE HADS', 'STATE NOS', 'COUNTY CBITS', 'COUNTY AHPS',
                'DATA SOURCE', 'STATION ID', 'USGS ID AHPS', 'USGS ID NRLDB', "OWNER NRLDB"]

unique_df_meta = unique_df_meta.reindex(columns=column_order)

duplicate_dict = {"nwc_duplicates":nwc_duplicates, "mdl_duplicates": mdl_duplicates,\
                 "nos_duplicates":nos_duplicates}

# =============================================================================
unique_station_ids = set(nwc_duplicates['STATION ID']).union(set(mdl_duplicates['STATION ID'])\
                                                ).union(set(nos_duplicates['STATION ID']))
#%% 

#ground_truth_dict still available...
duplicate_df = unique_station_id(unique_station_ids, duplicate_dict)
duplicate_df = duplicate_df.dropna(axis=1, how='all')



unique_df_meta.to_excel(writer, index=False, sheet_name='Master List Meta', startrow=1)
Master_Sheet2 = writer.sheets['Master List Meta']
Master_Sheet2 = format_excel_stoplight_meta(unique_df_meta, Master_Sheet2,\
                                            styles, headerbuffer=True)

unique_dfx.to_excel(writer, index=False, sheet_name='Master List ∆x', startrow=1)
Master_Sheet = writer.sheets['Master List ∆x']
Master_Sheet = format_excel_stoplight(unique_dfx, Master_Sheet, styles, headerbuffer=True)

# write the DataFrame to the Excel file
removed_df.to_excel(writer, index=False, sheet_name='Removed')
Removed_Sheet = writer.sheets['Removed']
Removed_Sheet = format_excel_stoplight(removed_df, Removed_Sheet, styles)


# write the DataFrame to the Excel file
duplicate_df.to_excel(writer, index=False, sheet_name='ZZZZZ')
Duplicate_Sheet = writer.sheets['ZZZZZ']
Duplicate_Sheet = format_excel_stoplight(duplicate_df, Duplicate_Sheet, styles)

writer.save()
