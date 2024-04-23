#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 10:20:18 2023

@author: ericallen
"""
import json
from datetime import datetime
import numpy as np
import pandas as pd
import requests
from src.check_url import check_url
from src.get_urls import create_hyperlink

def get_station_flood_levels(dataframe):
    """NOS stores NOS and NWS flood levels in the flood json file, extract these and
    save to a pandas dataframe -- being built out"""
    for index, row in dataframe.iterrows():
        station_id = row["Station ID"]
        data_source = row["Data Source"]
        if data_source == "Tide":
            url = (f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/"
                   f"{station_id}/floodlevels.json")

            if check_url(url):
                data = json.loads(requests.get(url).text)
                # Replace None with NaN
                data = {k: np.nan if v is None else v for k, v in data.items()}

                # Convert the dictionary to a dataframe
                dfnos = pd.DataFrame(data, index=[0])
                dfnos = dfnos.drop(labels=["self"], axis=1)

                for column in dfnos.columns:
                    dataframe.at[index, column] = dfnos[column].values[0]

    return dataframe

def get_station_products(dataframe):
    """
    Take the pandas dataframe being built out with information about all the data/metadata
    that NOS has, in this function the focus is the products. Those products will be hyperlinked
    in the final spreadsheet that is output. Return the pandas dataframe with the hyperlinks.

    Parameters
    ----------
    dataframe : pd.df
        DESCRIPTION. original

    Returns
    -------
    dataframe : pd.df
        DESCRIPTION. With station products as hyperlinks

    """
    for index, row in dataframe.iterrows():
        station_id = row["Station ID"]
        data_source = row["Data Source"]
        if data_source == "Tide":
            url = (f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/"
                   f"{station_id}/products.json")
            data = json.loads(requests.get(url).text)
            data = data["products"]

            # Create a pandas dataframe from the data
            df_new = pd.DataFrame(data)
            #Transpose -- make a row
            df_new = df_new.T
            #Make the top row the column names
            df_new.columns = df_new.iloc[0]
            #Make the rest of the data in the data frame start at row 1
            df_new = df_new[1:]
            for column in df_new.columns:
                if "tidesandcurrents.noaa.gov" in df_new[column].value:
                    dataframe.at[index, column] = create_hyperlink(df_new[column].value, column)
                else:
                    dataframe.at[index, column] =  df_new[column].value


    return dataframe



def get_station_start_end(dataframe):
    """
    Add the start date and end date for the station (or just the start date if still active).
    Then append it to the pandas dataframe and return it.

    Parameters
    ----------
    dataframe : TYPE
        DESCRIPTION.

    Returns
    -------
    dataframe : TYPE
        DESCRIPTION.

    """
    start_dates = []
    end_dates = []
    for index, row in dataframe.iterrows():
        station_id = row["Station ID"]
        data_source = row["Data Source"]
        if data_source == "Tide":
            url = (f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/"
                   f"{station_id}/details.json")

            if check_url(url):

                data = json.loads(requests.get(url).text)

                established = data["established"].split(" ")[0]
                removed = data["removed"].split(" ")[0]

                if len(established) == 0:
                    start_dates.append(np.nan)
                else:
                    try:
                        established2 = datetime.strptime(established, "%Y-%m-%d")
                        date_obj = datetime.strftime(established2, "%Y-%m-%d")
                        start_dates.append(date_obj)

                    except:
                        print(station_id, " invalid Start:", established)

                if len(removed) == 0:
                    end_dates.append(np.nan)
                else:
                    try:
                        removed2 = datetime.strptime(removed, "%Y-%m-%d")
                        date_obj2 = datetime.strftime(removed2, "%Y-%m-%d")
                        end_dates.append(date_obj2)

                    except:
                        print(station_id, " invalid End:", removed)
            else:
                alt_url = f"https://tidesandcurrents.noaa.gov/stationhome.html?id={station_id}"

                if check_url(alt_url):
                    start_dates.append(np.nan)
                    end_dates.append(np.nan)
                else:
                    print("Error: ", station_id, " is not found")

        elif data_source == "USGS":
            start_dates.append(np.nan)
            end_dates.append(np.nan)
            station_id = station_id[2:]

            url = (f"https://waterservices.usgs.gov/nwis/site/?format=rdb&sites={station_id}"
                   f"&seriesCatalogOutput=true&outputDataTypeCd=sv&siteStatus=all")
            print(url)
            #url = (f"https://waterdata.usgs.gov/nwis/inventory?search_site_no={station_id}&"
            #       f"search_site_no_match_type=exact&group_key=NONE&format=sitefile_output&"
            #       f"sitefile_output_format=rdb&column_name=construction_dt&"
            #       f"column_name=inventory_dt&column_name=rt_bol&column_name=sv_begin_date&"
            #       f"column_name=sv_end_date&column_name=sv_count_nu&"
            #       f"list_of_search_criteria=search_site_no")

            dfusgs = pd.read_csv(url, delimiter="\t", comment="#", header=0)
            dfusgs = dfusgs.drop([0])

            to_drop = ['agency_cd', 'site_no', 'station_nm', 'site_tp_cd', 'dec_lat_va',
                   'dec_long_va', 'coord_acy_cd', 'dec_coord_datum_cd', 'alt_va',
                   'alt_acy_va', 'alt_datum_cd', 'huc_cd', 'data_type_cd', 'parm_cd',
                   'stat_cd', 'ts_id', 'loc_web_ds', 'medium_grp_cd', 'parm_grp_cd',
                   'srs_id', 'access_cd', 'count_nu']

            dfusgs = dfusgs.drop(labels=to_drop, axis=1)
            print(dfusgs)

            print(f"Station: {0} has a Begin Date: {1} and an End Date: {2}".format(station_id,\
                dfusgs["begin_date"].values[0], dfusgs["end_date"].values[0]))

            print()


        else:
            start_dates.append(np.nan)
            end_dates.append(np.nan)

    dataframe["Start Date"] = start_dates
    dataframe["End Date"] = end_dates
    return dataframe
