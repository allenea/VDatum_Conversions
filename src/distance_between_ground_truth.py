#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 12:58:05 2023

@author: ericallen
"""
import numpy as np
import pandas as pd
from src.haversine import haversine


def dist_btwn_gtruth(unique_twl_locations, ground_truth_dict):
    """
    Calculate and save the distance between the coordiantes in the various datasets
    in a pandas dataframe.


    Parameters
    ----------
    unique_twl_locations : list
        DESCRIPTION. List of unique NWSLIs being used in the various models
    ground_truth_dict : dictionary of dataframes
        DESCRIPTION. dataframes with the metadata associated with the TWL points

    Returns
    -------
    dataframe
        DESCRIPTION. dataframe with the NWSLIs and distances between the coordinates in the
            various databases

    """
    datasets = list(ground_truth_dict.keys())

    column_dict = {'NWSLI': list(unique_twl_locations)}
    column_names = []

    for i, dataset1 in enumerate(datasets):
        for dataset2 in datasets[i+1:]:
            name_dataset1 = dataset1.split("_metadata")[0]
            name_dataset2 = dataset2.split("_metadata")[0]

            column_name = f"|{name_dataset1.upper()} - {name_dataset2.upper()}|"
            column_names.append(column_name)
            column_dict[column_name] = []

            for loc in unique_twl_locations:
                in_ds1 = loc in set(ground_truth_dict[dataset1]['NWSLI'])
                in_ds2 = loc in set(ground_truth_dict[dataset2]['NWSLI'])

                if in_ds1 and in_ds2:
                    row1 = ground_truth_dict[dataset1].loc[ground_truth_dict[dataset1]
                                                           ['NWSLI'] == loc]
                    lat1, lon1 = float(row1.iloc[0]['LATITUDE']), float(
                        row1.iloc[0]['LONGITUDE'])

                    row2 = ground_truth_dict[dataset2].loc[ground_truth_dict[dataset2]
                                                           ['NWSLI'] == loc]
                    lat2, lon2 = float(row2.iloc[0]['LATITUDE']), float(
                        row2.iloc[0]['LONGITUDE'])

                    distance = haversine(lat1, lon1, lat2, lon2)

                    column_dict[column_name].append(round(abs(distance), 1))

                else:
                    column_dict[column_name].append(np.nan)

    return pd.DataFrame(column_dict), column_names
