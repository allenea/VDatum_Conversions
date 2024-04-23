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
    
    
    nws_df = nws_df.rename(columns={'WFO':'WFO AWIPS', 'RFC':'RFC AWIPS',\
                                    'REGION':'REGION AWIPS', 'COUNTY':'COUNTY AWIPS',\
                                    'STATE':'STATE AWIPS', 'TIME ZONE':'TIME ZONE AWIPS'})
"""
import os
import sys
import pandas as pd
import numpy as np
import geopandas as gpd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.read_awips import get_nws_attributes
from src.read_ahps import read_ahps
from src.read_hads import retrieve_hads
from src.read_nwsli import read_in_nwsli
from src.usgs_datum import grab_usgs_data
from src.haversine import haversine
from src.vdatum_conversion import convert_datums, convert_from_ref_datum
from src.tidesandcurrents_datum import grab_nos_data
from src.vdatum_region_selection import assign_regions_vdatum
from src.get_urls import get_station_info_urls, get_station_datum_urls, extra_link, create_hyperlink
from src.excel_formatting import init_styles, format_excel



# =============================================================================
# SETUP Excel Spreadsheet and Workbook Objects
# =============================================================================
writer = pd.ExcelWriter('NWM_TWL_Forecast_Locations_SciEval-Sept7.xlsx', engine='xlsxwriter')
workbook, styles  = init_styles(writer.book)
#%%
# =============================================================================
# Establish the path
# =============================================================================
path = os.getcwd()
#path = os.path.abspath("./..")
# =============================================================================
#Datums that we are looking for....
req_data = {key: np.nan for key in ["Ref_Datum", "MHHW", "MHW", "MTL", "MSL",\
                                    "DTL", "MLW", "MLLW", "NAVD88", "STND", "NGVD29"]}
# =============================================================================
# READ IN NWC/NWM's TWL OUTPUT LOCATION MASTER LIST
# =============================================================================
master_list_start = pd.read_excel(os.path.join(path, "official_data", "Obs Location Requests All.xlsx"),\
                                                                                  header=0)
master_list_start.columns = map(str.upper, master_list_start.columns)
master_list_start = master_list_start.drop(['NODE', 'CORRECTION'], axis=1)
original_list = master_list_start.copy()

# =============================================================================
# =============================================================================
# READ IN NWS GIS (SHAPEFILE) DATA -- Add to the original list
# =============================================================================
all_shp = {}

shp_files = {"CWA":"w_05mr24.shp", "RFC":"rf05mr24.shp", "MARINE_ZONES":"mz05mr24.shp",\
             "COUNTIES":"c_05mr24.shp"}
for key, value in shp_files.items():
    all_shp[key] = gpd.read_file(os.path.join(path, "NWS_GIS_Data", value.split(".shp",\
                                                                maxsplit=1)[0], value))

nws_data = get_nws_attributes(all_shp, master_list_start)

# =============================================================================
#JOIN THE DATA TO STATION DATA
#nws_data has nwsli in the first position

location_metadata = pd.merge(nws_data, master_list_start, on="NWSLI", how="inner", suffixes=(' AWIPS', ' NWC'))

location_metadata["RFC NWC"]  = location_metadata["RFC NWC"] + "RFC"
vdatum_regions = assign_regions_vdatum(location_metadata)
location_metadata["VDATUM REGIONS"] = vdatum_regions

#Sort then reser the index so that it is like 0,1,2,3, etc.
location_metadata = location_metadata.sort_values(['REGION AWIPS', 'WFO', 'STATION ID'])
location_metadata = location_metadata.reset_index(drop=True)

#Do the datum conversion for the model, NAVD88 to MLLW assuming water level/station = 0
#%%
df_converted, df_converted["VD NAVD88 - MLLW"] = convert_datums(location_metadata, input_v="NAVD88",\
                                        output_v="MLLW", input_height=0.0)
df_converted, df_converted["VD NAVD88 - MHHW"] = convert_datums(df_converted, input_v="NAVD88",\
                                         output_v="MHHW", input_height=0.0)
df_converted, df_converted["VD LMSL - MLLW"] = convert_datums(df_converted, input_v="LMSL",\
                                        output_v="MLLW", input_height=0.0)
df_converted, df_converted["VD LMSL - MHHW"] = convert_datums(df_converted, input_v="LMSL",\
                                         output_v="MHHW", input_height=0.0)

df_converted["VDATUM LATITUDE"] = ''
df_converted["VDATUM LONGITUDE"] = ''
df_converted["VDATUM HEIGHT"] = ''
df_converted["VDATUM TO MLLW"] = ''
df_converted["VDATUM TO MHHW"] = ''
df_converted["COMMENTS"] = ''


df_col_order = ['NWSLI', 'WFO', 'RFC AWIPS', 'RFC NWC', 'REGION AWIPS', 'REGION NWC', 'COUNTY', 'STATE', 'TIME ZONE',\
                'LONGITUDE', 'LATITUDE', 'STATION ID', 'SITE TYPE', 'DATA SOURCE','DOMAIN', 'VDATUM REGIONS',\
                'NAVD88 TO MLLW', 'NAVD88 TO MHHW', 'LMSL TO MLLW', 'LMSL TO MHHW',\
                'VD NAVD88 - MLLW', 'VD NAVD88 - MHHW', 'VD LMSL - MLLW', 'VD LMSL - MHHW', 'VDATUM LATITUDE',\
                'VDATUM LONGITUDE', 'VDATUM HEIGHT', 'VDATUM TO MLLW', 'VDATUM TO MHHW',\
                'COMMENTS']

df_converted = df_converted.reindex(columns=df_col_order)

## Create the hyperlinks for station information -- will link with Station ID for now
station_info_urls_with_ids = []
station_info_urls = []
for index, row in df_converted.iterrows():
    station_id = row["STATION ID"]
    if row["DATA SOURCE"] == "USGS":
        stid_short = station_id[2:]
        station_info_urls_with_ids.append(create_hyperlink(get_station_info_urls(stid_short,\
                                                        source="USGS"), station_id))

        station_info_urls.append(create_hyperlink(get_station_info_urls(stid_short,\
                                                        source="USGS"), "Station Info"))
    elif row["DATA SOURCE"].upper() == "TIDE" or row["DATA SOURCE"] == "NOS":
        station_info_urls_with_ids.append(create_hyperlink(get_station_info_urls(station_id,\
                                                    source="NOS"), station_id))

        station_info_urls.append(create_hyperlink(get_station_info_urls(station_id,\
                                                    source="NOS"), "Station Info"))
    elif row["DATA SOURCE"].upper() == "USACE":
        stid_short = station_id[5:]
        station_info_urls_with_ids.append(create_hyperlink(get_station_info_urls(stid_short,\
                                                    source="USACE"), station_id))

        station_info_urls.append(create_hyperlink(get_station_info_urls(stid_short,\
                                                    source="USACE"), "Station Info"))
    
    elif station_id is None:
        station_info_urls_with_ids.append(str("None"))
        station_info_urls.append(np.nan)

    else:
        station_info_urls_with_ids.append(station_id)
        station_info_urls.append(np.nan)


#Save a copy before making all the Station ID's hyperlinks, required for later steps
save_df = df_converted.copy()

#Now replace the Station ID column with the hyperlinks
df_converted["STATION ID"] = station_info_urls_with_ids
# =============================================================================
#%%
#SAVE DATA -- NWM List of Stations
df_converted.to_excel(writer, index=False, sheet_name='NWM List with Conversions')
NWC_List_Excel = writer.sheets['NWM List with Conversions']
NWC_List_Excel = format_excel(df_converted, NWC_List_Excel, styles)
# =============================================================================
#%%
coord_sheet = master_list_start.copy()
coord_sheet = coord_sheet.drop(['SITE TYPE', 'DOMAIN'], axis=1)

# =============================================================================
### NEXT STEP.... we want to get the AHPS datum information and add that to the end
# both of the ahps_cms and usgs_hads information will go into the master list...
# however, as stated we will include the AHPS_CMS datum information for the datum sheet.
# =============================================================================
# READ IN AHPS CMS METADATA
# =============================================================================
df_cms = read_ahps()

df_cms_copy = df_cms.copy()


cols_to_drop = ['AHPS NAME', 'PROXIMITY', 'RIVER WATERBODY NAME',
       'LOCATION TYPE', 'HUC2', 'INUNDATION', 'ELEVATION', 'ACTION STAGE',
       'FLOOD STAGE', 'MODERATE FLOOD STAGE', 'MAJOR FLOOD STAGE',
       'FLOOD STAGE UNIT', 'COEID', 'HYDROGRAPH', 'PEDTS', 'IN SERVICE',
       'LOW WATER THRESHOLD VALUE / UNITS', 'FORECAST STATUS',
       'DISPLAY LOW WATER IMPACTS', 'LOW FLOW DISPLAY',
       'GIVE DATA ATTRIBUTION', 'ATTRIBUTION WORDING', 'FEMA WMS',
       'PROBABILISTIC SITE', 'WEEKLY CHANCE PROBABILISTIC ENABLED',
       'SHORT-TERM PROBABILISTIC ENABLED',
       'CHANCE OF EXCEEDING PROBABILISTIC ENABLED',
       'NRLDB VERTICAL DATUM NAME', 'NRLDB VERTICAL DATUM',
       'NAVD88 VERTICAL DATUM', 'NGVD29 VERTICAL DATUM', 'MSL VERTICAL DATUM',
       'OTHER VERTICAL DATUM', 'COUNTY']

df_cms_copy.drop(labels=cols_to_drop, axis=1, inplace=True)

nwm_list_with_ahps = pd.merge(coord_sheet, df_cms_copy, on="NWSLI", how="outer", suffixes=(' NWC', ' AHPS'))

nwm_list_with_ahps2 = nwm_list_with_ahps[nwm_list_with_ahps['NWSLI'].isin(coord_sheet['NWSLI'].unique())]

nwm_list_with_ahps_3 = pd.merge(nwm_list_with_ahps2, nws_data, on="NWSLI", how="outer", suffixes=('', ' AWIPS'))

nwm_list_with_ahps4 = nwm_list_with_ahps_3[nwm_list_with_ahps_3['NWSLI'].isin(coord_sheet['NWSLI'].unique())]

nwm_list_with_ahps4 = nwm_list_with_ahps4.rename(columns={"RFC": "RFC AWIPS", "TIME ZONE":"TIME ZONE AHPS", "COUNTY":"COUNTY AHPS",\
                                          "STATE":"STATE AHPS", "WFO":"WFO AHPS", "REGION":"REGION NWC"})

#%%
hads_metadata = retrieve_hads()

# Save the dataframe to a CSV file
hads_metadata.to_csv(os.path.join(path, 'all_dcp_defs.csv'), index=False)

cols_to_drop_hads = ['GOES_ID', 'TRANSMISSION_TIME', 'TRANSMISSION_INTERVAL', 'LOCATION_NAME', 'DECODING_MODE'] +\
                    ["PE_"+str(i) for i in range(1,41)]

short_hads = hads_metadata.drop(labels=cols_to_drop_hads, axis=1)
short_hads = short_hads.rename(columns={'DCP_OWNER':'DATA SOURCE HADS', 'STATE':'STATE HADS',\
                                                        'HYDROLOGIC_AREA':"WFO HADS", 'LATITUDE':'LATITUDE HADS',
                                                               'LONGITUDE':'LONGITUDE HADS'})
with_hads = pd.merge(nwm_list_with_ahps4, short_hads, on="NWSLI", how="outer", suffixes=('', ' HADS'))

with_hads = with_hads[with_hads['NWSLI'].isin(coord_sheet['NWSLI'].unique())]


with_hads["RFC AHPS"] = with_hads["RFC AHPS"].str.upper()



nwsli = os.path.join(path, "NWSLI_All_Sites.xlsx")
nwsli_metadata = read_in_nwsli(nwsli)


with_nwsli = pd.merge(with_hads, nwsli_metadata, on="NWSLI", how="outer")

with_nwsli = with_nwsli[with_nwsli['NWSLI'].isin(coord_sheet['NWSLI'].unique())]



coord_col_order = ['NWSLI', 'WFO NWSLI', 'WFO AHPS', 'WFO AWIPS', 'WFO HADS', 'STATION ID',\
                   'DATA SOURCE', 'USGS ID','DATA SOURCE HADS', "LATITUDE NWSLI", "LONGITUDE NWSLI",\
                   'LATITUDE NWC', 'LONGITUDE NWC', 'LATITUDE AHPS', 'LONGITUDE AHPS',\
                   'LATITUDE HADS', 'LONGITUDE HADS','REGION NWSLI', 'REGION NWC', 'REGION AWIPS',\
                   'RFC NWSLI', 'RFC NWC',  'RFC AHPS','RFC AWIPS', 'STATE NWSLI', 'STATE AHPS',\
                   'STATE AWIPS', 'STATE HADS', 'COUNTY NWSLI', 'COUNTY AHPS', 'COUNTY AWIPS',\
                   'TIME ZONE AHPS','TIME ZONE AWIPS']

with_nwsli = with_nwsli.reindex(columns=coord_col_order)

print(with_nwsli.columns)
#%%
# =============================================================================
#SAVE DATA -- NWM List of Stations
with_nwsli.to_excel(writer, index=False, sheet_name='Compare Station Locations')
Coord_List_Excel = writer.sheets['Compare Station Locations']
Coord_List_Excel = format_excel(with_nwsli, Coord_List_Excel, styles)

# =============================================================================
#%% Now we are going to get the datum information for each gage location
#We only want to use a copy of save_df
datum_metadata = save_df.copy()
#And drop things we don't need for this sheet
datum_metadata = datum_metadata.drop(['RFC NWC', 'REGION NWC', 'TIME ZONE', 'DOMAIN',
       'NAVD88 TO MLLW', 'NAVD88 TO MHHW', 'LMSL TO MLLW', 'LMSL TO MHHW',
       'VD NAVD88 - MLLW', 'VD NAVD88 - MHHW', 'VD LMSL - MLLW',
       'VD LMSL - MHHW', 'VDATUM LATITUDE', 'VDATUM LONGITUDE',
       'VDATUM HEIGHT', 'VDATUM TO MLLW', 'VDATUM TO MHHW', 'COMMENTS'], axis=1)


#Now we are going to collect the station datum data and the urls and extra urls that tell
# us more information about the data
station_datum_urls = []
extra_urls = []
for index, row in datum_metadata.iterrows():

    station_id = row["STATION ID"]

    if row["DATA SOURCE"] == "USGS":
        stid_short = station_id[2:]
        tmp_df, api_url = grab_usgs_data(stid_short)

        station_datum_urls.append(create_hyperlink(api_url, "Datum Info"))

        extra_urls.append(np.nan)

    elif row["DATA SOURCE"].upper() == "TIDE" or row["DATA SOURCE"].upper() == "NOS":
        tmp_df, ref_datum_nos = grab_nos_data(station_id, ref_datum="MLLW", source="web")

        station_datum_urls.append(create_hyperlink(get_station_datum_urls(station_id,\
                        source="NOS", ref_datum=ref_datum_nos, fmt="web"), "Datum Info"))

        extra_urls.append(create_hyperlink(extra_link(station_id), "More Info"))
    
    elif row["DATA SOURCE"].upper() == "USACE":
        stid_short = station_id[5:]
        
        station_datum_urls.append(create_hyperlink(get_station_info_urls(stid_short,\
                                                source="USACE"), "Datum Info"))
        
        extra_urls.append(np.nan)

    else:
        tmp_df = pd.DataFrame(req_data, index=["name"])

        station_datum_urls.append(np.nan)

        extra_urls.append(np.nan)

    if index == 0:
        combine_df = tmp_df
    else:
        combine_df = pd.concat([combine_df, tmp_df], ignore_index=True)

#We are going to combine this with the datum_metadata we cleaned up above.
datum_metadata = datum_metadata.join(combine_df, how="outer")
#And add Datum Info... We are going to save extra_urls for the Master List
datum_metadata["DATUM INFO"] = station_datum_urls

mask = datum_metadata['DATA SOURCE'] == 'Tide'
datum_metadata.loc[mask, ['MHHW', 'MHW', 'MTL', 'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29']] *= -1
datum_metadata.replace(-0.0, 0, inplace=True)
sys.exit(0)
#%%
# =============================================================================
#Now we are going to try to fill and datum conversions which are blank, using vdatum
#  if possible
## WE DON"T WANT TO DO THIS AND MIX THE TWO....
#datum_metadata = convert_from_ref_datum(datum_metadata)
save_df3 = datum_metadata.copy()
# =============================================================================
# =============================================================================
#Now that's all done, let's save a copy that will be used by the master list

#We'll use a copy of that for the datum sheet, we will drop the columns we don't want
ahps_datum = df_cms.copy()


ahps_datum = ahps_datum.drop(['AHPS NAME', 'PROXIMITY', 'RIVER WATERBODY NAME',
       'LOCATION TYPE', 'USGS ID', 'LATITUDE', 'LONGITUDE', 'WFO', 'RFC',
       'STATE', 'COUNTY', 'HUC2', 'TIME ZONE', 'INUNDATION', 'COEID',
       'PEDTS', 'IN SERVICE', 'HYDROGRAPH',
       'LOW WATER THRESHOLD VALUE / UNITS', 'FORECAST STATUS',
       'DISPLAY LOW WATER IMPACTS', 'LOW FLOW DISPLAY',
       'GIVE DATA ATTRIBUTION', 'ATTRIBUTION WORDING', 'FEMA WMS',
       'PROBABILISTIC SITE', 'WEEKLY CHANCE PROBABILISTIC ENABLED',
       'SHORT-TERM PROBABILISTIC ENABLED',
       'CHANCE OF EXCEEDING PROBABILISTIC ENABLED'], axis=1)

#Then join it with the cleaned up datum_metadata dataframe
all_datums = pd.merge(datum_metadata, ahps_datum, on="NWSLI", how="left")

#and add station urls back to the station ID... at this point we won't want to
#  reference all_datums again for iteration purposes
all_datums["Station ID"] = station_info_urls_with_ids

#Then reorder the columns to match what we want...
df_order2 = ['NWSLI', 'WFO', 'RFC', 'NWS REGION', 'COUNTYNAME', 'STATE', 'TIME ZONE',
            'STATION ID','LONGITUDE', 'LATITUDE', 'SITE TYPE', 'DATA SOURCE', 'USGS STATION NUMBER', 
            'VDATUM REGIONS', 'DATUM INFO', 'REF_DATUM', 'MHHW', 'MHW', 'MTL',
            'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29', 'LMSL',
            'nrldb vertical datum name', 'nrldb vertical datum', 'navd88 vertical datum',
            'ngvd29 vertical datum', 'msl vertical datum', 'other vertical datum',
            'elevation', 'action stage', 'flood stage', 'moderate flood stage',
            'major flood stage', 'flood stage unit']

all_datums = all_datums.reindex(columns=df_order2)

all_datums.columns = map(str.upper, all_datums.columns)

# =============================================================================
#SAVE DATA
all_datums.to_excel(writer, index=False, sheet_name='Tidal Datum Offsets')
Datums_Excel = writer.sheets['Tidal Datum Offsets']
Datums_Excel = format_excel(all_datums, Datums_Excel, styles)
writer.save()

#%%
sys.exit(0)

# =============================================================================
# JOIN HADS+AHPS METADATA TO STATION_METADATA -- CLEAN UP
# =============================================================================
#%%
# =============================================================================
# NEXT STEP -- CREATE A MASTER LIST WITH THE 2 SAVED Dataframes
# =============================================================================

#all_metadata = pd.merge(save_df, save_df2, on="NWSLI", how="left")
all_metadata = save_df.copy()
#Now add in the Extra Metadata links
all_metadata["Station Info"] = station_info_urls
all_metadata["Datum Info"] = station_datum_urls
all_metadata["Extra Metadata"] = extra_urls

drop_from_df3 = ['NWSLI', 'WFO', 'RFC', 'NWS REGION', 'COUNTYNAME', 'STATE', 'TIME ZONE',
       'Longitude', 'Latitude', 'Station ID', 'Site Type', 'Data Source',
       'VDatum Regions', 'Datum Info']

save_df3 = save_df3.drop(columns=drop_from_df3)
all_metadata = all_metadata.join(save_df3, how="outer")

# =============================================================================
# CLEAN UP
# =============================================================================
#Reorder to match how we want the output
reindex_metadata = ['NWSLI', 'WFO', 'RFC', 'NWS REGION', 'COUNTYNAME', 'STATE', 'TIME ZONE',
        'River Waterbody Name', 'HUC2', 'Location Name', 'AHPS Name',
        'Longitude', 'Latitude', 'Station ID', 'Site Type', 'Data Source',
        "Station Info", "Datum Info", "Extra Metadata",
        'Node', 'Correction', 'Domain', 'VDatum Regions', 'Ref_Datum', 'MHHW', 'MHW',
        'MTL', 'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',"LMSL",\
        'NAVD88 TO MLLW', 'NAVD88 TO MHHW',
        'nrldb vertical datum name', 'nrldb vertical datum',
        'navd88 vertical datum', 'ngvd29 vertical datum', 'msl vertical datum',
        'other vertical datum', 'elevation', 'action stage', 'flood stage',
        'moderate flood stage', 'major flood stage', 'flood stage unit',
        'Hydrograph']

all_metadata = all_metadata.reindex(columns=reindex_metadata)

#create the hyperlinks for the Hydrograph pages
for index2,row2 in all_metadata.iterrows():
    if not pd.isna(row2["Hydrograph"]):
        all_metadata.at[index2, "Hydrograph"] = create_hyperlink(row2["Hydrograph"], "AHPS Data")

#Add back in the urls for VDatum and the blank cells
all_metadata["VDATUM - MLLW"] = df_converted["VD NAVD88 - MLLW"]
all_metadata["VDATUM - MHHW"] = df_converted["VD NAVD88 - MHHW"]

all_metadata["VDATUM LATITUDE"] = ''
all_metadata["VDATUM LONGITUDE"] = ''
all_metadata["VDATUM HEIGHT"] = ''
all_metadata["VDATUM TO MLLW"] = ''
all_metadata["VDATUM TO MHHW"] = ''
all_metadata["COMMENTS"] = ''

#%%
# create a Pandas Excel writer using XlsxWriter engine

# write the DataFrame to the Excel file
all_metadata.to_excel(writer, index=False, sheet_name='Master List')
Master_Sheet = writer.sheets['Master List']
Master_Sheet = format_excel(all_metadata, Master_Sheet, styles, hyper_id=False)
#%%
# =============================================================================
# ## LAST STEP - CREATE A SHEET WITH ONLY MISSING VALUES SO WE CAN QC MANUALLY LATER
# =============================================================================
errors_only = all_metadata.loc[(all_metadata['NAVD88 TO MHHW'] == -999999) |\
                               (all_metadata['NAVD88 TO MLLW'] == -999999)]

#columns we want to drop
cols_2_drop = ['TIME ZONE',
        'River Waterbody Name', 'HUC2', 'Location Name', 'AHPS Name',
        'Node', 'Correction', 'Domain', 'VDatum Regions', 'Ref_Datum', 'MHHW', 'MHW',
        'MTL', 'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',"LMSL",\
        'NAVD88 TO MLLW', 'NAVD88 TO MHHW',
        'nrldb vertical datum name', 'nrldb vertical datum',
        'navd88 vertical datum', 'ngvd29 vertical datum', 'msl vertical datum',
        'other vertical datum', 'elevation', 'action stage', 'flood stage',
        'moderate flood stage', 'major flood stage', 'flood stage unit',
        'Hydrograph', "VDatum - MLLW", "VDatum - MHHW"]

errors_only = errors_only.drop(columns=cols_2_drop)
#Rename the columns that have bad (non-descriptive) names
errors_only = errors_only.rename(columns={'VDATUM LATITUDE':"NEW LATITUDE",\
                         "VDATUM LONGITUDE":"NEW LONGITUDE", "VDATUM HEIGHT":"NEW HEIGHT"})


# write the DataFrame to the Excel file
errors_only.to_excel(writer, index=False, sheet_name='No VDatum Estimate')
Errors_Only_Sheet = writer.sheets['No VDatum Estimate']
Errors_Only_Sheet = format_excel(errors_only, Errors_Only_Sheet, styles, hyper_id=False)
# save the Excel file
writer.save()
