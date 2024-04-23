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
from src.excel_formatting import init_styles, format_excel

# =============================================================================
# SETUP Excel Spreadsheet and Workbook Objects
# =============================================================================
writer = pd.ExcelWriter('NWM_TWL_Forecast_Locations_SciEval.xlsx', engine='xlsxwriter')
workbook, styles  = init_styles(writer.book)
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
master_list_start = pd.read_excel(os.path.join(path, "Obs_Location_Requests_Science_Eval.xlsx"),\
                                                                                  header=0)
master_list_start = master_list_start.drop(["Region", "RFC"], axis=1)
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
location_metadata = pd.merge(nws_data, master_list_start, on="NWSLI", how="inner")

vdatum_regions = assign_regions_vdatum(location_metadata)
location_metadata["VDatum Regions"] = vdatum_regions

#Sort then reser the index so that it is like 0,1,2,3, etc.
location_metadata = location_metadata.sort_values(['NWS REGION', 'WFO', 'Station ID'])
location_metadata = location_metadata.reset_index(drop=True)

#Do the datum conversion for the model, NAVD88 to MLLW assuming water level/station = 0
df_converted, url_list_mllw = convert_datums(location_metadata, input_v="NAVD88",\
                                        output_v="MLLW", input_height=0.0)

df_converted, url_list_mhhw = convert_datums(df_converted, input_v="NAVD88",\
                                         output_v="MHHW", input_height=0.0)

df_converted["VDatum - MLLW"] = url_list_mllw
df_converted["VDatum - MHHW"] = url_list_mhhw

df_converted["VDATUM Latitude"] = ''
df_converted["VDATUM Longitude"] = ''
df_converted["VDATUM Height"] = ''
df_converted["VDATUM to MLLW"] = ''
df_converted["VDATUM to MHHW"] = ''
df_converted["Comments"] = ''

df_col_order = ['NWSLI', 'WFO', 'RFC', 'NWS REGION', 'COUNTYNAME', 'STATE', 'TIME ZONE',\
                'Longitude', 'Latitude', 'Station ID', 'Site Type', 'Data Source','Node',\
                'Correction', 'Domain', 'VDatum Regions','NAVD88 to MLLW', 'NAVD88 to MHHW',\
                'VDatum - MLLW', 'VDatum - MHHW', 'VDATUM Latitude',\
                'VDATUM Longitude', 'VDATUM Height', 'VDATUM to MLLW', 'VDATUM to MHHW',\
                'Comments']

df_converted = df_converted.reindex(columns=df_col_order)

## Create the hyperlinks for station information -- will link with Station ID for now
station_info_urls_with_ids = []
station_info_urls = []
for index, row in df_converted.iterrows():
    station_id = row["Station ID"]
    if row["Data Source"] == "USGS":
        stid_short = station_id[2:]
        station_info_urls_with_ids.append(create_hyperlink(get_station_info_urls(stid_short,\
                                                        source="USGS"), station_id))

        station_info_urls.append(create_hyperlink(get_station_info_urls(stid_short,\
                                                        source="USGS"), "Station Info"))
    elif row["Data Source"] == "Tide":
        station_info_urls_with_ids.append(create_hyperlink(get_station_info_urls(station_id,\
                                                    source="NOS"), station_id))

        station_info_urls.append(create_hyperlink(get_station_info_urls(station_id,\
                                                    source="NOS"), "Station Info"))
    elif station_id is None:
        station_info_urls_with_ids.append(str("None"))
        station_info_urls.append(np.nan)

    else:
        station_info_urls_with_ids.append(station_id)
        station_info_urls.append(np.nan)


#Save a copy before making all the Station ID's hyperlinks, required for later steps
save_df = df_converted.copy()

