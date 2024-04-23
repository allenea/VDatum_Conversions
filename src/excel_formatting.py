#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 16:57:12 2023

@author: ericallen
"""
import pandas as pd
import numpy as np

# =============================================================================

#FOR MASTER METADATA
COLS_TO_FORMAT = ['REF_DATUM', 'MHHW', 'MHW', 'MTL', 'MSL', 'DTL', 'MLW', 'MLLW',\
                       'NAVD88', 'STND', 'NGVD29',"LMSL"]

COLS_TO_FORMAT2 = ['NAVD88 to MLLW', 'NAVD88 to MHHW', 'LMSL to MLLW', 'LMSL to MHHW']

# =============================================================================

## FOR STOPLIGHT
COLS_TO_FORMAT3 = ['|CBITS - AHPS|', '|CBITS - HADS|', '|AHPS - HADS|', '|CBITS-NWC|',\
                   '|CBITS-NOS|', '|CBITS-MDL|', '|AHPS-NWC|', '|AHPS-NOS|', '|AHPS-MDL|',\
                   '|NWC-NOS|', '|NWC-MDL|', '|NOS-MDL|', 'Greatest ∆X Value']

COLS_TO_FORMAT4 = ['NWSLI', 'IN USE', 'TIDE', 'CBITS', 'AHPS', 'HADS', 'NWC', 'ETSS', 'STOFS',\
                  "STATION ID", "LATITUDE CBITS", "LONGITUDE CBITS", "LATITUDE AHPS",\
                  "LONGITUDE AHPS", "LATITUDE HADS", "LONGITUDE HADS", "LATITUDE NWC",\
                  "LONGITUDE NWC", "LATITUDE NOS", "LONGITUDE NOS", "LATITUDE MDL",\
                  "LONGITUDE MDL", "COUNTY CBITS", "COUNTY AHPS", 'DATA SOURCE',\
                  'STATION ID', 'USGS ID AHPS', 'USGS ID NRLDB', 'OWNER']

# =============================================================================
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
                                              'valign':'vcenter', 'border': 1})

    default_col_format2 = workbook.add_format({'text_wrap':False, 'align':'center',\
                                                  'valign':'vcenter', 'border': 1})

    regular_format = workbook.add_format({'text_wrap': True, 'align':'center',\
                                                      'valign':'vcenter', 'border': 1})

    header_format = workbook.add_format({'text_wrap': True, 'bold': True, 'border': 1})

    header_format2 = workbook.add_format({'text_wrap': True, 'bold': True, 'align':'center',\
                                                  'valign':'vcenter', 'border': 1})

    header_format3 = workbook.add_format({'text_wrap': True, 'bold': True, 'align':'center',\
                                                  'valign':'vcenter', 'font_color': 'red', 'border': 1})


    # Define the red fill format

    bright_red_fill_format = workbook.add_format({'bg_color': '#FF0000', 'align':'center',\
                                                  'valign':'vcenter', 'border': 1})
    red_fill_format = workbook.add_format({'bg_color': '#FFC7CE','align':'center',\
                                           'valign':'vcenter', 'border': 1})
    light_yellow_fill_format = workbook.add_format({'bg_color': '#FDF2D0','align':'center',\
                                                    'valign':'vcenter','border': 1})
    cyan_fill_format = workbook.add_format({'bg_color': '#00FFFF','align':'center',\
                                            'valign':'vcenter','border': 1})
    bright_green_fill_format = workbook.add_format({'bg_color': "#02f502",'align':'center',\
                                                    'valign':'vcenter','border': 1})
    light_green_fill_format = workbook.add_format({'bg_color': "C6EFCE", 'align':'center',\
                                                   'valign':'vcenter','border': 1})
    blank_white_fill_format = workbook.add_format({'bg_color': "#FFFFFF",'align':'center',\
                                                   'valign':'vcenter','border': 1})



    styles = {"hyperlink":blue_hyperlink_format,\
              "default_col_format":default_col_format,\
              "default_col_format2":default_col_format2,\
              'regular_format':regular_format,\
                "header_format":header_format,\
                "header_format2": header_format2,\
                "header_format3": header_format3,\
                "red_fill_format":red_fill_format,\
                "light_yellow_fill_format":light_yellow_fill_format,\
                "cyan_fill_format":cyan_fill_format,\
                "bright_red_fill_format": bright_red_fill_format,\
                "bright_green_fill_format": bright_green_fill_format,\
                "light_green_fill_format":light_green_fill_format,\
                "blank_white_fill_format":blank_white_fill_format}

    return workbook, styles



def format_excel(dataframe, worksheet, style, hyper_id=True):
    """
    format master metadata list for stations associated with TWL NWSLIs

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

        if col_name.upper() in ['STATION INFO', 'DATUM INFO', 'EXTRA METADATA', 'HYDROGRAPH',\
                            'VD NAVD88 - MLLW', 'VD NAVD88 - MHHW', 'VD LMSL - MLLW',\
                            'VD LMSL - MHHW', 'WATER LEVELS', 'DATUMS',\
                            'HARMONIC', 'BENCHMARKS', 'REPORTS', "TIDE PREDICTIONS",
                            'EXTREME WATER LEVELS', 'METEOROLOGICAL', 'CONDUCTIVITY',
                            'SEA LEVEL TRENDS', 'OFS', 'PORTS']:
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

        elif col_name.upper() in ["COMMENTS"]:
            max_len = 20
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format'])
        elif col_name.upper() in ["VDATUM LATITUDE", "VDATUM LONGITUDE", "VDATUM HEIGHT",\
                                "VDATUM TO MLLW", "VDATUM TO MHHW", "NEW LATITUDE","NEW LONGITUDE",\
                                "NEW HEIGHT"]:
            max_len = 18
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format'])
        elif col_name.upper() not in ['RIVER WATERBODY NAME', 'HUC2', 'LOCATION NAME', 'AHPS NAME']:
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format'])
        else:
            max_len = 15
            worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format'])


    # Wrap the headers
    for col_num, value in enumerate(dataframe.columns.values):
        worksheet.write(0, col_num, value, style['header_format'])

    #Hyperlink on valid Hyperlink cells in Station ID. This is the best way...
    if hyper_id and "STATION ID" in dataframe.columns:
        col_idx = dataframe.columns.get_loc("STATION ID")
        for idx, row in dataframe.iterrows():
            if row["DATA SOURCE"] not in ["HCFCD", "None", "USACE", "NCDPS", "NERRS"]:
                worksheet.conditional_format(idx+1, col_idx, idx+1, col_idx, hyperlink_rule)


    if all(col in dataframe.columns for col in COLS_TO_FORMAT):
        for col in COLS_TO_FORMAT:
            if col == "REF DATUM":
                pass
            else:
                dataframe[col] = pd.to_numeric(dataframe[col], errors='coerce')

            #Apply the conditional formatting rule to the cell if blank for these columns
            worksheet.conditional_format(1, dataframe.columns.get_loc(col),
                                         len(dataframe.index),
                                         dataframe.columns.get_loc(col),
                                         blank_cell_rule)

    # Check for columns "NAVD88 to MLLW" and "NAVD88 to MHHW"
    if ('NAVD88 TO MLLW' in dataframe.columns and 'NAVD88 TO MHHW' in dataframe.columns) or\
        ('LMSL TO MLLW' in dataframe.columns and 'LMSL TO MHHW' in dataframe.columns):
        # Apply conditional formatting to selected columns
        for col in COLS_TO_FORMAT2:
            if col in dataframe.columns:
                dataframe[col] = pd.to_numeric(dataframe[col], errors='coerce')
                # Apply the conditional formatting rule to the column
                worksheet.conditional_format(1, dataframe.columns.get_loc(col),
                                             len(dataframe.index),
                                             dataframe.columns.get_loc(col),
                                             missing_rule)

    # Check for columns "NAVD88 to MLLW" and "NAVD88 to MHHW"
    if 'NAVD88 TO MLLW' in dataframe.columns and 'NAVD88 TO MHHW' in dataframe.columns:
        # Check if both columns contain -999999 in the same row
        for idx, row in dataframe.iterrows():
            if (row['NAVD88 TO MLLW'] == -999999 and row['NAVD88 TO MHHW'] == -999999) and\
                (row['LMSL TO MLLW'] == -999999 and row['LMSL TO MHHW'] == -999999):
                for col_name in ['VDATUM LATITUDE', 'VDATUM LONGITUDE', 'VDATUM HEIGHT',\
                                     'VDATUM TO MLLW', 'VDATUM TO MHHW']:
                    col_idx = dataframe.columns.get_loc(col_name)
                    worksheet.conditional_format(idx+1, col_idx, idx+1, col_idx, check_error_rule)

    return worksheet


