#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 14:40:08 2023

@author: ericallen

Downside... only picks the first program if multiple are associated
"""
import pandas as pd


def read_in_nwsli(file):
    """
    READ IN NWSLI Spreadsheet provided by Tom Raffa, reformat to a readable format

    Parameters
    ----------
    file : string
        DESCRIPTION. path to NWSLI Metadata file, must download from CBITS or get from Tom Raffa

    Returns
    -------
    nwsli_metadata : dataframe
        DESCRIPTION. dataframe of NWSLI metadata

    """

    print("LAST UPDATED MARCH 15th, 2024")

    nwsli_data = pd.ExcelFile(file)

    # Read in the two dataframes
    all_sites = pd.read_excel(nwsli_data, "All Sites", header=0)
    all_sites_programs = pd.read_excel(nwsli_data, "All Sites With Programs", header=0)

    # Convert column names to title case
    all_sites.columns = map(str.upper, all_sites.columns)
    all_sites_programs.columns = map(str.upper, all_sites_programs.columns)

    #rename 2 column headers so there is consistency to the other sheet
    all_sites_programs = all_sites_programs.rename(columns={'DECLON': "DECIMAL LON",
                                                            "DECLAT": "DECIMAL LAT"})

    # Find columns that are only in all_sites_programs (excluding the Sid column)
    additional_cols = set(all_sites_programs.columns) - set(all_sites.columns)

    # create a list of columns to drop from all_sites_programs
    cols_to_drop = set(all_sites_programs.columns) - {'SID'} - additional_cols

    # drop the unwanted columns from all_sites_programs
    all_sites_programs.drop(cols_to_drop, axis=1, inplace=True)

    # Merge the two dataframes on the Sid column, keeping only the necessary columns
    nwsli_metadata = pd.merge(all_sites, all_sites_programs, on='SID')
    nwsli_metadata = nwsli_metadata.drop_duplicates(subset=['SID'], keep='first')

    #NWSLI is used throughout this program
    nwsli_metadata = nwsli_metadata.rename(columns={'SID': "NWSLI"})

    reorder = ['STNSEQNO', 'NWSLI', 'REGION', 'WFO', 'RFC', 'CITY', 'COUNTY', 'STATE',
               'LATITUDE', 'LONGITUDE', 'DECIMAL LAT', 'DECIMAL LON', 'STATION NAME',
               'TYPE', 'PGMA', 'PID', 'ADM']

    nwsli_metadata = nwsli_metadata.reindex(columns=reorder)

    nwsli_metadata = nwsli_metadata.drop(['STNSEQNO', 'TYPE', 'LATITUDE',
                                          'LONGITUDE', "CITY"], axis=1)

    rfc_dict_nwsli = {"ACR": "APRFC", "ALR": "SERFC", "FWR": "WGRFC", "KRF": "MBRFC",
                      "MSR": "NCRFC", "ORN": "LMRFC", "PTR": "NWRFC", "RHA": "MARFC",
                      "RSA": "CNRFC", "STR": "CBRFC", "TAR": "NERFC", "TIR": "OHRFC",
                      "TUA": "ARRFC"}

    region_dict_nwsli = {"1": "ER", "2": "SR", "3": "CR", "4": "WR", "5": "AR", "6": "PR",
                         "7": "INTL", "8": "Other"}

    for index, row in nwsli_metadata.iterrows():
        #Creating consistency for RFC String/Name for spreadsheet/comparison
        if not pd.isna(row["RFC"]) and row["RFC"] in rfc_dict_nwsli:
            nwsli_metadata.loc[index, "RFC"] = rfc_dict_nwsli[row["RFC"].upper()]
        elif not pd.isna(row["RFC"]) and row["RFC"] in rfc_dict_nwsli.values():
            nwsli_metadata.loc[index, "RFC"] = row["RFC"]
            print("Invalid RFC SID: ", row["RFC"])
        elif pd.isna(row["RFC"]):
            pass
        else:
            print("Invalid Entry - RFC: ", row["RFC"])

        #Creating consistency for Region String/Name for spreadsheet/comparison
        if not pd.isna(row["REGION"]) and str(row["REGION"]) in region_dict_nwsli:
            nwsli_metadata.loc[index, "REGION"] = region_dict_nwsli[str(int(row["REGION"]))]
        elif pd.isna(row["REGION"]) or str(row["REGION"]) == "9":
            pass
        else:
            print("Invalid Entry - Region: ", row["REGION"])

    nwsli_metadata = nwsli_metadata.rename(columns={'DECIMAL LAT': "LATITUDE",
                                                    'DECIMAL LON': "LONGITUDE", 'REGION': "REGION",
                                                    'WFO': "WFO", 'RFC': "RFC", 'COUNTY': "COUNTY",
                                                    'STATE': "STATE"})

    return nwsli_metadata