#Now replace the Station ID column with the hyperlinks
df_converted["Station ID"] = station_info_urls_with_ids
# =============================================================================
#SAVE DATA -- NWM List of Stations
df_converted.to_excel(writer, index=False, sheet_name='NWM List with Conversions')
NWC_List_Excel = writer.sheets['NWM List with Conversions']
NWC_List_Excel = format_excel(df_converted, NWC_List_Excel, styles)
# =============================================================================
#%% Now we are going to get the datum information for each gage location
#We only want to use a copy of save_df
datum_metadata = save_df.copy()
#And drop things we don't need for this sheet
datum_metadata = datum_metadata.drop(['Node', 'Correction', 'Domain', 'NAVD88 to MLLW',
                'NAVD88 to MHHW', 'VDatum - MLLW', 'VDatum - MHHW', 'VDATUM Latitude',
                'VDATUM Longitude', 'VDATUM Height', 'VDATUM to MLLW', 'VDATUM to MHHW',
                'Comments'], axis=1)

#Now we are going to collect the station datum data and the urls and extra urls that tell
# us more information about the data
station_datum_urls = []
extra_urls = []
for index, row in datum_metadata.iterrows():

    station_id = row["Station ID"]

    if row["Data Source"] == "USGS":
        stid_short = station_id[2:]
        tmp_df, api_url = grab_usgs_data(stid_short)

        station_datum_urls.append(create_hyperlink(api_url, "Datum Info"))

        extra_urls.append(np.nan)

    elif row["Data Source"] == "Tide":
        tmp_df, ref_datum_nos = grab_nos_data(station_id, ref_datum="MLLW", source="web")

        station_datum_urls.append(create_hyperlink(get_station_datum_urls(station_id,\
                        source="NOS", ref_datum=ref_datum_nos, fmt="web"), "Datum Info"))

        extra_urls.append(create_hyperlink(extra_link(station_id), "More Info"))

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
datum_metadata["Datum Info"] = station_datum_urls
# =============================================================================
#Now we are going to try to fill and datum conversions which are blank, using vdatum
#  if possible
## WE DON"T WANT TO DO THIS AND MIX THE TWO....
#datum_metadata = convert_from_ref_datum(datum_metadata)
save_df3 = datum_metadata.copy()
# =============================================================================
### NEXT STEP.... we want to get the AHPS datum information and add that to the end
# both of the ahps_cms and usgs_hads information will go into the master list...
# however, as stated we will include the AHPS_CMS datum information for the datum sheet.
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
# =============================================================================
#JOIN THESE 2 SETS OF DATA
new_df = pd.merge(df_hads, df_cms, on="NWSLI", how="left")

#Drop columns we don't care about -- these are the columns
columns_to_drop = ['GOES Identifer', 'latitude_x',
       'longitude_x', 'proximity', 'location type', 'usgs id', 'latitude_y',
       'longitude_y', 'inundation', 'coeid', 'pedts', 'in service', 'hemisphere',
       'low water threshold value / units', 'forecast status',
       'display low water impacts', 'low flow display',
       'give data attribution', 'attribution wording', 'fema wms',
       'probabilistic site', 'weekly chance probabilistic enabled',
       'short-term probabilistic enabled',
       'chance of exceeding probabilistic enabled']

new_df = new_df.drop(columns_to_drop, axis=1)

#Rename the columns that have bad (non-descriptive) names
new_df = new_df.rename(columns={'river/water-body name':"River Waterbody Name",\
                         "wrr":"HUC2", "Location":"Location Name", "location name":"AHPS Name",\
                             "hydrograph page":"Hydrograph"})

# =============================================================================
#Now that's all done, let's save a copy that will be used by the master list
save_df2 = new_df.copy()

#We'll use a copy of that for the datum sheet, we will drop the columns we don't want
ahps_datum = save_df2.copy()
ahps_datum = ahps_datum.drop(['Location Name', 'AHPS Name', 'River Waterbody Name',\
                              'HUC2', 'Hydrograph'], axis=1)

#Then join it with the cleaned up datum_metadata dataframe
all_datums = pd.merge(datum_metadata, ahps_datum, on="NWSLI", how="left")