def format_excel_stoplight_meta(dataframe, worksheet, style, headerbuffer=False):
    """
    Create the excel file with the specified formatting and conditional formatting
    for all TWL forecast points in the TWL models. This is to be used for text comparisons.


    Parameters
    ----------
    dataframe : dataframe
        DESCRIPTION. dataframe with the data
    worksheet : excel object
        DESCRIPTION. Spreadshet, pre-format
    style : dictionary
        DESCRIPTION. dictionary with style information
    headerbuffer : bool, optional
        DESCRIPTION. The default is False. If True there is an extra header row

    Returns
    -------
    worksheet : excel object
        DESCRIPTION. formattted spreadsheet

    """

    #dataframe = dataframe.replace(np.nan, "")

    dataframe = dataframe.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Set the column formats
    for col_num, col_name in enumerate(dataframe.columns):

        max_len = dataframe.iloc[1:,:][col_name].astype(str).str.len().max()

        if max_len > 6:
            max_len = 12
        elif max_len <= 6:
            max_len = 8.5

        worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format2'])


    if headerbuffer:

        first_row = 2
        last_row = 1

        worksheet.merge_range('A1:B1', 'Units: Meters', style['header_format3'])
        worksheet.merge_range('D1:F1', 'Observation Info', style['header_format2'])
        worksheet.merge_range('G1:I1', 'Available in Model', style['header_format2'])
        worksheet.merge_range('K1:V1', 'Lat/Lon Pairs', style['header_format2'])
        worksheet.merge_range('W1:Y1', 'Region', style['header_format2'])
        worksheet.merge_range('Z1:AD1', 'WFO', style['header_format2'])
        worksheet.merge_range('AE1:AH1', 'RFC', style['header_format2'])
        worksheet.merge_range('AI1:AL1', 'STATE', style['header_format2'])
        worksheet.merge_range('AM1:AN1', 'COUNTY', style['header_format2'])
        worksheet.merge_range('AO1:AS1', 'DATA PROVIDER INFO', style['header_format2'])

        #Region (columns U:V), WFO (columns: W:Y), RFC (columns: Z:AB),
        #STATE (columns AC:AF), COUNTY (columns: AG:AH)

        for col_num, value in enumerate(dataframe.columns.values):
            worksheet.write(1, col_num, value, style['header_format2'])
    else:
        first_row = 1
        last_row = 0
        # Wrap the headers
        for col_num, value in enumerate(dataframe.columns.values):
            worksheet.write(0, col_num, value, style['header_format2'])

    #Hyperlink on valid Hyperlink cells in Station ID. This is the best way...
    if "NWSLI" in dataframe.columns and headerbuffer:
        col_idx = dataframe.columns.get_loc("NWSLI")
        for idx, row in dataframe.iterrows():
            #print(row["CBITS"], type(row["CBITS"]), np.isnan(row["CBITS"]))
            if np.isnan(row["CBITS"]):
                worksheet.conditional_format(idx+2, col_idx, idx+2, col_idx,\
                                             {'type': 'no_errors',\
                                              'format':style['bright_red_fill_format']})
    if "Greatest ∆X Value" in dataframe.columns:
        col_name = "Greatest ∆X Value"
        dataframe[col_name] = pd.to_numeric(dataframe[col_name], errors='coerce')


        worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                     last_row+len(dataframe.index),
                                     dataframe.columns.get_loc(col_name),
                                     {'type': 'blanks',
                               'format': style["blank_white_fill_format"]})

        worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                     last_row+len(dataframe.index),
                                     dataframe.columns.get_loc(col_name),
                                     {'type': 'cell',
                                        'criteria': '>',
                                        'value': 10000,
                                        'format': style['bright_red_fill_format']})


        worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                     last_row+len(dataframe.index),
                                     dataframe.columns.get_loc(col_name),
                                     {'type': 'cell',
                                        'criteria': '>',
                                        'value': 1000,
                                        'format': style['red_fill_format']})


        worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                     last_row+len(dataframe.index),
                                     dataframe.columns.get_loc(col_name),
                                     {'type': 'cell',
                                        'criteria': '>',
                                        'value': 555,
                                        'format': style['light_yellow_fill_format']})


        worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                     last_row+len(dataframe.index),
                                     dataframe.columns.get_loc(col_name),
                                     {'type': 'cell',
                                        'criteria': '==',
                                        'value': 0,
                                        'format': style["bright_green_fill_format"]})


        worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                     last_row+len(dataframe.index),
                                     dataframe.columns.get_loc(col_name),
                                     {'type': 'cell',
                                        'criteria': '>',
                                        'value': 0,
                                        'format': style['light_green_fill_format']})


    header_row_offset = 2 if headerbuffer else 1


    # Define the groupings with column indices
    groupings_indices = {
        'REGION': [dataframe.columns.get_loc(c) for c in ['REGION CBITS', 'REGION AWIPS',\
                                                          'REGION NWC']],
        'WFO': [dataframe.columns.get_loc(c) for c in ['WFO CBITS', 'WFO AWIPS',\
                                                       'WFO AHPS', 'WFO NRLDB', 'WFO HADS']],
        'RFC': [dataframe.columns.get_loc(c) for c in ['RFC CBITS', 'RFC AWIPS',\
                                                       'RFC AHPS', 'RFC NWC']],
        'STATE': [dataframe.columns.get_loc(c) for c in ['STATE CBITS', 'STATE AHPS',\
                                                         'STATE HADS', 'STATE NOS']],
        'STATION ID': [dataframe.columns.get_loc(c) for c in ['STATION ID', 'USGS ID AHPS', 'USGS ID NRLDB']]}

    # Get the index of 'REGION CBITS' to apply the specific '9' rule
    region_cbits_idx = dataframe.columns.get_loc('REGION CBITS')

    # Write DataFrame to Excel with conditional formatting
    for row_idx, row in dataframe.iterrows():
        # Adjust row index to account for the header rows when writing to the worksheet
        adjusted_row_idx = row_idx + header_row_offset  # Shift down by 2 for the headers
        for group, indices in groupings_indices.items():
            group_values = row.iloc[indices].replace('', pd.NA).dropna().unique()  # Unique non-NaN values in the group
            #group_values = row.iloc[indices].dropna().unique()  # Unique non-NaN values in the group
            group_format = None

            # Determine the format for the group
            if len(group_values) == 1:
                group_format = style['light_green_fill_format']
            elif len(group_values) > 1:
                group_format = style['red_fill_format']

            # Write the group's cells with the determined format
            for col_idx in indices:
                value = row.iloc[col_idx]
                # Check for '9' in 'REGION CBITS' and apply nine_red_format
                if col_idx == region_cbits_idx and '9' in str(value):
                    cell_format = style['bright_red_fill_format']
                else:
                    cell_format = style['light_yellow_fill_format'] if pd.isna(value) or value == '' else group_format
                    #cell_format = style['light_yellow_fill_format'] if pd.isna(value) else group_format

                #worksheet.write(adjusted_row_idx, col_idx, '' if pd.isna(value) else value, cell_format)
                worksheet.write(adjusted_row_idx, col_idx, '' if pd.isna(value) or value == '' else value, cell_format)

    if any(col in dataframe.columns for col in COLS_TO_FORMAT4):
        for col_name in COLS_TO_FORMAT4:
            if col_name in dataframe.columns:
                col_idx = dataframe.columns.get_loc(col_name)
                # Apply the format to the entire column using numerical indices
                worksheet.set_column(col_idx, col_idx, None, style['regular_format'])

    return worksheet


