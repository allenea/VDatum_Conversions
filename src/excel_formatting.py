#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 16:57:12 2023

@author: ericallen
"""
import pandas as pd

COLS_TO_FORMAT = ['Ref_Datum', 'MHHW', 'MHW', 'MTL', 'MSL', 'DTL', 'MLW', 'MLLW',\
                       'NAVD88', 'STND', 'NGVD29',"LMSL"]

COLS_TO_FORMAT2 = ['NAVD88 to MLLW', 'NAVD88 to MHHW']

# =============================================================================
# SETUP Excel Spreadsheet
# =============================================================================
def init_styles(workbook):
    """
    Initialize styles used in this program

    Parameters
    ----------
    workbook : pandas.xlsxwriter.workbook
        DESCRIPTION.

    Returns
    -------
    workbook : pandas.xlsxwriter.workbook
        DESCRIPTION.
    styles : dict
        DESCRIPTION.

    """
    # Define the blue hyperlink format
    blue_hyperlink_format = workbook.add_format({'color':'blue', 'underline':1,\
                                    'text_wrap':False, 'align':'left', 'valign':'vcenter'})

    # Set the format for other columns
    default_col_format = workbook.add_format({'text_wrap':False, 'align':'left',\
                                              'valign':'vcenter'})

    header_format = workbook.add_format({'text_wrap': True, 'bold': True})


    # Define the red fill format
    red_fill_format = workbook.add_format({'bg_color': '#FFC7CE'})
    light_yellow_fill_format = workbook.add_format({'bg_color': '#FDF2D0'})
    cyan_fill_format = workbook.add_format({'bg_color': '#00FFFF'})


    styles = {"hyperlink":blue_hyperlink_format,\
              "default_col_format":default_col_format,\
                "header_format":header_format,\
                "red_fill_format":red_fill_format,\
                "light_yellow_fill_format":light_yellow_fill_format,\
                "cyan_fill_format":cyan_fill_format}


    return workbook, styles



def format_excel(dataframe, worksheet, style, hyper_id=True):
    """


    Parameters
    ----------
    dataframe : pandas.dataframe
        DESCRIPTION. some set of data that needs to be formatted

    Returns
    -------
    None.

    """
    # Define the conditional formatting rule
    blank_cell_rule = {'type': 'blanks', 'format':style['light_yellow_fill_format']}
    missing_rule = {'type':'cell', 'criteria':'==', 'value':-999999,\
                        'format':style['red_fill_format']}
    check_error_rule = {'type': 'no_errors', 'format': style['cyan_fill_format']}
    hyperlink_rule = {'type': 'no_errors', 'format': style['hyperlink']}

    #hyperlink_rule = {'type':'text', 'criteria':'not containing', 'value':'None',\
    #                    'format':style['hyperlink']}


    dataframe = dataframe.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Set the column formats
    for col_num, col_name in enumerate(dataframe.columns):

        max_len = dataframe.iloc[1:,:][col_name].astype(str).str.len().max() * 1.25

        if max_len > 18:
            max_len = 18
        elif 6 < max_len < 10:
            max_len = 10
        elif max_len < 6:
            max_len = 7.5


        if col_name in ['Station Info', 'Datum Info', 'Extra Metadata', 'Hydrograph',\
                            'VDatum - MLLW', 'VDatum - MHHW']:
            #if col_name == 'Station ID':
            #    # Check if the value is not None and the cell contains a hyperlink function
            #    #cond = dataframe[col_name].notna() & (dataframe[col_name].str.startswith(\
            #       '=HYPERLINK('))
            #    #hyperlink_rule = {'type': 'formula', 'criteria': f'=AND({cond.to_list()})',\
            #    #                    'format':style['hyperlink']}
            #    # Apply the blue hyperlink formatting to the selected cells
            #    #worksheet.conditional_format(1, dataframe.columns.get_loc(col_name),
            #                                 len(dataframe.index),
            #                                 dataframe.columns.get_loc(col_name),
            #                                 hyperlink_rule)
            #else:
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['hyperlink'])

        elif col_name in ["Comments"]:
            max_len = 20
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format'])
        elif col_name in ["VDATUM Latitude", "VDATUM Longitude", "VDATUM Height", "VDATUM to MLLW",\
                              "VDATUM to MHHW", "New Latitude","New Longitude", "New Height"]:
            max_len = 18
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format'])
        elif col_name not in ['River Waterbody Name', 'HUC2', 'Location Name', 'AHPS Name']:
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format'])
        else:
            max_len = 15
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format'])


    # Wrap the headers
    for col_num, value in enumerate(dataframe.columns.values):
        worksheet.write(0, col_num, value, style['header_format'])

    #Hyperlink on valid Hyperlink cells in Station ID. This is the best way...
    if hyper_id and "Station ID" in dataframe.columns:
        col_idx = dataframe.columns.get_loc("Station ID")
        for idx, row in dataframe.iterrows():
            if row["Data Source"] not in ["HCFCD", "None"]:
                worksheet.conditional_format(idx+1, col_idx, idx+1, col_idx, hyperlink_rule)


    if all(col in dataframe.columns for col in COLS_TO_FORMAT):
        for col in COLS_TO_FORMAT:
            if col == "Ref Datum":
                pass
            else:
                dataframe[col] = pd.to_numeric(dataframe[col], errors='coerce')

            #Apply the conditional formatting rule to the cell if blank for these columns
            worksheet.conditional_format(1, dataframe.columns.get_loc(col),
                                         len(dataframe.index),
                                         dataframe.columns.get_loc(col),
                                         blank_cell_rule)

    # Check for columns "NAVD88 to MLLW" and "NAVD88 to MHHW"
    if 'NAVD88 to MLLW' in dataframe.columns and 'NAVD88 to MHHW' in dataframe.columns:
        # Apply conditional formatting to selected columns
        for col in COLS_TO_FORMAT2:
            dataframe[col] = pd.to_numeric(dataframe[col], errors='coerce')
            # Apply the conditional formatting rule to the column
            worksheet.conditional_format(1, dataframe.columns.get_loc(col),
                                         len(dataframe.index),
                                         dataframe.columns.get_loc(col),
                                         missing_rule)

    # Check for columns "NAVD88 to MLLW" and "NAVD88 to MHHW"
    if 'NAVD88 to MLLW' in dataframe.columns and 'NAVD88 to MHHW' in dataframe.columns:
        # Check if both columns contain -999999 in the same row
        for idx, row in dataframe.iterrows():
            if row['NAVD88 to MLLW'] == -999999 and row['NAVD88 to MHHW'] == -999999:
                for col_name in ['VDATUM Latitude', 'VDATUM Longitude', 'VDATUM Height',\
                                     'VDATUM to MLLW', 'VDATUM to MHHW']:
                    col_idx = dataframe.columns.get_loc(col_name)
                    worksheet.conditional_format(idx+1, col_idx, idx+1, col_idx, check_error_rule)

    return worksheet
