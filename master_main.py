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

for index, row in location_metadata.iterrows():

    station_id = row["Station ID"]

    if row["Data Source"] == "USGS":
        tmp_df = grab_usgs_data(station_id)

    elif row["Data Source"] == "Tide":
        tmp_df = grab_nos_data(station_id, ref_datum="MLLW", source="web")

        #Since we only want NAVD88 to MLLW, leave this out for now to avoid confusion
        #But corrcting Reference datum to be STND -- which VDATUM won't know...
        if pd.isna(tmp_df["MLLW"]).values[0] and tmp_df["STND"].values == 0:
            tmp_df = grab_nos_data(station_id, ref_datum="STND", source="web")

    else:
        tmp_df = pd.DataFrame(req_data, index=["name"])

    if index == 0:
        combine_df = tmp_df
    else:
        combine_df = pd.concat([combine_df, tmp_df], ignore_index=True)



station_metadata = location_metadata.join(combine_df, how="outer")
# =============================================================================
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
         'Station ID', 'Longitude', 'Latitude', 'Site Type', 'Data Source', 'Node', 'Correction',\
         'Domain', 'VDatum Regions', 'Ref_Datum', 'MHHW', 'MHW', 'MTL', 'MSL', 'DTL',\
         'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',\
         'nrldb vertical datum name', 'nrldb vertical datum', 'navd88 vertical datum',
         'ngvd29 vertical datum', 'msl vertical datum', 'other vertical datum',
         'elevation', 'action stage', 'flood stage', 'moderate flood stage',
         'major flood stage', 'flood stage unit', 'hydrograph page']

all_metadata = all_metadata.reindex(columns=reindex_metadata)

all_metadata = all_metadata.rename(columns={'river/water-body name':"River Waterbody Name",\
                         "wrr":"HUC2", "Location":"Location Name", "location name":"AHPS Name",\
                             "hydrograph page":"AHPS URL"})

#SAVE FILE
all_metadata.to_excel("Non_Converted_Datums_for_NWM_Experiment-All.xlsx", index=False)
#%%
# =============================================================================
# BEGIN VDATUM CONVERSIONS
# =============================================================================
#Convert to all datums (possible) for the actual stations FROM the reference datum
all_converted_data, url_list3 = convert_from_ref_datum(all_metadata)

print("DONE WITH FROM REF DATUM")

#Do the datum conversion for the model, NAVD88 to MLLW assuming water level/station = 0
all_converted_data_MLLW, url_list1 = convert_datums(all_converted_data, input_v="NAVD88",\
                                        output_v="MLLW", input_height=0.0)

all_converted_data_MHHW, url_list2 = convert_datums(all_converted_data_MLLW, input_v="NAVD88", \
                                         output_v="MHHW", input_height=0.0)
    
    


reindex_metadata2 = ['WFO', 'RFC', 'NWS REGION', 'COUNTYNAME', 'STATE', 'TIMEZONE',
        'River Waterbody Name', 'HUC2', 'Location Name', 'AHPS Name',
        'NWSLI', 'Station ID', 'Longitude', 'Latitude', 'Site Type', 'Data Source',
        'Node', 'Correction', 'Domain', 'VDatum Regions', 'Ref_Datum', 'MHHW', 'MHW',
        'MTL', 'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',"LMSL",\
        'NAVD88 to MLLW', 'NAVD88 to MHHW',
        'nrldb vertical datum name', 'nrldb vertical datum',
        'navd88 vertical datum', 'ngvd29 vertical datum', 'msl vertical datum',
        'other vertical datum', 'elevation', 'action stage', 'flood stage',
        'moderate flood stage', 'major flood stage', 'flood stage unit',
        'AHPS URL']


all_converted_data_final = all_converted_data_MHHW.reindex(columns=reindex_metadata2)

#SAVE FILE
all_converted_data_final.to_excel("Converted_Datums_for_NWM_Experiment-All.xlsx", index=False)
