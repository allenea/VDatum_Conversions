#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 13:37:21 2023

@author: ericallen
"""
import numpy as np

def check_url_len(url):
    """


    Parameters
    ----------
    url : TYPE
        DESCRIPTION.

    Returns
    -------
    url : TYPE
        DESCRIPTION.

    """
    if len(url) <= 255:
        return url
    return None

def get_station_info_urls(station_id, source="NOS"):
    """


    Parameters
    ----------
    station_id : TYPE
        DESCRIPTION.
    source : TYPE, optional
        DESCRIPTION. The default is "NOS".

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    if source.upper() == "NOS":
        #f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station_id}.json"
        return f"https://tidesandcurrents.noaa.gov/stationhome.html?id={station_id}"

    if source.upper() == "USGS":
        return f"https://waterdata.usgs.gov/nwis/nwismap/?site_no={station_id}&agency_cd=USGS"

    return np.nan

def extra_link(station_id):
    """


    Parameters
    ----------
    station_id : TYPE
        DESCRIPTION.

    Returns
    -------
    str
        DESCRIPTION.

    """
    return f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station_id}.json"



def get_station_datum_urls(station_id, source="NOS", ref_datum=None, fmt="rdb"):
    """


    Parameters
    ----------
    station_id : TYPE
        DESCRIPTION.
    source : TYPE, optional
        DESCRIPTION. The default is "NOS".
    ref_datum : TYPE, optional
        DESCRIPTION. The default is None.
    fmt : TYPE, optional
        DESCRIPTION. The default is "rdb".

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    if source.upper() == "NOS":
        if fmt.upper() == "API":
            return (f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/"
                    f"stations/{station_id}/datums.json")

        return (f"https://tidesandcurrents.noaa.gov/datums.html?datum={ref_datum}&"
                f"units=0&epoch=0&id={station_id}")

    if source.upper() == "USGS":
        return f"https://waterservices.usgs.gov/nwis/site/?site={station_id}&format={fmt}"

    return np.nan

def create_hyperlink(url, display_text):
    """


    Parameters
    ----------
    url : TYPE
        DESCRIPTION.
    display_text : TYPE
        DESCRIPTION.

    Returns
    -------
    str
        DESCRIPTION.

    """
    if check_url_len(url) is not None:
        return f'=HYPERLINK("{url}", "{display_text}")'

    print("URL Exceeds Excel Hyperlink URL Length of 255 Characters")
    return np.nan
