#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 17:01:15 2023

@author: ericallen
"""
import json
import requests

def check_url(url):
    """Checks to make sure the URL is valid and doesn't contain an error code"""
    try:
        response = requests.get(url)
        if response.status_code == 500:
            return False
        if response.status_code == 403:
            return False
        if  "errorCode" in json.loads(response.text) and \
            json.loads(response.text)["errorCode"] == 412:
            return False
        return True
    except requests.exceptions.RequestException as err:
        return f"Request failed: {err}"
