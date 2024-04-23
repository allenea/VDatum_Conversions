#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 18:14:48 2023

@author: ericallen
"""
import urllib.request
import requests


def fcc_loc_metadata(lat, lon, census_year="2020", fmt="json"):
    """
    Provide coordinates and the census year and the FCC api will provide infromation
    about the location.

    Parameters
    ----------
    lat : float-string
        DESCRIPTION. Latitude (as type string)
    lon : float-string
        DESCRIPTION. Longitude (as type string)
    censusYear : str, optional
        DESCRIPTION. The default is "2020".
    fmt : str, optional
        DESCRIPTION. The default is "json".

    Returns
    -------
    dict
        DESCRIPTION. The metadata for a given coordinate per the fcc API

    """

    url = (f"https://geo.fcc.gov/api/census/area?lat={lat}&lon={lon}&",
           f"censusYear={census_year}&format={fmt}")

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        data = data['results']
        if "state_name" not in data.keys():
            print("Error: No Data Found - Offshore?")
            # do something with the response data
    else:
        print('Error:', response.status_code)

    return {data["county_fips"]: data["county_name"], data["state_fips"]: data["state_code"]}


def make_lookup_state_fips():
    """
    Obtains the national state fips codes (2 digit) from the census website

    #Special
    state_codes = {"60": "AS", "64":"FM", "66": "GU", "68": "MH", "69":"MP",
                   "70": "PW", "72": "PR", "74": "UM", "78":"VI",
                   "81": "Baker Island, UMI", "84": "Howland Island, UMI",
                   "86": "Jarvis Island, UMI", "67": "Johnston Atoll, UMI",
                   "89": "Kingman Reef, UMI", "71": "Midway Islands, UMI",
                   "76": "Navassa Island, UMI", "95": "Palmyra Atoll, UMI",
                   "79": "Wake Island, UMI"}

    Returns
    -------
    state_codes : dict
        DESCRIPTION. State codes

    """

    # Download the file
    url = 'https://www2.census.gov/geo/docs/reference/codes2020/national_state2020.txt'
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')

    # Create the dictionary
    state_codes = {}
    for line in data.splitlines():
        parts = line.split('|')
        if parts[0] == "STATE":
            continue
        state_name = parts[0]
        state_code = parts[1]
        state_codes[state_code] = state_name

    # Print the dictionary
    return state_codes


def make_lookup_county_fips():
    """
    retrieves the latest national county fips codes from the census website

    Returns
    -------
    county_codes : dict
        DESCRIPTION. dictionary of national county fips codes

    """
    # DOES NOT INCLUDE: Federated States of Micronesia, Marshall Islands, Palau
    # Download the file
    url = 'https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt'
    response = urllib.request.urlopen(url)
    data = response.read().decode('utf-8')

    # Create the dictionary
    county_codes = {}
    for line in data.splitlines():
        parts = line.split(',')
        code = parts[1] + parts[2]
        name = parts[3]+", "+parts[0]
        county_codes[code] = name

    return county_codes


def make_reverse_lookup(dicts):
    """
    Takes a dictionary and returns the inverse where the keys are the values
    and the values are the keys

    Parameters
    ----------
    dicts : dict
        DESCRIPTION. any dictionary

    Returns
    -------
    inv_d : dict
        DESCRIPTION. Inverse of the input dictionary

    """
    inv_d = {v: k for k, v in dicts.items()}
    return inv_d


def state_abbreviation_to_fips(state_abbr, state_names):
    """
    Takes the state names and in a dictionary looks up the FIPS code associated with that state.

    Parameters
    ----------
    state_abbr : str
        DESCRIPTION. A string representing a two-letter state abbreviation.
    state_names : dict
        DESCRIPTION.

    Returns
    -------
    fips_state : str
        DESCRIPTION. A string representing the FIPS code for the given state abbreviation,
        or an empty string if the state abbreviation is not found.

    """
    # Look up the state abbreviation in the inverted dictionary
    try:
        fips_state = state_names[state_abbr]
    except KeyError:
        return ""

    return fips_state


def get_county_name_from_fips(fips, county_codes):
    """
    Take the full fips code which is state and county and returns the county,
    removing the state and the word county

    Parameters
    ----------
    fips : str
        DESCRIPTION. a fips code (numbers that correlate to a county)
    county_codes : dict
        DESCRIPTION. Dictionary of FIPS codes with the keys being the Census countys.

    Returns
    -------
    str
        DESCRIPTION. County Name

    """
    # Look up the state abbreviation in the inverted dictionary
    try:
        county_name = county_codes[fips]
    except KeyError:
        return ""

    county_only = county_name.split(",")
    if len(county_only) > 2:
        county_str = county_only[0].replace(" County", "")
        print(county_name)
    else:
        county_str = county_only[0].replace(" County", "")
    return county_str.strip()
