#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 13:37:21 2023

@author: ericallen
"""

def check_url_len(url):
    """
    Check the length of a given URL and return it if it is less than or equal to 255 characters.

    Parameters
    ----------
    url : str
        The URL to check the length of.

    Returns
    -------
    str or None
        The input URL if it is less than or equal to 255 characters, otherwise None.
    """
    if len(url) <= 255:
        return url

    print(f"URL: '{url}' exceeds the maximum allowed length of 255 characters.")
    return None

def get_station_info_urls(station_id, source="NOS"):
    """
    Get the link for additional information about the station

    Parameters
    ----------
    station_id : str
        DESCRIPTION.
    source : str, optional
        DESCRIPTION. The default is "NOS".

    Returns
    -------
    url: str
        DESCRIPTION. the url with station information

    """
    if source.casefold() == "nos":
        #This returns f"https://tidesandcurrents.noaa.gov/stationhome.html?id={station_id}"
        #return extra_link(station_id, api=False)
        return f"https://tidesandcurrents.noaa.gov/stationhome.html?id={station_id}"

    if source.casefold() == "usgs":
        return f"https://waterdata.usgs.gov/nwis/nwismap/?site_no={station_id}&agency_cd=USGS"

    return None


def extra_link(station_id, api=True):
    """
    Generate a link to the NOAA API or webpage for a given station ID to obtain additional
    information, if you are using the API it has decimal lat/lon and links to other data.

    Parameters
    ----------
    station_id : str
        Station ID for the desired NOAA station.
    api : bool, optional
        If True, generate the link to the NOAA API. Otherwise, generate the
        link to the NOAA station webpage. The default is False.

    Returns
    -------
    str
        A URL for the given station ID.

    """
    if api:
        return f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/{station_id}.json"

    return f"https://tidesandcurrents.noaa.gov/stationhome.html?id={station_id}"



def get_station_datum_urls(station_id, source="NOS", ref_datum=None, fmt="rdb"):
    """
    Generate URL for accessing station datum information.

    Parameters
    ----------
    station_id : str
        Station identifier.
    source : str, optional
        Source of the station data. Either "NOS" or "USGS". Default is "NOS".
    ref_datum : str, optional
        Reference datum for the station. Required for NOS source. Default is None.
    fmt : str, optional
        Format of the data. Required for USGS source. Default is "rdb".

    Returns
    -------
    str
        The URL for accessing the station datum information.

    Raises
    ------
    ValueError
        If the source is not supported.
    """
    if source.casefold() == "nos":
        if ref_datum is None:
            raise ValueError("For NOS source, ref_datum parameter is required.")

        if fmt.casefold() == "api":
            url = (f"https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations/"
                   f"{station_id}/datums.json")
        else:
            url = (f"https://tidesandcurrents.noaa.gov/datums.html?datum={ref_datum}&units=0&"
                   f"epoch=0&id={station_id}")

    elif source.casefold() == "usgs":

        acceptable_fmts = ["rdb", "rdb,1.0", "gm", "gm,1.0", "ge", "ge,1.0", "mapper", "mapper,1.0"]

        if fmt.casefold() not in acceptable_fmts:
            raise ValueError((f"For USGS source, fmt parameter is required and {fmt}"
                             f"should be one of {acceptable_fmts}."))

        url = f"https://waterservices.usgs.gov/nwis/site/?site={station_id}&format={fmt}"

    else:
        raise ValueError(f"Unsupported source: {source}")

    return url


def create_hyperlink(url, display_text):
    """
    creates a hyperlink formula for the excel output

    Parameters
    ----------
    url : str
        DESCRIPTION. the url being hyperlinked
    display_text : str
        DESCRIPTION. the text displayed for the hyperlink

    Returns
    -------
    str
        DESCRIPTION. Hyperlink formula

    """
    if not url:
        raise ValueError("url parameter cannot be empty.")

    if not display_text:
        raise ValueError("display_text parameter cannot be empty.")

    if check_url_len(url) is not None:
        return f'=HYPERLINK("{url}", "{display_text}")'

    print("URL Exceeds Excel Hyperlink URL Length of 255 Characters")
    return None
