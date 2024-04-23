#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 11:34:08 2023

@author: ericallen
"""
import math

def haversine(lat1, lon1, lat2, lon2):
    """


    Parameters
    ----------
    lat1 : float
        DESCRIPTION. Latitude for point 1
    lon1 : float
        DESCRIPTION. Longitude for point 1
    lat2 : float
        DESCRIPTION. Latitude for point 2
    lon2 : float
        DESCRIPTION. Longitude for point 2

    Returns
    -------
    distance : float
        DESCRIPTION. Distance between the two points

    """

    radius = 6371.0  # radius of the Earth in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    arc = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    acos = 2 * math.atan2(math.sqrt(arc), math.sqrt(1-arc))
    distance = radius * acos * 1000  # distance in meters

    return distance
