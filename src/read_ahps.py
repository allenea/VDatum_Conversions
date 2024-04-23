#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 20:26:07 2023

@author: ericallen

TO CHECK THAT THE 2 PROCESSES PRODUCE THE SAME DATAFRAME

df_cms1 = read_ahps()
df_cms2 = read_ahps(option="csv")
cols_check = []
for column in df_cms1.columns:
    if not df_cms1[column].equals(df_cms2[column]):
        cols_check.append(column)
        print(column, df_cms1[column].equals(df_cms2[column]))
        print(df_cms1[column][123], df_cms2[column][123])
        print(type(df_cms1[column][123]), type(df_cms2[column][123]))
        print()
for col in cols_check:
    for idx, row in df_cms1.iterrows():
        if not row[col] == df_cms2[col][idx]:
            print(col, row["NWSLI"], idx, "!!!!", row[col], df_cms2[col][idx])
            print(col, idx, "!!!!", type(row[col]), type(df_cms2[col][idx]))
            print()
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import src.fcc_census_metadata as fcc
from src.convert_timezone import convert_tz_to_pytz

def convert_longitude(longitude, hemisphere):
    """
    AHPS database reports all longitudes in positive numbers but signify's
    the sign using the hemisphere column.

    Parameters
    ----------
    longitude : str
        DESCRIPTION. float as type str for longitude
    hemisphere : TYPE
        DESCRIPTION. W or E. W is -1 *

    Returns
    -------
    str
        DESCRIPTION. Longitude with the proper sign (+/-)

    """
    if hemisphere == 'W':
        new_lon = -1 * abs(float(longitude))
        return str(new_lon)
    return longitude

def read_ahps(option="scrape"):
    """
    Process the AHPS metadata from the web either scraping the web
    (which retains some additional useful information like the USGS ID's leading 0) or
     by downloading and reading in the csv file. Other formatting is done to meet my likeness

    Parameters
    ----------
    option : str, optional
        DESCRIPTION. The default is "scrape". Anything else results in the csv file being used

    Returns
    -------
    df_cms : dataframe
        DESCRIPTION.

    """


    ##OPTION ONE

    if option == "scrape":

        ##OPTION TWO
        url = 'http://water.weather.gov/monitor/ahps_cms_report.php'

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the table header (thead)
        header_row = soup.find('thead').find_all('th')
        header = [th.text.strip() for th in header_row]

        # Extract the table body (tbody)
        table_body = soup.find('tbody')
        rows = table_body.find_all('tr')
        data = []
        for row in rows:
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            data.append(cols)

        df_cms = pd.DataFrame(data, columns=header)

    else:
        df_cms = read_ahps_csv()

    df_cms = df_cms.rename(columns={"nws shef id": "nwsli", "timezone":"time zone"})
    df_cms.columns = map(str.upper, df_cms.columns)

    #This needs to be a string type
    df_cms["USGS ID"] = df_cms["USGS ID"].astype(str)

    df_cms["NWSLI"] = df_cms["NWSLI"].str.upper()
    df_cms["WFO"] = df_cms["WFO"].str.upper()
    df_cms["RFC"] = df_cms["RFC"].str.upper()
    df_cms["STATE"] = df_cms["STATE"].str.upper()
    df_cms["PEDTS"] = df_cms["PEDTS"].str.upper()

    df_cms = df_cms.applymap(lambda x: x.strip() if isinstance(x, str) else x)


    #Likely won't work if using the csv input
    df_cms['USGS ID'] = df_cms['USGS ID'].apply(lambda x: 'US' + x if x != '' else '')

    df_cms['LONGITUDE'] = df_cms.apply(lambda x: convert_longitude(x['LONGITUDE'],\
                                                           x['HEMISPHERE']), axis=1)

    ## REQUIRED FOR CONSISTENT FORMATTING BETWEEN THE TWO APPROACHES -- has to happen here!
    df_cms = df_cms.replace("", np.nan)
    df_cms = df_cms.replace("?", np.nan)
    df_cms = df_cms.replace("NULL", np.nan)
    df_cms = df_cms.replace("N/A", np.nan)
    df_cms = df_cms.replace("USnan", np.nan)
    df_cms = df_cms.replace("USNA", np.nan)
    df_cms = df_cms.replace("USN/A", np.nan)
    df_cms = df_cms.replace({'&#039;': '\'', '&amp;': '&'}, regex=True)
    df_cms = df_cms.applymap(lambda x: "" if pd.isna(x) else x)


    # Get the state code -> state name dictionary
    state_codes = fcc.make_lookup_state_fips()

    # Invert the dictionary so we can look up by state name
    state_names = fcc.make_reverse_lookup(state_codes)

    df_cms['STATE_FIPS'] = df_cms['STATE'].apply(lambda x: fcc.state_abbreviation_to_fips(x,\
                                                                                  state_names))


    df_cms['FULL_FIPS'] = df_cms['STATE_FIPS']+df_cms["COUNTY"]

    county_codes = fcc.make_lookup_county_fips()

    df_cms['COUNTY_NAME'] = df_cms['FULL_FIPS'].apply(lambda x: fcc.get_county_name_from_fips(x,\
                                                                                  county_codes))

    # Use apply() with a lambda function to convert the time zone abbreviations
    # to pytz time zone strings
    print("ALL AHPS Time Zones: ", list(set(df_cms["TIME ZONE"])))
    df_cms = convert_tz_to_pytz(df_cms, header="TIME ZONE")

    df_cms = df_cms.drop(labels=["STATE_FIPS", "FULL_FIPS", "COUNTY", 'HEMISPHERE'],\
                         axis=1)

    df_cms = df_cms.rename(columns={'RIVER/WATER-BODY NAME':"RIVER WATERBODY NAME", "WRR":"HUC2",\
                                    "LOCATION NAME":"AHPS NAME", "HYDROGRAPH PAGE":"HYDROGRAPH",\
                                    "COUNTY_NAME":"COUNTY"})

    return df_cms

def read_ahps_csv():
    """
    reads in the ahps csv file

    Returns
    -------
    df_cms : dataframe
        DESCRIPTION. dataframe for AHPS cms

    """
    url = "https://water.weather.gov/monitor/ahps_cms_report.php?type=csv"
    dtypes = {
        "location name": str,
        "proximity": str,
        "river/water-body name": str,
        "nws shef id": str,
        "location type": str,
        "usgs id": str,
        "latitude": str,
        "longitude": str,
        "wfo": str,
        "rfc": str,
        "state": str,
        "county": str,
        "wrr": str,
        "timezone": str,
        "inundation": str,
        "elevation": str,
        "action stage": str,
        "flood stage": str,
        "moderate flood stage": str,
        "major flood stage": str,
        "flood stage unit": str,
        "coeid": str,
        "hydrograph page": str,
        "pedts": str,
        "in service": str,
        "hemisphere": str,
        "low water threshold value / units": str,
        "forecast status": str,
        "display low water impacts": str,
        "low flow display": str,
        "give data attribution": str,
        "attribution wording": str,
        "fema wms": str,
        "probabilistic site": str,
        "weekly chance probabilistic enabled": str,
        "short-term probabilistic enabled": str,
        "chance of exceeding probabilistic enabled": str,
        "nrldb vertical datum name": str,
        "nrldb vertical datum": str,
        "navd88 vertical datum": str,
        "ngvd29 vertical datum": str,
        "msl vertical datum": str,
        "other vertical datum": str,
    }
    df_cms = pd.read_csv(url, dtype=dtypes)
    return df_cms
