# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 15:56:13 2023

@author: ericallen
"""
import pandas as pd
import numpy as np

DATA_USGS = {"Ref_Datum":np.nan, 'MHHW':np.nan, 'MHW':np.nan, 'MTL':np.nan,\
             'MSL':np.nan, 'DTL':np.nan, 'MLW':np.nan, 'MLLW':np.nan,\
             'NAVD88':np.nan, 'STND':np.nan, "NGVD29":np.nan}

def grab_usgs_data(stid):
    """
    This function retrieves tidal and current conversion data from the USGS (United States
         Geological Survey) API for a given station identifier. The function takes in a
         station identifier (stid) as an input and outputs a pandas DataFrame with the
         conversion data.

    The function first converts the station identifier to a "short_id" by removing the
        "US/USGS" text from the front of the identifier. The API URL is then constructed
        using the short_id and a data request is sent to the API. The returned data is
        stored in a pandas DataFrame and some cleaning is performed on the data to remove
        unnecessary columns and rows with missing data.

    The cleaned data is then added to a copy of a predefined dictionary (DATA_USGS) to
        form a new DataFrame. The new DataFrame contains the reference datum and conversions
        from various tidal levels to the given reference datum. If the cleaned data is empty,
        a DataFrame is returned with all values set to NaN.

    {0} = site id without US/USGS text in front
    https://waterservices.usgs.gov/nwis/site/?site={0}&format=rdb"


    #  agency_cd       -- Agency
    #  site_no         -- Site identification number
    #  station_nm      -- Site name
    #  site_tp_cd      -- Site type
    #  dec_lat_va      -- Decimal latitude
    #  dec_long_va     -- Decimal longitude
    #  coord_acy_cd    -- Latitude-longitude accuracy
    #  dec_coord_datum_cd -- Decimal Latitude-longitude datum
    #  alt_va          -- Altitude of Gage/land surface
    #  alt_acy_va      -- Altitude accuracy
    #  alt_datum_cd    -- Altitude datum
    #  huc_cd          -- Hydrologic unit code

    Possible Datums:
        Code    Name    Explanation
        NGVD29    V Datum of 1929    National Geodetic Vertical Datum of 1929
        NAVD88    V Datum of 1988    North American Vertical Datum of 1988
        OLDAK    Old Alaska    Old Alaska (Mainland) and Aleutian Island Datum
        OLDPR    Old PR & VI    Old Puerto Rico and Virgin Island Datum
        HILOCAL    Hawaii Local    Local Hawaiian Datum
        GUVD04    Guam Datum    Guam Vertical Datum of 2004
        ASVD02    Am Samoa Datum    American Samoa Vertical Datum of 2002
        NMVD03    N Marianas Datum    Northern Marianas Vertical Datum of 2003
        TIDELOCAL    Tidal Local    Local Tidal Datum
        COE1912    COE Datum 1912    U.S. Corps of Engineers datum adjustment 1912
        IGLD    Gr Lakes Datum    International Great Lakes Datum
        ASLOCAL    *Am Samoa Local    Local American Samoa Datum
        GULOCAL    *Guam Local    Local Guam Datum

    Parameters
    ----------
    stid : TYPE
        DESCRIPTION.

    Returns
    -------
    usgs_df : TYPE
        DESCRIPTION.

    """
    short_id = stid[2:]
    # Ping the USGS API for data - data in feet
    api_url = f"https://waterservices.usgs.gov/nwis/site/?site={short_id}&format=rdb"
    skiprows = list(range(0,29))
    read_usgs = pd.read_csv(api_url, sep="\t", skiprows=skiprows)
    try:
        read_usgs = read_usgs.drop([0])
        read_usgs = read_usgs.drop(['agency_cd', 'station_nm', 'site_tp_cd', 'dec_lat_va',\
               'dec_long_va', 'coord_acy_cd', 'dec_coord_datum_cd', 'huc_cd'], axis=1)
        read_usgs = read_usgs.dropna()
    except:
        print("ERROR: " + api_url)
        read_usgs = pd.DataFrame()

    if read_usgs.empty:
        usgs_df = pd.DataFrame(DATA_USGS, index=["name"])

    else:
        data2 = DATA_USGS.copy()
        data2[read_usgs["alt_datum_cd"].values[0]]=read_usgs["alt_va"].values[0]
        data2["Ref_Datum"] = read_usgs["alt_datum_cd"].values[0]
        usgs_df = pd.DataFrame(data2, index=["name"])

    return usgs_df

# =============================================================================
# df = pd.read_excel(os.path.join(os.getcwd(), "Obs_Locations_Request.xlsx"), header=0)
# for index, row in df.iterrows():
#     station_id = row["Station ID"]
#     if row["Data Source"] == "USGS":
#         tmp_df = grab_usgs_data(station_id)
#         print(station_id, "\n", tmp_df)
#     else:
#         pass
#
# =============================================================================
