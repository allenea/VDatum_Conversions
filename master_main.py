#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 17:22:11 2023

@author: ericallen

ChatGPT Says: "It looks like this script is used to process some data sources,
    including tide data and water level data, and combines the information into a
    single DataFrame called all_metadata. The script reads in an excel file
    Obs_Locations_Request.xlsx which lists the information about different water
    level monitoring stations, including their station ID and data source.
    The function grab_usgs_data is used to retrieve water level data from the USGS
    data source, while the function grab_nos_data is used to retrieve tide data
    from the National Ocean Service's Tides and Currents website.

Once the data is obtained, it is combined into a single DataFrame and then two
    other data sources are loaded from URLs, df_cms and df_hads. The two data
    sources are merged with the original DataFrame using the column "NWSLI".
    Finally, some columns are dropped from the resulting DataFrame all_metadata."
"""
import os
import sys
import pandas as pd
import numpy as np
import geopandas as gpd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.usgs_datum import grab_usgs_data
from src.tidesandcurrents_datum import grab_nos_data
from src.VDatum_Region_Selection import assign_regions_vdatum
from src.VDatum_Conversion import convert_datums, convert_from_ref_datum
from src.read_join_nws_data import get_nws_attributes
from src.get_urls import get_station_info_urls, get_station_datum_urls, extra_link, create_hyperlink


path = os.getcwd()
#path = os.path.abspath("./..")


req_data = {"Ref_Datum":np.nan, 'MHHW':np.nan, 'MHW':np.nan, 'MTL':np.nan,\
             'MSL':np.nan, 'DTL':np.nan, 'MLW':np.nan, 'MLLW':np.nan,\
             'NAVD88':np.nan, 'STND':np.nan, "NGVD29":np.nan}

# =============================================================================
# READ IN NWC/NWM's TWL OUTPUT LOCATION MASTER LIST
# =============================================================================
master_list_start = pd.read_excel(os.path.join(path, "Obs_Location_Requests_All.xlsx"), header=0)
master_list_start = master_list_start.drop(["Region", "RFC"], axis=1)

# =============================================================================
# READ IN NWS GIS (SHAPEFILE) DATA -- Add to the original list
# =============================================================================
#READ IN NWS GIS DATA - WHO IS RESPONSIBLE FOR FORECASTING THESE LOCATIONS
marine_zones = gpd.read_file(os.path.join(path, "NWS_GIS_Data", "mz08mr23", "mz08mr23.shp"))
rfc = gpd.read_file(os.path.join(path, "NWS_GIS_Data", "rf12ja05", "rf12ja05.shp"))
cwa = gpd.read_file(os.path.join(path, "NWS_GIS_Data", "w_08mr23", "w_08mr23.shp"))
counties = gpd.read_file(os.path.join(path, "NWS_GIS_Data", "c_08mr23", "c_08mr23.shp"))
all_shp = {"CWA": cwa, "RFC": rfc, "MARINE_ZONES": marine_zones, "COUNTIES":counties}

nws_data = get_nws_attributes(all_shp, master_list_start)

#JOIN THE DATA TO STATION DATA
location_metadata = pd.merge(nws_data, master_list_start, on="NWSLI", how="left")

vdatum_regions = assign_regions_vdatum(location_metadata)
location_metadata["VDatum Regions"] = vdatum_regions
# =============================================================================
#SAVE DATA
location_metadata.to_excel("Reformat_Obs_Location_Requests_All.xlsx", index=False)
# =============================================================================
station_info_urls = []
station_datum_urls = []
extra_urls = []
for index, row in location_metadata.iterrows():

    station_id = row["Station ID"]

    if row["Data Source"] == "USGS":
        tmp_df, api_url = grab_usgs_data(station_id)
        station_info_urls.append(create_hyperlink(get_station_info_urls(station_id,\
                                                        source="USGS"),"Station Info"))
        station_datum_urls.append(create_hyperlink(api_url, "Datum Info"))
        extra_urls.append(np.nan)

    elif row["Data Source"] == "Tide":
        tmp_df, ref_datum_nos = grab_nos_data(station_id, ref_datum="MLLW", source="web")

        station_info_urls.append(create_hyperlink(get_station_info_urls(station_id,\
                                                    source="NOS"), "Station Info"))

        station_datum_urls.append(create_hyperlink(get_station_datum_urls(station_id,\
                        source="NOS", ref_datum=ref_datum_nos, fmt="web"), "Datum Info"))

        extra_urls.append(create_hyperlink(extra_link(station_id), "More Info"))

    else:
        tmp_df = pd.DataFrame(req_data, index=["name"])
        station_info_urls.append(np.nan)
        station_datum_urls.append(np.nan)
        extra_urls.append(np.nan)

    if index == 0:
        combine_df = tmp_df
    else:
        combine_df = pd.concat([combine_df, tmp_df], ignore_index=True)



station_metadata = location_metadata.join(combine_df, how="outer")
# =============================================================================
station_metadata["Station Info"] = station_info_urls
station_metadata["Datum Info"] = station_datum_urls
station_metadata["Extra Metadata"] = extra_urls


#RAW DATA
station_metadata.to_excel("Raw_Data-All.xlsx", index=False)
# =============================================================================
# =============================================================================
# READ IN AHPS CMS METADATA
# =============================================================================
url_ahps_cms = "https://water.weather.gov/monitor/ahps_cms_report.php?type=csv"
df_cms = pd.read_csv(url_ahps_cms)
df_cms = df_cms.rename(columns={"nws shef id": "NWSLI"})
df_cms["NWSLI"] = df_cms["NWSLI"].str.upper()
df_cms = df_cms.drop(["wfo", "rfc", 'state', 'county', "timezone"], axis=1)

# =============================================================================
# READ IN USGS HADS METADATA
# =============================================================================
url_usgs_hads = "https://hads.ncep.noaa.gov/USGS/ALL_USGS-HADS_SITES.txt"
df_hads = pd.read_csv(url_usgs_hads, skiprows=4, sep="|", header=None,
                  names=["NWSLI", "USGS Station Number", "GOES Identifer", "NWS HAS",
                         "latitude", "longitude", "Location"])
df_hads["NWSLI"] = df_hads["NWSLI"].str.upper()
df_hads = df_hads.drop(["NWS HAS"], axis=1)

#JOIN THESE 2 SETS OF DATA
new_df = pd.merge(df_hads, df_cms, on="NWSLI", how="left")
# =============================================================================
# JOIN HADS+AHPS METADATA TO STATION_METADATA -- CLEAN UP
# =============================================================================
all_metadata = pd.merge(station_metadata, new_df, on="NWSLI", how="left")

columns_to_drop = ['USGS Station Number', 'GOES Identifer', 'latitude_x',
       'longitude_x', 'proximity', 'location type', 'usgs id', 'latitude_y',
       'longitude_y', 'inundation', 'coeid', 'pedts', 'in service', 'hemisphere',
       'low water threshold value / units', 'forecast status',
       'display low water impacts', 'low flow display',
       'give data attribution', 'attribution wording', 'fema wms',
       'probabilistic site', 'weekly chance probabilistic enabled',
       'short-term probabilistic enabled',
       'chance of exceeding probabilistic enabled']

all_metadata = all_metadata.drop(columns_to_drop, axis=1)

# =============================================================================
# CLEAN UP
# =============================================================================
reindex_metadata = ["NWSLI", 'WFO', 'RFC', 'NWS REGION', 'COUNTYNAME', 'STATE', "TIMEZONE",\
                    'river/water-body name', 'wrr',  'Location', 'location name',\
         'Station ID', 'Longitude', 'Latitude', 'Site Type', 'Data Source', "Station Info",\
         "Datum Info", "Extra Metadata", 'Node', 'Correction',\
         'Domain', 'VDatum Regions', 'Ref_Datum', 'MHHW', 'MHW', 'MTL', 'MSL', 'DTL',\
         'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',\
         'nrldb vertical datum name', 'nrldb vertical datum', 'navd88 vertical datum',
         'ngvd29 vertical datum', 'msl vertical datum', 'other vertical datum',
         'elevation', 'action stage', 'flood stage', 'moderate flood stage',
         'major flood stage', 'flood stage unit', 'hydrograph page']

all_metadata = all_metadata.reindex(columns=reindex_metadata)

all_metadata = all_metadata.rename(columns={'TIMEZONE':'TIME ZONE',\
                        'river/water-body name':"River Waterbody Name",\
                         "wrr":"HUC2", "Location":"Location Name", "location name":"AHPS Name",\
                             "hydrograph page":"Hydrograph"})

#SAVE FILE
all_metadata.to_excel("Non_Converted_Datums_for_NWM_Experiment-All.xlsx", index=False)
#%%
# =============================================================================
# BEGIN VDATUM CONVERSIONS
# =============================================================================
#Convert to all datums (possible) for the actual stations FROM the reference datum
#ignore urls for this one
all_converted_data = convert_from_ref_datum(all_metadata)

print("DONE WITH FROM REF DATUM")

#Do the datum conversion for the model, NAVD88 to MLLW assuming water level/station = 0
all_converted_data_MLLW, url_list_mllw = convert_datums(all_converted_data, input_v="NAVD88",\
                                        output_v="MLLW", input_height=0.0)

all_converted_data_MHHW, url_list2_mhhw = convert_datums(all_converted_data_MLLW, input_v="NAVD88",\
                                         output_v="MHHW", input_height=0.0)




reindex_metadata2 = ['WFO', 'RFC', 'NWS REGION', 'COUNTYNAME', 'STATE', 'TIME ZONE',
        'River Waterbody Name', 'HUC2', 'Location Name', 'AHPS Name',
        'NWSLI', 'Station ID', 'Longitude', 'Latitude', 'Site Type', 'Data Source',
        "Station Info", "Datum Info", "Extra Metadata",
        'Node', 'Correction', 'Domain', 'VDatum Regions', 'Ref_Datum', 'MHHW', 'MHW',
        'MTL', 'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',"LMSL",\
        'NAVD88 to MLLW', 'NAVD88 to MHHW',
        'nrldb vertical datum name', 'nrldb vertical datum',
        'navd88 vertical datum', 'ngvd29 vertical datum', 'msl vertical datum',
        'other vertical datum', 'elevation', 'action stage', 'flood stage',
        'moderate flood stage', 'major flood stage', 'flood stage unit',
        'Hydrograph']

#%%
all_converted_data_final = all_converted_data_MHHW.reindex(columns=reindex_metadata2)

all_converted_data_final["VDatum - MLLW"] = url_list_mllw
all_converted_data_final["VDatum - MHHW"] = url_list2_mhhw

for index2,row2 in all_converted_data_final.iterrows():
    if not pd.isna(row2["Hydrograph"]):
        all_converted_data_final.at[index2, "Hydrograph"] = create_hyperlink(row2["Hydrograph"],\
                                                                             "AHPS Data")


all_converted_data_final.to_excel("Converted_Datums_for_NWM_Experiment-All.xlsx", index=False)


#%% CREATE FORMATTED EXCEL FILE
all_converted_data_final2 = all_converted_data_final

all_converted_data_final2["VDATUM Latitude"] = ''
all_converted_data_final2["VDATUM Longitude"] = ''
all_converted_data_final2["VDATUM Height"] = ''
all_converted_data_final2["VDATUM to MLLW"] = ''
all_converted_data_final2["VDATUM to MHHW"] = ''
all_converted_data_final2["Comments"] = ''

## Make sure data types are numeric for the excel spreadsheet for these columns
# Recycle the cols_to_format lists
cols_to_format = ['Ref_Datum', 'MHHW', 'MHW', 'MTL', 'MSL', 'DTL', 'MLW', 'MLLW',\
                       'NAVD88', 'STND', 'NGVD29',"LMSL"]
for col in cols_to_format:
    #Except this one
    if col == "Ref_Datum":
        continue
    all_converted_data_final2[col] = pd.to_numeric(all_converted_data_final2[col],\
                                                       errors='coerce')

cols_to_format2 = ['NAVD88 to MLLW', 'NAVD88 to MHHW']
for col in cols_to_format2:
    all_converted_data_final2[col] = pd.to_numeric(all_converted_data_final2[col], errors='coerce')


# Get the index of the NWSLI column
nwsli_index = all_converted_data_final2.columns.get_loc('NWSLI')

# Move the NWSLI column to the first position
tmp_col = list(all_converted_data_final2.columns)
tmp_col.insert(0, tmp_col.pop(nwsli_index))
all_converted_data_final2 = all_converted_data_final2[tmp_col]

all_converted_data_final2 = all_converted_data_final2.applymap(lambda x: x.strip()\
                                                   if isinstance(x, str) else x)

#SORT DATA
all_converted_data_final2 = all_converted_data_final2.sort_values(['NWS REGION',\
                                                           'WFO', 'Station ID'])


########################################
# create a Pandas Excel writer using XlsxWriter engine
writer = pd.ExcelWriter('output1.xlsx', engine='xlsxwriter')

# write the DataFrame to the Excel file
all_converted_data_final2.to_excel(writer, index=False, sheet_name='Master Sheet')

# get the XlsxWriter workbook and worksheet objects
workbook  = writer.book
worksheet = writer.sheets['Master Sheet']

# Define the blue hyperlink format
blue_hyperlink_format = workbook.add_format({'color':'blue', 'underline':1,\
                                'text_wrap':False, 'align':'left', 'valign':'vcenter'})

# Set the format for excluded columns
excluded_col_format = workbook.add_format({'text_wrap':False, 'align':'left', 'valign':'vcenter'})

# Set the format for other columns
default_col_format = workbook.add_format({'text_wrap':False, 'align':'left', 'valign':'vcenter'})

# Set the column formats
for col_num, col_name in enumerate(all_converted_data_final2.columns):

    max_len = all_converted_data_final2.iloc[1:,:][col_name].astype(str).str.len().max() * 1.25

    #print(col_name, max_len)
    if max_len > 18:
        max_len = 18
    elif 6 < max_len < 10:
        max_len = 10
    elif max_len < 6:
        max_len = 7.5


    if col_name in ['Station Info', 'Datum Info', 'Extra Metadata', 'Hydrograph',\
                        'VDatum - MLLW', 'VDatum - MHHW']:
        worksheet.set_column(col_num, col_num, max_len, cell_format=blue_hyperlink_format)
    elif col_name in ["Comments"]:
        max_len = 20
        worksheet.set_column(col_num, col_num, max_len, cell_format=default_col_format)
    elif col_name in ["VDATUM Latitude", "VDATUM Longitude", "VDATUM Height", "VDATUM to MLLW",\
                          "VDATUM to MHHW"]:
        max_len = 18
        worksheet.set_column(col_num, col_num, max_len, cell_format=default_col_format)
    elif col_name not in ['River Waterbody Name', 'HUC2', 'Location Name', 'AHPS Name']:
        worksheet.set_column(col_num, col_num, max_len, cell_format=default_col_format)
    else:
        max_len = 15
        worksheet.set_column(col_num, col_num, max_len, cell_format=excluded_col_format)


# Wrap the headers
header_format = workbook.add_format({'text_wrap': True, 'bold': True})
for col_num, value in enumerate(all_converted_data_final2.columns.values):
    worksheet.write(0, col_num, value, header_format)

# Define the red fill format
red_fill_format = workbook.add_format({'bg_color': '#FFC7CE'})
light_yellow_fill = workbook.add_format({'bg_color': '#FDF2D0'})
cyan_fill_format = workbook.add_format({'bg_color': '#00FFFF'})

# Define the conditional formatting rule
blank_cell_rule = {'type': 'blanks', 'format': light_yellow_fill}
missing_rule = {'type':'cell', 'criteria':'==', 'value':-999999, 'format':red_fill_format}
check_error_rule = {'type':'cell', 'criteria':'==', 'value':-999999, 'format':cyan_fill_format}

for col in cols_to_format:
    #Apply the conditional formatting rule to the cell if blank for these columns
    worksheet.conditional_format(1, all_converted_data_final2.columns.get_loc(col),
                                 len(all_converted_data_final2.index),
                                 all_converted_data_final2.columns.get_loc(col),
                                 blank_cell_rule)

# Apply conditional formatting to selected columns
for col in cols_to_format2:
    # Apply the conditional formatting rule to the column
    worksheet.conditional_format(1, all_converted_data_final2.columns.get_loc(col),
                                 len(all_converted_data_final2.index),
                                 all_converted_data_final2.columns.get_loc(col),
                                 missing_rule)


# Check if both columns contain -999999 in the same row
for idx, row in all_converted_data_final2.iterrows():
    if row['NAVD88 to MLLW'] == -999999 and row['NAVD88 to MHHW'] == -999999:
        for col_name in ['VDATUM Latitude', 'VDATUM Longitude', 'VDATUM Height',\
                             'VDATUM to MLLW', 'VDATUM to MHHW']:
            col_idx = all_converted_data_final2.columns.get_loc(col_name)
            worksheet.conditional_format(idx+1, col_idx, idx+1, col_idx,
                                        {'type': 'no_errors', 'format': cyan_fill_format})


# save the Excel file
writer.save()
