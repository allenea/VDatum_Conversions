#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 16:23:05 2023

@author: ericallen
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.read_kml import read_kml_file

def read_vdatum_regions():
    """read in kml files that were downloaded from
    https://vdatum.noaa.gov/download/data/vdatum_regional_20221116.zip and unzipped
    """
    path = os.getcwd()

    # =============================================================================
    # READ IN VDATUM REGIONS AND ASSIGN REGIONS TO EACH STATION
    # =============================================================================
    if os.path.exists(os.path.join(path, "vdatum")):
        #chesapeak_delaware
        DEdelbay33_file = os.path.join(path,"vdatum", "DEdelbay33_8301", "DEdelbay33_8301.kml")
        MDnwchb11_8301_file = os.path.join(path,"vdatum", "MDnwchb11_8301", "MDnwchb11_8301.kml")
        MDVAechb1_file = os.path.join(path,"vdatum", "MDVAechb11_8301", "MDVAechb11_8301.kml")
        VAswchb11_8301_file = os.path.join(path,"vdatum", "VAswchb11_8301", "VAswchb11_8301.kml")
        NJVAmab33_file = os.path.join(path,"vdatum", "NJVAmab33_8301", "NJVAmab33_8301.kml")
        NJscstemb32_file = os.path.join(path,"vdatum", "NJscstemb32_8301", "NJscstemb32_8301.kml")

        #prvi
        PRVI_file = os.path.join(path,"vdatum", "PRVI01_8301", "PRVI01_8301.kml")

        #seak
        AKyakutat00_file = os.path.join(path,"vdatum","AKyakutat00_8301", "AKyakutat00_8301.kml")
        AKglacier00_file = os.path.join(path,"vdatum","AKglacier00_8301", "AKglacier00_8301.kml")
        AKwhale00_file = os.path.join(path,"vdatum", "AKwhale00_8301", "AKwhale00_8301.kml")

        #westcoast
        CAsouthn00_file = os.path.join(path,"vdatum", "CAsouthn00_8301", "CAsouthn00_8301.kml")
        CAsouin00_file = os.path.join(path,"vdatum", "CAsouin00_8301", "CAsouin00_8301.kml")
        CAsfdel00_file = os.path.join(path,"vdatum", "CAsfdel00_8301", "CAsfdel00_8301.kml")
        CAsfbay13_file = os.path.join(path,"vdatum", "CAsfbay13_8301", "CAsfbay13_8301.kml")
        CAoregon00_file = os.path.join(path,"vdatum", "CAoregon00_8301", "CAoregon00_8301.kml")
        CAmontby13_file = os.path.join(path,"vdatum", "CAmontby13_8301", "CAmontby13_8301.kml")
        ORcoast00_file = os.path.join(path,"vdatum", "ORcoast00_8301", "ORcoast00_8301.kml")
        ORcoain00_file = os.path.join(path,"vdatum", "ORcoain00_8301", "ORcoain00_8301.kml")
        WCoffsh00_file = os.path.join(path,"vdatum", "WCoffsh00_8301", "WCoffsh00_8301.kml")
        WApuget13_file = os.path.join(path,"vdatum", "WApugets13_8301", "WApugets13_8301.kml")
        WAjdfuca14_file = os.path.join(path,"vdatum", "WAjdfuca14_8301", "WAjdfuca14_8301.kml")
        WAjdfin00_file = os.path.join(path,"vdatum", "WAjdfin00_8301", "WAjdfin00_8301.kml")
        WAcoast00_file = os.path.join(path,"vdatum","WAcoast00_8301" , "WAcoast00_8301.kml")
        CRD_file = os.path.join(path,"vdatum","CRD" , "CRD.kml")
    else:
        err_str = "The directory containing the vdatum regions and kml files could not be found"
        raise FileNotFoundError(err_str)

    ############################
    #chesapeak_delaware
    DEdelbay33 = read_kml_file(DEdelbay33_file)
    MDnwchb11_8301 = read_kml_file(MDnwchb11_8301_file)
    MDVAechb1 = read_kml_file(MDVAechb1_file)
    VAswchb11_8301 = read_kml_file(VAswchb11_8301_file)
    NJVAmab33 = read_kml_file(NJVAmab33_file)
    NJscstemb32 = read_kml_file(NJscstemb32_file)

    #prvi
    PRVI = read_kml_file(PRVI_file)

    #seak
    AKyakutat00 = read_kml_file(AKyakutat00_file)
    AKglacier00 = read_kml_file(AKglacier00_file)
    AKwhale00 = read_kml_file(AKwhale00_file)

    #westcoast
    CAsouthn00 = read_kml_file(CAsouthn00_file)
    CAsouin00 = read_kml_file(CAsouin00_file)
    CAsfdel00 = read_kml_file(CAsfdel00_file)
    CAsfbay13 = read_kml_file(CAsfbay13_file)
    CAoregon00 = read_kml_file(CAoregon00_file)
    CAmontby13 = read_kml_file(CAmontby13_file)
    ORcoast00 = read_kml_file(ORcoast00_file)
    ORcoain00 = read_kml_file(ORcoain00_file)
    WCoffsh00 = read_kml_file(WCoffsh00_file)
    WApuget13 = read_kml_file(WApuget13_file)
    WAjdfuca14 = read_kml_file(WAjdfuca14_file)
    WAjdfin00 = read_kml_file(WAjdfin00_file)
    WAcoast00 = read_kml_file(WAcoast00_file)
    CRD = read_kml_file(CRD_file)
    ############################

    #return all_kmls
    return {"New Jersey - coastal embayment - South":NJscstemb32,\
            "Virginia/Maryland/Delaware/New Jersey - Mid-Atlantic Bight shelf":NJVAmab33,\
            "Delaware - Delaware Bay":DEdelbay33,\
            "Virginia/Maryland - East Chesapeake Bay":MDVAechb1,\
            "Maryland - Northwest Chesapeake Bay":MDnwchb11_8301,\
            "Virginia - Southwest Chesapeake Bay":VAswchb11_8301,\
            "Puerto Rico and U.S. Virgin Islands":PRVI,\
            "Alaska - Southeast, Yakutat to Glacier Bay":AKyakutat00,\
              "Alaska - Southeast, Glacier Bay to Whale Bay":AKglacier00,\
              "Alaska - Southeast, Whale Bay to US/Canada Border":AKwhale00,\
            "Washington - Coastal":WAcoast00,\
            "Washington - Strait of Juan de Fuca Inland":WAjdfin00,\
            "Washington - Strait of Juan de Fuca":WAjdfuca14,\
            "Washington - Puget Sound":WApuget13,\
            "Washington/Oregon/California - Offshore":WCoffsh00,\
            "Oregon - Coastal Inland":ORcoain00,\
            "Oregon - Coastal":ORcoast00,\
            "California -Monterey Bay to Morro Bay":CAmontby13,\
            "California/Oregon - Coastal":CAoregon00,\
            "California - San Francisco Bay Vicinity":CAsfbay13,\
            "California - San Francisco Bay Inland":CAsfdel00,\
            "California - Southern California Inland":CAsouin00,\
            "California - Southern California":CAsouthn00,\
            "Columbia River":CRD}