#and add station urls back to the station ID... at this point we won't want to
#  reference all_datums again for iteration purposes
all_datums["Station ID"] = station_info_urls_with_ids

#Then reorder the columns to match what we want...
df_order2 = ['NWSLI', 'WFO', 'RFC', 'NWS REGION', 'COUNTYNAME', 'STATE', 'TIME ZONE',
            'Station ID','Longitude', 'Latitude', 'Site Type', 'Data Source', 'USGS Station Number', 
            'VDatum Regions', 'Datum Info', 'Ref_Datum', 'MHHW', 'MHW', 'MTL',
            'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29', 'LMSL',
            'nrldb vertical datum name', 'nrldb vertical datum', 'navd88 vertical datum',
            'ngvd29 vertical datum', 'msl vertical datum', 'other vertical datum',
            'elevation', 'action stage', 'flood stage', 'moderate flood stage',
            'major flood stage', 'flood stage unit']

all_datums = all_datums.reindex(columns=df_order2)

# =============================================================================
#SAVE DATA
all_datums.to_excel(writer, index=False, sheet_name='Tidal Datums')
Datums_Excel = writer.sheets['Tidal Datums']
Datums_Excel = format_excel(all_datums, Datums_Excel, styles)

# =============================================================================
# JOIN HADS+AHPS METADATA TO STATION_METADATA -- CLEAN UP
# =============================================================================
#%%
# =============================================================================
# NEXT STEP -- CREATE A MASTER LIST WITH THE 2 SAVED Dataframes
# =============================================================================

all_metadata = pd.merge(save_df, save_df2, on="NWSLI", how="left")
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
        'NAVD88 to MLLW', 'NAVD88 to MHHW',
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
all_metadata["VDatum - MLLW"] = url_list_mllw
all_metadata["VDatum - MHHW"] = url_list_mhhw

all_metadata["VDATUM Latitude"] = ''
all_metadata["VDATUM Longitude"] = ''
all_metadata["VDATUM Height"] = ''
all_metadata["VDATUM to MLLW"] = ''
all_metadata["VDATUM to MHHW"] = ''
all_metadata["Comments"] = ''

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
errors_only = all_metadata.loc[(all_metadata['NAVD88 to MHHW'] == -999999) |\
                               (all_metadata['NAVD88 to MLLW'] == -999999)]

#columns we want to drop
cols_2_drop = ['TIME ZONE',
        'River Waterbody Name', 'HUC2', 'Location Name', 'AHPS Name',
        'Node', 'Correction', 'Domain', 'VDatum Regions', 'Ref_Datum', 'MHHW', 'MHW',
        'MTL', 'MSL', 'DTL', 'MLW', 'MLLW', 'NAVD88', 'STND', 'NGVD29',"LMSL",\
        'NAVD88 to MLLW', 'NAVD88 to MHHW',
        'nrldb vertical datum name', 'nrldb vertical datum',
        'navd88 vertical datum', 'ngvd29 vertical datum', 'msl vertical datum',
        'other vertical datum', 'elevation', 'action stage', 'flood stage',
        'moderate flood stage', 'major flood stage', 'flood stage unit',
        'Hydrograph', "VDatum - MLLW", "VDatum - MHHW"]

errors_only = errors_only.drop(columns=cols_2_drop)
#Rename the columns that have bad (non-descriptive) names
errors_only = errors_only.rename(columns={'VDATUM Latitude':"New Latitude",\
                         "VDATUM Longitude":"New Longitude", "VDATUM Height":"New Height"})


# write the DataFrame to the Excel file
errors_only.to_excel(writer, index=False, sheet_name='No VDatum Estimate')
Errors_Only_Sheet = writer.sheets['No VDatum Estimate']
Errors_Only_Sheet = format_excel(errors_only, Errors_Only_Sheet, styles, hyper_id=False)
# save the Excel file
writer.save()
