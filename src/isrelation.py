#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 16:24:19 2023

@author: ericallen
"""

def is_west_of(point, longitude):
    """
    Check if the Point is to the west of the specified longitude.
    :param point: A Shapely Point object.
    :param longitude: The longitude to compare against.
    :return: True if the Point is to the west of the longitude, False otherwise.
    """
    return point.x < longitude

def is_north_of(point, latitude):
    """
    Check if the Point is to the north of the specified latitude.
    :param point: A Shapely Point object.
    :param latitude: The latitude to compare against.
    :return: True if the Point is to the north of the latitude, False otherwise.
    """
    return point.y > latitude
