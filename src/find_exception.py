#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 17:04:11 2023

@author: ericallen
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.check_url import check_url

def find_h_ref_exception(api_url_text):
    """THIS IS A REALLY BAD WAY TO DO THIS....
    Some weird things are happening with expected inputs"""

    horizontal_reference_frame_list = ["NAD83_2011", "NAD27", "IGS14", "NAD83_1986",\
                            "NAD83_NSRS2007", "NAD83_MARP00", "NAD83_PACP00",\
                            "WGS84_G1674", "ITRF2014",\
                            "IGS14", "ITRF2008", "IGS08", "ITRF2005", "IGS2005",\
                            "WGS84_G1150", "ITRF2000", "IGS00", "IGb00", "ITRF96",\
                            "WGS84_G873", "ITRF94", "ITRF93", "ITRF92", "SIOMIT92",\
                            "WGS84_G730", "ITRF91", "ITRF90", "ITRF89", "ITRF88",\
                            "WGS84_TRANSIT", "WGS84_G1762", "WGS84_G2139"]

    for input_h_ref in horizontal_reference_frame_list:
        for target_h_ref in horizontal_reference_frame_list:
            tmp_api = api_url_text.format(input_h_ref, target_h_ref)
            url_check = check_url(tmp_api)
            if url_check:
                print(input_h_ref, target_h_ref)
                return input_h_ref, target_h_ref

    print("ERROR: COULD NOT ACCESS API")
    return None, None
