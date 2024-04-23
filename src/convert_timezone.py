#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 10:16:16 2023

@author: ericallen
"""
# Define a dictionary of time zone abbreviations and their corresponding pytz time zone strings
TIMEZONE_LOOKUP = {
    'AKDT': 'America/Anchorage',
    'AKST': 'America/Anchorage',
    'CDT': 'America/Chicago',
    'CST': 'America/Chicago',
    'EDT': 'America/New_York',
    'EST': 'America/New_York',
    'EST5': 'America/New_York',
    'HADT': 'America/Adak',
    'HST': 'Pacific/Honolulu',
    'HAST': 'Pacific/Honolulu',
    'MDT': 'America/Denver',
    'MST': 'America/Denver',
    'MST7': 'America/Phoenix',
    'PDT': 'America/Los_Angeles',
    'PST': 'America/Los_Angeles',
    'SST': 'Pacific/Pago_Pago',
    'ChST': 'Pacific/Guam',
    'AST': 'America/Puerto_Rico',
    'ADT': 'America/Puerto_Rico',
    'UTC': 'UTC',
    'V': 'America/Puerto_Rico',  # Atlantic Standard
    'E': 'America/New_York',  # Eastern Standard
    'C': 'America/Chicago',  # Central Standard
    'M': 'America/Denver',  # Mountain Standard
    'm': 'America/Denver',  # Mountain Standard (daylight time not observed)
    'P': 'America/Los_Angeles',  # Pacific Standard
    'A': 'America/Anchorage',  # Alaska Standard
    'H': 'Pacific/Honolulu',  # Hawaii-Aleutian Standard
    # Hawaii-Aleutian Standard (daylight time observed)
    'h': 'Pacific/Honolulu',
    'G': 'Pacific/Guam',  # Guam & Marianas
    'J': 'Asia/Tokyo',  # Japan Time
    'S': 'Pacific/Pago_Pago',  # Samoa Standard
    # Add more abbreviations and corresponding time zone strings as needed
}


def convert_tz_to_pytz(dataframe, header="TIME ZONE"):
    """
    Convert various timezone abbrivations to a universal pytz string

    Parameters
    ----------
    dataframe : dataframe
        DESCRIPTION. Contains whatever metadata
    header : str, optional
        DESCRIPTION. The default is "TIME ZONE". The column header for the dataframe.

    Returns
    -------
    dataframe : TYPE
        DESCRIPTION.

    """

    dataframe[header] = dataframe[header].apply(lambda x: TIMEZONE_LOOKUP.get(x,
                                                                              "Unknown timezone"))

    return dataframe
