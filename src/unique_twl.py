#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 10:21:48 2023

@author: ericallen
"""
import os
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.haversine import haversine
from src.distance_between_ground_truth import dist_btwn_gtruth

def create_unique_twl_list(unique_twl_locations, metadata_dict, ground_truth_dict, truth_list_str):
    """
    Recreate the Master TWL List that MDL developed manually.

    Parameters
    ----------
    unique_twl_locations : set
        DESCRIPTION. list(set()) for unique NWSLIs from the various lists
    metadata_dict : dict of dataframes
        DESCRIPTION. All the metadata dictionaries for the various TWL sources
    ground_truth_dict : dict of dataframes
        DESCRIPTION. dataframe with the ground truth metadata (typically NWSLI and/or AHPS)
    truth_list_str : list of strings
        DESCRIPTION. For Header Formatting, truth name: NWSLI or AHPS

    Returns
    -------
    dataframe
        DESCRIPTION. Dataframe with the unique twl list, which source is each in and
            distance between various sources.

    """
    on_value="NWSLI"
    
    dist_gtruth, gtrust_list = dist_btwn_gtruth(unique_twl_locations, ground_truth_dict)

    count = 0
    
    for key in metadata_dict.keys():
        if "nwc" in key:
            nwc_df = metadata_dict[key]
        elif "mdl" in key:
            mdl_df = metadata_dict[key]
        elif "nos" in key:
            nos_df = metadata_dict[key]
        else:
            sys.exit("ERROR... FAILED")
        
    for index, ground_truth in enumerate(ground_truth_dict):
        
        ground_truth = ground_truth_dict[ground_truth]
        truth_str = truth_list_str[index]
        
        # Initialize empty lists to store data for each dataframe
        nwc_present = []
        mdl_present = []
        nos_present = []
        truth_present = []

        nwc_mdl_dist = []
        nwc_nos_dist = []
        nwc_truth_dist = []
        nos_mdl_dist = []
        nos_truth_dist = []
        mdl_truth_dist = []
        
        # Iterate over each unique location and check if it is present in each dataframe
        for loc in unique_twl_locations:

            in_nwc = False
            in_mdl = False
            in_nos = False
            in_truth = False

            if loc in set(nwc_df[on_value]):
                in_nwc = True
                nwc_present.append(in_nwc)
                # For nwc_df
                row_nwc = nwc_df[nwc_df[on_value] == loc]
                lat_nwc = float(row_nwc.iloc[0]['LATITUDE'])
                lon_nwc = float(row_nwc.iloc[0]['LONGITUDE'])
            else:
                nwc_present.append(np.nan)
                nwc_mdl_dist.append(np.nan)
                nwc_nos_dist.append(np.nan)
                nwc_truth_dist.append(np.nan)

            if loc in set(nos_df[on_value]):
                in_nos = True
                nos_present.append(in_nos)

                # For nos_df
                row_nos = nos_df[nos_df[on_value] == loc]
                lat_nos = float(row_nos.iloc[0]['LATITUDE'])
                lon_nos = float(row_nos.iloc[0]['LONGITUDE'])

                if in_nwc:
                    distance_nwc_nos = haversine(lat_nwc, lon_nwc, lat_nos, lon_nos)
                    nwc_nos_dist.append(round(abs(distance_nwc_nos), 1))

            elif in_nwc and loc not in set(nos_df[on_value]):
                nos_present.append(np.nan)
                nwc_nos_dist.append(np.nan)
                nos_mdl_dist.append(np.nan)
                nos_truth_dist.append(np.nan)

            else:
                nos_present.append(np.nan)
                nos_mdl_dist.append(np.nan)
                nos_truth_dist.append(np.nan)

            if loc in set(mdl_df[on_value]):
                in_mdl = True
                mdl_present.append(in_mdl)

                # For mdl_df
                row_mdl = mdl_df[mdl_df[on_value] == loc]
                lat_mdl = float(row_mdl.iloc[0]['LATITUDE'])
                lon_mdl = float(row_mdl.iloc[0]['LONGITUDE'])

                if in_nwc:
                    distance_nwc_mdl = haversine(lat_nwc, lon_nwc, lat_mdl, lon_mdl)
                    nwc_mdl_dist.append(round(abs(distance_nwc_mdl), 1))

                if in_nos:
                    distance_nos_mdl = haversine(lat_nos, lon_nos, lat_mdl, lon_mdl)
                    nos_mdl_dist.append(round(abs(distance_nos_mdl), 1))

            elif in_nwc and loc not in set(mdl_df[on_value]):
                mdl_present.append(np.nan)
                nwc_mdl_dist.append(np.nan)
                mdl_truth_dist.append(np.nan)
                if in_nos:
                    nos_mdl_dist.append(np.nan)

            elif in_nos and loc not in set(mdl_df[on_value]):
                mdl_present.append(np.nan)
                nos_mdl_dist.append(np.nan)
                mdl_truth_dist.append(np.nan)
            else:
                mdl_present.append(np.nan)
                mdl_truth_dist.append(np.nan)


            if loc in set(ground_truth[on_value]):
                in_truth = True
                truth_present.append(in_truth)

                # For df_cms_copy
                row_cms = ground_truth[ground_truth[on_value] == loc]
                lat_truth = float(row_cms.iloc[0]['LATITUDE'])
                lon_truth = float(row_cms.iloc[0]['LONGITUDE'])

                if in_nwc:
                    distance_nwc_truth = haversine(lat_nwc, lon_nwc, lat_truth, lon_truth)
                    nwc_truth_dist.append(round(abs(distance_nwc_truth), 1))

                if in_mdl:
                    distance_mdl_truth = haversine(lat_mdl, lon_mdl, lat_truth, lon_truth)
                    mdl_truth_dist.append(round(abs(distance_mdl_truth), 1))

                if in_nos:
                    distance_nos_truth = haversine(lat_nos, lon_nos, lat_truth, lon_truth)
                    nos_truth_dist.append(round(abs(distance_nos_truth), 1))

            elif in_nwc and loc not in set(ground_truth[on_value]):
                truth_present.append(np.nan)
                nwc_truth_dist.append(np.nan)
                if in_mdl:
                    mdl_truth_dist.append(np.nan)
                if in_nos:
                    nos_truth_dist.append(np.nan)

            elif in_mdl and loc not in set(ground_truth[on_value]):
                truth_present.append(np.nan)
                mdl_truth_dist.append(np.nan)
                if in_nos:
                    nos_truth_dist.append(np.nan)

            elif in_nos and loc not in set(ground_truth[on_value]):
                truth_present.append(np.nan)
                nos_truth_dist.append(np.nan)
            else:
                truth_present.append(np.nan)


        #Create new df with columns for each dataframe indicating whether each location is present
        data = {on_value: list(unique_twl_locations), truth_str: truth_present, 'NWC': nwc_present,\
                'ETSS': mdl_present, 'STOFS': nos_present, '|'+truth_str+'-NWC|':nwc_truth_dist,\
                '|'+truth_str+'-NOS|':nos_truth_dist, '|'+truth_str+'-MDL|':mdl_truth_dist,\
                '|NWC-NOS|':nwc_nos_dist, '|NWC-MDL|':nwc_mdl_dist,'|NOS-MDL|':nos_mdl_dist}

        if index == 0:
            unique_df = pd.DataFrame(data)
            count = index
        else:
            unique_df = pd.merge(unique_df, pd.DataFrame(data),  on=on_value, how="outer",\
                                 suffixes=('', '_DROP'))

            # assuming merged_df is your merged dataframe
            unique_df = unique_df.filter(regex='^(?!.*_DROP)')

            # drop the columns with "_df2" suffix
            unique_df.drop(columns=[col for col in unique_df.columns if '_DROP' in col],\
                                                                               inplace=True)

            # output the resulting dataframe
            move = unique_df.pop(truth_str)
            unique_df.insert(index+1, truth_str, move)
            count = index + 1


    #Move the IN USE column to right after the NWSLI column (spot 2)
    unique_df['IN USE'] = (unique_df == True).sum(axis=1)
    in_use = unique_df.pop("IN USE")
    unique_df.insert(1, "IN USE", in_use)
    count += 1


    # remove the columns you want to move to the end
    nwc_nos_col = unique_df.pop('|NWC-NOS|')
    nwc_mdl_col = unique_df.pop('|NWC-MDL|')
    nos_mdl_col = unique_df.pop('|NOS-MDL|')

    # concat the columns at the end of the list
    unique_df = pd.concat([unique_df, nwc_nos_col, nwc_mdl_col, nos_mdl_col], axis=1)
    
    unique_df = pd.merge(unique_df, dist_gtruth,  on=on_value, how="outer")

    for colname in gtrust_list:
        count += 1
        gt_col = unique_df.pop(colname)
        unique_df.insert(count, colname, gt_col)

    # drop selected rows and drop the ZZZZZ row
    unique_df = unique_df[unique_df[on_value] != 'ZZZZZ']

    # drop the columns with "|HADS-" prefix
    unique_df = unique_df.drop(columns=unique_df.filter(like='|HADS-').columns)

    return unique_df


def unique_station_id(unique_twl_locations, metadata_dict):
    """
    Same thing as above but for Station ID where ZZZZZ (primarily is used)

    Parameters
    ----------
    unique_twl_locations : TYPE
        DESCRIPTION.
    metadata_dict : TYPE
        DESCRIPTION.

    Returns
    -------
    unique_df : TYPE
        DESCRIPTION.
    """

    
    on_value = "STATION ID" 
    
    for key in metadata_dict.keys():
        if "nwc" in key:
            nwc_df = metadata_dict[key]
        elif "mdl" in key:
            mdl_df = metadata_dict[key]
        elif "nos" in key:
            nos_df = metadata_dict[key]
        else:
            sys.exit("ERROR... FAILED")
    
    
    # Initialize empty lists to store data for each dataframe
    nwc_present = []
    mdl_present = []
    nos_present = []

    nwc_mdl_dist = []
    nwc_nos_dist = []
    nos_mdl_dist = []
    
    # Iterate over each unique location and check if it is present in each dataframe
    for loc in unique_twl_locations:

        in_nwc = False
        in_mdl = False
        in_nos = False

        if loc in set(nwc_df[on_value]):
            in_nwc = True
            nwc_present.append(in_nwc)
            # For nwc_df
            row_nwc = nwc_df[nwc_df[on_value] == loc]
            lat_nwc = float(row_nwc.iloc[0]['LATITUDE'])
            lon_nwc = float(row_nwc.iloc[0]['LONGITUDE'])
        else:
            nwc_present.append(np.nan)
            nwc_mdl_dist.append(np.nan)
            nwc_nos_dist.append(np.nan)

        if loc in set(nos_df[on_value]):
            in_nos = True
            nos_present.append(in_nos)

            # For nos_df
            row_nos = nos_df[nos_df[on_value] == loc]
            lat_nos = float(row_nos.iloc[0]['LATITUDE'])
            lon_nos = float(row_nos.iloc[0]['LONGITUDE'])

            if in_nwc:
                distance_nwc_nos = haversine(lat_nwc, lon_nwc, lat_nos, lon_nos)
                nwc_nos_dist.append(round(abs(distance_nwc_nos), 1))

        elif in_nwc and loc not in set(nos_df[on_value]):
            nos_present.append(np.nan)
            nwc_nos_dist.append(np.nan)
            nos_mdl_dist.append(np.nan)

        else:
            nos_present.append(np.nan)
            nos_mdl_dist.append(np.nan)

        if loc in set(mdl_df[on_value]):
            in_mdl = True
            mdl_present.append(in_mdl)

            # For mdl_df
            row_mdl = mdl_df[mdl_df[on_value] == loc]
            lat_mdl = float(row_mdl.iloc[0]['LATITUDE'])
            lon_mdl = float(row_mdl.iloc[0]['LONGITUDE'])

            if in_nwc:
                distance_nwc_mdl = haversine(lat_nwc, lon_nwc, lat_mdl, lon_mdl)
                nwc_mdl_dist.append(round(abs(distance_nwc_mdl), 1))

            if in_nos:
                distance_nos_mdl = haversine(lat_nos, lon_nos, lat_mdl, lon_mdl)
                nos_mdl_dist.append(round(abs(distance_nos_mdl), 1))

        elif in_nwc and loc not in set(mdl_df[on_value]):
            mdl_present.append(np.nan)
            nwc_mdl_dist.append(np.nan)
            if in_nos:
                nos_mdl_dist.append(np.nan)

        elif in_nos and loc not in set(mdl_df[on_value]):
            mdl_present.append(np.nan)
            nos_mdl_dist.append(np.nan)
        else:
            mdl_present.append(np.nan)


    #Create new df with columns for each dataframe indicating whether each location is present
    data = {on_value: list(unique_twl_locations), 'NWC': nwc_present, 'ETSS': mdl_present,\
            'STOFS': nos_present, '|NWC-NOS|':nwc_nos_dist, '|NWC-MDL|':nwc_mdl_dist,\
                '|NOS-MDL|':nos_mdl_dist}

    unique_df = pd.DataFrame(data)

    #Move the IN USE column to right after the NWSLI column (spot 2)
    unique_df['IN USE'] = (unique_df == True).sum(axis=1)
    in_use = unique_df.pop("IN USE")
    unique_df.insert(1, "IN USE", in_use)
    
    return unique_df
