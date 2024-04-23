#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 17:04:11 2023

@author: ericallen
"""
from src.check_url import check_url
import os
import sys
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


def find_h_ref_exception(api_url_text):
    """
    The function creates a list of horizontal reference frames and loops through the list
    twice to create a temporary API url with each possible combination of input and target
    reference frames. The function then checks if each temporary API url is valid using the
    check_url() function from a module called src.check_url. If a valid API url is found,
    the input and target reference frames are printed and returned. If no valid API url is
    found, None is returned.

    Parameters
    ----------
    api_url_text : str
        DESCRIPTION.

    Returns
    -------
    input_h_ref: str, None
        DESCRIPTION. horizontal reference frames for input
    target_h_ref : str, None
        DESCRIPTION. horizontal reference frames for output

    """

    horizontal_reference_frame_list = ["NAD83_2011", "NAD27", "IGS14", "NAD83_1986",
                                       "NAD83_NSRS2007", "NAD83_MARP00", "NAD83_PACP00",
                                       "WGS84_G1674", "ITRF2014",
                                       "IGS14", "ITRF2008", "IGS08", "ITRF2005", "IGS2005",
                                       "WGS84_G1150", "ITRF2000", "IGS00", "IGb00", "ITRF96",
                                       "WGS84_G873", "ITRF94", "ITRF93", "ITRF92", "SIOMIT92",
                                       "WGS84_G730", "ITRF91", "ITRF90", "ITRF89", "ITRF88",
                                       "WGS84_TRANSIT", "WGS84_G1762", "WGS84_G2139"]

    for input_h_ref in horizontal_reference_frame_list:
        for target_h_ref in horizontal_reference_frame_list:
            tmp_api = api_url_text.format(input_h_ref, target_h_ref)
            if check_url(tmp_api):
                return input_h_ref, target_h_ref

    print("ERROR: COULD NOT ACCESS API")
    return None, None