def format_excel_stoplight(dataframe, worksheet, style, headerbuffer=False):
    """
    Create the excel file with the specified formatting and conditional formatting
    for all TWL forecast points in the TWL models.


    Parameters
    ----------
    dataframe : dataframe
        DESCRIPTION. dataframe with the data
    worksheet : excel object
        DESCRIPTION. Spreadshet, pre-format
    style : dictionary
        DESCRIPTION. dictionary with style information
    headerbuffer : bool, optional
        DESCRIPTION. The default is False. If True there is an extra header row

    Returns
    -------
    worksheet : excel object
        DESCRIPTION. formattted spreadsheet

    """

    #dataframe = dataframe.replace(np.nan, "")

    dataframe = dataframe.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Set the column formats
    for col_num, col_name in enumerate(dataframe.columns):

        max_len = dataframe.iloc[1:,:][col_name].astype(str).str.len().max()

        if max_len > 6:
            max_len = 12
        elif max_len <= 6:
            max_len = 8.5

        worksheet.set_column(col_num, col_num, max_len, cell_format=style['default_col_format2'])


    if headerbuffer:

        first_row = 2
        last_row = 1

        worksheet.merge_range('A1:B1', 'Units: Meters', style['header_format3'])
        worksheet.merge_range('C1:E1', 'Observation Info', style['header_format2'])
        worksheet.merge_range('F1:H1', 'Distance Between Coordinates using Haversine',\
                              style['header_format2'])
        worksheet.merge_range('I1:K1', 'Available in Model', style['header_format2'])
        worksheet.merge_range('L1:T1', 'Distance Between Coordinates using Haversine',\
                              style['header_format2'])

        for col_num, value in enumerate(dataframe.columns.values):
            worksheet.write(1, col_num, value, style['header_format2'])
    else:
        first_row = 1
        last_row = 0
        # Wrap the headers
        for col_num, value in enumerate(dataframe.columns.values):
            worksheet.write(0, col_num, value, style['header_format2'])

    #Hyperlink on valid Hyperlink cells in Station ID. This is the best way...
    if "NWSLI" in dataframe.columns and headerbuffer:
        col_idx = dataframe.columns.get_loc("NWSLI")
        for idx, row in dataframe.iterrows():
            #print(row["CBITS"], type(row["CBITS"]), np.isnan(row["CBITS"]))
            if np.isnan(row["CBITS"]):
                worksheet.conditional_format(idx+2, col_idx, idx+2, col_idx,\
                                             {'type': 'no_errors',\
                                              'format':style['bright_red_fill_format']})



    if any(col in dataframe.columns for col in COLS_TO_FORMAT3):
        for col_name in COLS_TO_FORMAT3:
            if col_name in dataframe.columns:

                dataframe[col_name] = pd.to_numeric(dataframe[col_name], errors='coerce')


                worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                             last_row+len(dataframe.index),
                                             dataframe.columns.get_loc(col_name),
                                             {'type': 'blanks',
                                       'format': style["blank_white_fill_format"]})

                worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                             last_row+len(dataframe.index),
                                             dataframe.columns.get_loc(col_name),
                                             {'type': 'cell',
                                                'criteria': '>',
                                                'value': 10000,
                                                'format': style['bright_red_fill_format']})


                worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                             last_row+len(dataframe.index),
                                             dataframe.columns.get_loc(col_name),
                                             {'type': 'cell',
                                                'criteria': '>',
                                                'value': 1000,
                                                'format': style['red_fill_format']})


                worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                             last_row+len(dataframe.index),
                                             dataframe.columns.get_loc(col_name),
                                             {'type': 'cell',
                                                'criteria': '>',
                                                'value': 555,
                                                'format': style['light_yellow_fill_format']})


                worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                             last_row+len(dataframe.index),
                                             dataframe.columns.get_loc(col_name),
                                             {'type': 'cell',
                                                'criteria': '==',
                                                'value': 0,
                                                'format': style["bright_green_fill_format"]})


                worksheet.conditional_format(first_row, dataframe.columns.get_loc(col_name),
                                             last_row+len(dataframe.index),
                                             dataframe.columns.get_loc(col_name),
                                             {'type': 'cell',
                                                'criteria': '>',
                                                'value': 0,
                                                'format': style['light_green_fill_format']})

    redo_format4 = COLS_TO_FORMAT4 + ["REGION CBITS", "WFO CBITS", "STATE CBITS", "RFC CBITS",\
                                      "REGION AWIPS", "WFO AWIPS", "RFC AWIPS"]

    if any(col in dataframe.columns for col in redo_format4):
        for col_name in redo_format4:
            if col_name in dataframe.columns:
                col_idx = dataframe.columns.get_loc(col_name)
                # Apply the format to the entire column using numerical indices
                worksheet.set_column(col_idx, col_idx, None, style["regular_format"])
    return worksheet
