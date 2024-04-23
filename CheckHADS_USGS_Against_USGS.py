#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 11:12:23 2023

@author: ericallen




Tidal Stream
https://waterdata.usgs.gov/nwis/inventory?site_tp_cd=ST-TS&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=agency_cd&column_name=site_no&column_name=station_nm&column_name=site_tp_cd&column_name=dec_lat_va&column_name=dec_long_va&column_name=dec_coord_datum_cd&column_name=state_cd&column_name=county_cd&column_name=country_cd&column_name=alt_va&column_name=alt_meth_cd&column_name=alt_acy_va&column_name=alt_datum_cd&column_name=huc_cd&column_name=basin_cd&column_name=construction_dt&column_name=inventory_dt&column_name=tz_cd&column_name=local_time_fg&column_name=reliability_cd&column_name=rt_bol&column_name=gw_begin_date&column_name=gw_end_date&list_of_search_criteria=site_tp_cd



Ocean and Coastal-Ocean:
https://waterdata.usgs.gov/nwis/inventory?site_tp_cd=OC&site_tp_cd=OC-CO&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=agency_cd&column_name=site_no&column_name=station_nm&column_name=site_tp_cd&column_name=dec_lat_va&column_name=dec_long_va&column_name=dec_coord_datum_cd&column_name=state_cd&column_name=county_cd&column_name=country_cd&column_name=alt_va&column_name=alt_meth_cd&column_name=alt_acy_va&column_name=alt_datum_cd&column_name=huc_cd&column_name=basin_cd&column_name=construction_dt&column_name=inventory_dt&column_name=tz_cd&column_name=local_time_fg&column_name=reliability_cd&column_name=rt_bol&column_name=gw_begin_date&column_name=gw_end_date&list_of_search_criteria=site_tp_cd

Estuary:
https://waterdata.usgs.gov/nwis/inventory?site_tp_cd=ES&site_tp_cd=LK&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=agency_cd&column_name=site_no&column_name=station_nm&column_name=site_tp_cd&column_name=dec_lat_va&column_name=dec_long_va&column_name=dec_coord_datum_cd&column_name=state_cd&column_name=county_cd&column_name=country_cd&column_name=alt_va&column_name=alt_meth_cd&column_name=alt_acy_va&column_name=alt_datum_cd&column_name=huc_cd&column_name=basin_cd&column_name=construction_dt&column_name=inventory_dt&column_name=tz_cd&column_name=local_time_fg&column_name=reliability_cd&column_name=rt_bol&column_name=gw_begin_date&column_name=gw_end_date&list_of_search_criteria=site_tp_cd

Stream - Canal/Ditch
https://waterdata.usgs.gov/nwis/inventory?site_tp_cd=ST-CA&site_tp_cd=ST-DCH&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=agency_cd&column_name=site_no&column_name=station_nm&column_name=site_tp_cd&column_name=dec_lat_va&column_name=dec_long_va&column_name=dec_coord_datum_cd&column_name=state_cd&column_name=county_cd&column_name=country_cd&column_name=alt_va&column_name=alt_meth_cd&column_name=alt_acy_va&column_name=alt_datum_cd&column_name=huc_cd&column_name=basin_cd&column_name=construction_dt&column_name=inventory_dt&column_name=tz_cd&column_name=local_time_fg&column_name=reliability_cd&column_name=rt_bol&column_name=gw_begin_date&column_name=gw_end_date&list_of_search_criteria=site_tp_cd


Streams (not including Ditch, Canal, and Tidal Stream) has too many



https://help.waterdata.usgs.gov/codes-and-parameters/type-of-data-collected

https://help.waterdata.usgs.gov/code/agency_cd_query?fmt=rdb

https://help.waterdata.usgs.gov/code/agency_cd_query?fmt=rdb


Unique Site Types:
[nan,
 'ST-CA',
 'LK',
 'OC',
 'GW-MW',
 'LA',
 'ST-DCH',
 'FA-DV',
 'GW-CR',
 'SP',
 'AT',
 'ST-TS',
 'WE',
 'LA-SNK',
 'ST',
 'ES',
 'GW',
 'OC-CO']

https://help.waterdata.usgs.gov/code/reliability_cd_query?fmt=html
Reliability Codes:
    C - Checked by reporting agency
    L - Location Not Accurate
    M - Minimal Data
    U - Unchecked Data
    
    
Time Zone Codes
    

"""
import pandas as pd

#url = "https://waterdata.usgs.gov/nwis/inventory?site_tp_cd=ES&site_tp_cd=LK&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=agency_cd&column_name=site_no&column_name=station_nm&column_name=site_tp_cd&column_name=dec_lat_va&column_name=dec_long_va&column_name=dec_coord_datum_cd&column_name=state_cd&column_name=county_cd&column_name=country_cd&column_name=alt_va&column_name=alt_meth_cd&column_name=alt_acy_va&column_name=alt_datum_cd&column_name=huc_cd&column_name=basin_cd&column_name=construction_dt&column_name=inventory_dt&column_name=tz_cd&column_name=local_time_fg&column_name=reliability_cd&column_name=rt_bol&column_name=gw_begin_date&column_name=gw_end_date&list_of_search_criteria=site_tp_cd"

#  agency_cd       -- Agency
#  site_no         -- Site identification number
#  station_nm      -- Site name
#  site_tp_cd      -- Site type
#  dec_lat_va      -- Decimal latitude
#  dec_long_va     -- Decimal longitude
#  coord_acy_cd    -- Latitude-longitude accuracy
#  dec_coord_datum_cd -- Decimal Latitude-longitude datum
#  state_cd        -- State code
#  county_cd       -- County code
#  country_cd      -- Country code
#  alt_va          -- Altitude of Gage/land surface
#  alt_meth_cd     -- Method altitude determined
#  alt_acy_va      -- Altitude accuracy
#  alt_datum_cd    -- Altitude datum
#  huc_cd          -- Hydrologic unit code
#  basin_cd        -- Drainage basin code
#  construction_dt -- Date of first construction
#  inventory_dt    -- Date site established or inventoried
#  tz_cd           -- Mean Greenwich time offset
#  local_time_fg   -- Local standard time flag
#  reliability_cd  -- Data reliability code
#  rt_bol          -- Real-time data flag
#  gw_begin_date   -- Field water-level measurements begin date
#  gw_end_date     -- Field water-level measurements end date


# Read the data from the URL into a pandas dataframe
#df = pd.read_csv(url, delimiter="\t", comment="#", header=0)
#df = df.drop([0])


url_usgs_hads = "https://hads.ncep.noaa.gov/USGS/ALL_USGS-HADS_SITES.txt"
df_hads = pd.read_csv(url_usgs_hads, dtype=str, skiprows=4, sep="|", header=None,
                  names=["NWSLI", "USGS Station Number", "GOES Identifer", "NWS HAS",
                         "latitude", "longitude", "Location"])
df_hads["NWSLI"] = df_hads["NWSLI"].str.upper()

lst = []

for station_id in df_hads["USGS Station Number"]:
    try:
        url = f"https://waterdata.usgs.gov/nwis/inventory?search_site_no={station_id}&search_site_no_match_type=exact&group_key=NONE&format=sitefile_output&sitefile_output_format=rdb&column_name=agency_cd&column_name=site_no&column_name=station_nm&column_name=site_tp_cd&list_of_search_criteria=search_site_no"
        df = pd.read_csv(url, delimiter="\t", comment="#", header=0)
        lst.append(df["site_tp_cd"][1])
        print("HERE")
    except:
        #print("No Site Found: ", station_id)
        pass
    
    
    
    
    
    
    