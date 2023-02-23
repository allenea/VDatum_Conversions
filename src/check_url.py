#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 17:01:15 2023

@author: ericallen
"""
import requests


def check_url(url):
    """
    Checks to make sure the URL is valid and doesn't contain an error code

    Parameters
    ----------
    url : TYPE string
        DESCRIPTION. A string that represents a URL

    Returns
    -------
    TYPE, Bool
        DESCRIPTION. True/False. Return True if no errors were found

    """
    try:
        response = requests.get(url)

        #500 Internal Server Error: This indicates that the server encountered an unexpected
        # condition that prevented it from fulfilling the request. Essentially, it means
        # that there was an error on the server side.
        if response.status_code == 500:
            return False

        #403 Forbidden: This means that the server understood the request, but is refusing
        # to fulfill it. This is usually because the user does not have sufficient
        # permissions to access the requested resource.
        if response.status_code == 403:
            return False

        #200 is a standard response code used by HTTP servers to indicate that everything
        # is working as expected. If not 200, then URL is not okay.
        if response.status_code != 200:
            return False

        content_type = response.headers.get("content-type")
        #If the application isn't a json then this conditional block won't work, so let it through
        if "application/json" in content_type:

            response_data = response.json()

            #412 Precondition Failed: This error occurs when a condition specified in the
            # request headers is not met. For example, if the request includes an "If-Match"
            # header and the specified entity tag does not match the current entity tag for
            # the requested resource, the server will return a 412 error.
            if "errorCode" in response_data and response_data["errorCode"] == 412:
                return False
            #Else -- True... leave loop and take the catch all for if it isn't a JSON

        #This includes other content-types other than jsons
        return True

    except requests.exceptions.RequestException as err:
        return f"Request failed: {err}"
