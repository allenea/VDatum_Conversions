#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 17:32:07 2023

@author: ericallen
"""
import sys
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

DATA_NOS = {'Ref_Datum':np.nan, 'MHHW':np.nan, 'MHW':np.nan, 'MTL':np.nan,\
            'MSL':np.nan, 'DTL':np.nan, 'MLW':np.nan, 'MLLW':np.nan,\
                'NAVD88':np.nan, 'STND':np.nan, "NGVD29":np.nan}

ALT_DATUMS = ['MLLW', 'NAVD88','MHHW', 'MSL', 'STND']

FILTER_LIST = [None, 'GT', 'MN', 'DHQ', 'DLQ', 'HWI', 'LWI', 'Max Tide',\
             'Max Tide Date & Time', 'Min Tide', 'Min Tide Date & Time',\
              'HAT', 'HAT Date & Time', 'LAT', 'LAT Date & Time']

def grab_nos_data(stid, ref_datum="MLLW", source="web", first=True):
    """
    This is a Python script that scrapes tide data from the National Oceanic and
    Atmospheric Administration (NOAA) website. The script uses the BeautifulSoup
    library to parse the HTML content of the website and extract the data from
    the table. The extracted data is then stored in a pandas DataFrame, which is
    a two-dimensional size-mutable, heterogeneous tabular data structure with
    labeled axes (rows and columns).

    The script can also make a request to the API provided by the NOAA to obtain
    the same data. The data obtained from the API is in JSON format, and the script
    uses the requests library to make the API call and the json library to parse
    the JSON data.

    The function grab_nos_data takes two arguments:

    stid: the station ID for which you want to obtain the tide data
    ref_datum (optional): the reference datum (default value is "MLLW")
    source (optional): the source of the data, either "web" or "api" (default value is "web")
    The function returns a pandas DataFrame that contains the tide data for the
    specified station and reference datum. If there is no data available, an
    empty DataFrame is returned, and a message is printed indicating that there
    is no data available.

        Parameters
        ----------
        stid : TYPE
            DESCRIPTION.
        ref_datum : TYPE, optional
            DESCRIPTION. The default is "MLLW".
        source : TYPE, optional
            DESCRIPTION. The default is "web".

        Returns
        -------
        df_nos : TYPE
            DESCRIPTION.

    """
    ref_datum_out = ref_datum

    if source == "web":
        url = (f"https://tidesandcurrents.noaa.gov/datums.html?"
               f"datum={ref_datum}&units=0&epoch=0&id={stid}")

        # Send a request to the website
        res = requests.get(url)

        # Parse the HTML content of the website
        soup = BeautifulSoup(res.content, 'html.parser')

        # Find the table in the HTML content
        table = soup.find('table')

        try:
            # Extract the data from the table - if table is missing w.o. try/except program breaks
            data = []
            for row in table.find_all('tr'):
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])

            # Create a pandas dataframe from the data
            df_nos = pd.DataFrame(data, columns=["name", "value", "description"])
            #This drops strings and times
            df_nos["value"] = pd.to_numeric(df_nos["value"], errors="coerce")
            #drop the long description
            df_nos = df_nos.drop(["description"], axis=1)
            #Transpose -- make a row
            df_nos = df_nos.T
            #Make the top row the column names
            df_nos.columns = df_nos.iloc[0]
            #Make the rest of the data in the data frame start at row 1
            df_nos = df_nos[1:]

            #Drop columns we aren't using
            drop_list = df_nos.filter(FILTER_LIST)
            df_nos.drop(drop_list, inplace=True, axis=1)
            #Insert the datum being used as a reference point or 0-point
            df_nos.insert(loc=0, column="Ref_Datum", value=ref_datum)

        except:
            print("NO DATA AVAILABLE ON THE WEB FOR: ", stid)
            df_nos = pd.DataFrame(DATA_NOS, index=["name"])
            df_nos["Ref_Datum"] = np.nan

        df_nos = df_nos.reindex(columns=list(DATA_NOS.keys()))

        #This only applied to web data since API is only ever STND (except it says NAVD88)
        count = 0
        if first and pd.isna(df_nos[ref_datum]).values[0] and df_nos["STND"].values[0] == 0:
            while count < len(ALT_DATUMS):
                df_nos, ref_datum_out = grab_nos_data(stid, ref_datum=ALT_DATUMS[count],\
                                                      source="web", first=False)
                if not pd.isna(df_nos[ALT_DATUMS[count]]).values[0]:
                    print(f"{ref_datum} is unavailable but {ref_datum_out} is available")
                    break
                count +=1

    elif source == "api":
        #FEET
        api_url = (f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/"
                   f"stations/{stid}/datums.json")

        data = json.loads(requests.get(api_url).text)

        try:
            metadata = data['datums']
            df_nos = pd.DataFrame.from_dict(metadata)
        except:
            df_nos = pd.DataFrame()
            print("BAD NOS STATION API REQUEST: ", stid)

        if df_nos.empty:
            df_nos = pd.DataFrame(DATA_NOS, index=["name"])
            df_nos["Ref_Datum"] = np.nan

        else:
            df_nos = df_nos.drop("description", axis=1)
            df_nos = df_nos.set_index("name")
            df_nos = df_nos.T
            #Drop columns we aren't using
            drop_list = df_nos.filter(FILTER_LIST)
            df_nos.drop(drop_list, inplace=True, axis=1)
            df_nos.insert(loc=0, column="Ref_Datum", value=data["OrthometricDatum"])

        df_nos = df_nos.reindex(columns=list(DATA_NOS.keys()))

    else:
        sys.exit("Invalid source type for get_nos_data, the options are web and api.")

    return df_nos, ref_datum_out
