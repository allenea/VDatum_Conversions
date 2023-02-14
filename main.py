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
from src.VDatum_Conversion import convert_datums

gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

def read_kml_file(kml_file):
    """simple read in kml file function with geopandas"""
    return gpd.read_file(kml_file, driver='KML')

req_data = {"Ref_Datum":np.nan, 'MHHW':np.nan, 'MHW':np.nan, 'MTL':np.nan,\
             'MSL':np.nan, 'DTL':np.nan, 'MLW':np.nan, 'MLLW':np.nan,\
             'NAVD88':np.nan, 'STND':np.nan, "NGVD29":np.nan}

df = pd.read_excel(os.path.join(os.getcwd(), "Obs_Locations_Request.xlsx"), header=0)
for index, row in df.iterrows():

    station_id = row["Station ID"]

    if row["Data Source"] == "USGS":
        tmp_df = grab_usgs_data(station_id)

    elif row["Data Source"] == "Tide":
        tmp_df = grab_nos_data(station_id, ref_datum="NAVD88", source="web")

        #Since we only want NAVD88 to MLLW, leave this out for now to avoid confusion
        #if pd.isna(tmp_df["NAVD88"]).values[0] and tmp_df["STND"].values == 0:
        #    tmp_df = grab_nos_data(station_id, ref_datum="MLLW", source="web")

    else:
        tmp_df = pd.DataFrame(req_data, index=["name"])

    if index == 0:
        combine_df = tmp_df
    else:
        combine_df = pd.concat([combine_df, tmp_df], ignore_index=True)

station_metadata = df.join(combine_df, how="outer")


url_ahps_cms = "https://water.weather.gov/monitor/ahps_cms_report.php?type=csv"
df_cms = pd.read_csv(url_ahps_cms)
df_cms = df_cms.rename(columns={"nws shef id": "NWSLI"})
df_cms["NWSLI"] = df_cms["NWSLI"].str.upper()

url_usgs_hads = "https://hads.ncep.noaa.gov/USGS/ALL_USGS-HADS_SITES.txt"
df_hads = pd.read_csv(url_usgs_hads, skiprows=4, sep="|", header=None,
                  names=["NWSLI", "USGS Station Number", "GOES Identifer", "NWS HAS",
                         "latitude", "longitude", "Location"])
df_hads["NWSLI"] = df_hads["NWSLI"].str.upper()

new_df = pd.merge(df_hads, df_cms, on="NWSLI", how="left")




all_metadata = pd.merge(station_metadata, new_df, on="NWSLI", how="left")


columns_to_drop = ['USGS Station Number', 'GOES Identifer', 'latitude_x',
       'longitude_x', 'proximity', 'location type', 'usgs id', 'latitude_y',
       'longitude_y', 'wfo', 'inundation', 'coeid', 'pedts', 'in service', 'hemisphere',
       'low water threshold value / units', 'forecast status',
       'display low water impacts', 'low flow display',
       'give data attribution', 'attribution wording', 'fema wms',
       'probabilistic site', 'weekly chance probabilistic enabled',
       'short-term probabilistic enabled',
       'chance of exceeding probabilistic enabled']

all_metadata = all_metadata.drop(columns_to_drop, axis=1)

path = os.getcwd()
#path = os.path.abspath("./..")

DEB_file = os.path.join(path,"VDatum_KML", "DEdelbay33_8301", "DEdelbay33_8301.kml")
CBN_file = os.path.join(path,"VDatum_KML", "MDnwchb11_8301", "MDnwchb11_8301.kml")
CBE_file = os.path.join(path,"VDatum_KML", "MDVAechb11_8301", "MDVAechb11_8301.kml")
CBW_file = os.path.join(path,"VDatum_KML", "VAswchb11_8301", "VAswchb11_8301.kml")

MAB_file = os.path.join(path,"VDatum_KML", "NJscstemb32_8301", "NJscstemb32_8301.kml")
NJS_file = os.path.join(path,"VDatum_KML", "NJVAmab33_8301", "NJVAmab33_8301.kml")


DEB = read_kml_file(DEB_file)
CBN = read_kml_file(CBN_file)
CBE = read_kml_file(CBE_file)
CBW = read_kml_file(CBW_file)
MAB = read_kml_file(MAB_file)
NJS = read_kml_file(NJS_file)

all_kmls = {"Delaware Bay": DEB, "Chesapeake North": CBN, "Chesapeake East": CBE,\
            "Chesapeake West":CBW, "Mid-Atlantic Bight":MAB, "New Jersey South":NJS}

vdatum_regions = assign_regions_vdatum(all_kmls, all_metadata)
all_metadata["VDatum Regions"] = vdatum_regions


reindex_metadata = ['NWS HAS', 'rfc', 'state', 'county','VDatum Regions', 'river/water-body name',\
                    'wrr', 'timezone','NWSLI', 'Station ID', 'Location', 'location name',\
         'Longitude', 'Latitude', 'Site Type', 'Data Source', 'Node', 'Correction',
         'Ref_Datum', 'MHHW', 'MHW', 'MTL', 'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',
         'nrldb vertical datum name', 'nrldb vertical datum', 'navd88 vertical datum',
         'ngvd29 vertical datum', 'msl vertical datum', 'other vertical datum',
         'elevation', 'action stage', 'flood stage', 'moderate flood stage',
         'major flood stage', 'flood stage unit', 'hydrograph page']

all_metadata = all_metadata.reindex(columns=reindex_metadata)
all_metadata["rfc"] = all_metadata["rfc"].str.upper()
all_metadata["state"] = all_metadata["state"].str.upper()

all_metadata = all_metadata.rename(columns={"NWS HAS":"WFO", "rfc":"RFC", "state":"State",\
                             "county":"County",'river/water-body name':"River_Waterbody_Name",\
                                 "timezone":"Timezone", "wrr":"HUC2", "Location":"Location Name",\
                                     "location name":"AHPS Name"})

#print(all_metadata)
all_metadata.to_excel("Non_Converted_Datums.xlsx", index=False)

all_converted_data = convert_datums(all_metadata, input_v="NAVD88", output_v="MLLW", s_z=0.0)

reindex_metadata2 = ['WFO', 'RFC', 'State', 'County', 'VDatum Regions',
       'River_Waterbody_Name', 'HUC2', 'Timezone', 'NWSLI', 'Station ID',
       'Location Name', 'AHPS Name', 'Longitude', 'Latitude', 'Site Type',
       'Data Source', 'Node', 'Correction', 'Ref_Datum', 'MHHW', 'MHW', 'MTL',
       'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',  'NAVD88_to_MLLW',
       'nrldb vertical datum name', 'nrldb vertical datum',
       'navd88 vertical datum', 'ngvd29 vertical datum', 'msl vertical datum',
       'other vertical datum', 'elevation', 'action stage', 'flood stage',
       'moderate flood stage', 'major flood stage', 'flood stage unit',
       'hydrograph page']

all_converted_data = all_converted_data.reindex(columns=reindex_metadata2)


all_converted_data.to_excel("Converted_Datums.xlsx", index=False)
