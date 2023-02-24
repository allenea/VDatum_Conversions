# VDatum_Conversions


Download VDatum_Conversions from github.

**Required Librarires:**
- Pandas
- Geopandas (with Fiona)
- Numpy
- BeautifulSoup
- Shapely
- os, sys, requests, json

**Required Data:**
- Download and unzip https://vdatum.noaa.gov/download/data/vdatum_regional_20221116.zip
- Download and unzip the following AWIPS Shapefiles: https://www.weather.gov/gis/AWIPSShapefiles

```
VDatum_Conversions
│   README.md
│   main.py (execute this file)
|   Obs_Location_Requests_Science_Eval.xlsx (INPUT)
|   NWM_TWL_Forecast_locations_SciEval.xlsx (OUTPUT)
│
└───src
│   │   __init__.py
│   │   check_url.py
│   │   excel_formatting.py
│   │   find_exception.py
│   │   get_urls.py
│   │   isrelation.py
│   │   read_join_nws_data.py
│   │   read_kml.py
│   │   read_vdatum_regions.py
│   │   tidesandcurrents_datum.py
│   │   usgs_datum.py
│   │   VDatum_Conversion.py
│   │   VDatum_Region_Selection.py
│
│   
└─── vdatum (REQUIRED: Download and unzip https://vdatum.noaa.gov/download/data/vdatum_regional_20221116.zip HERE)
    │   VariousFolders1
    │   VariousFolders2
    ....
└─── NWS_GIS_Data (REQUIRED: Download and unzip the following AWIPS Shapefiles HERE)
    │   c_08_mr23
    ----- c_08_mr23.shp
    │   mz08mr23
    ----- mz08mr23.shp
    |   rf12ja05
    ----- rf12ja05.shp
    |   w_08mr23
    ----- w_08mr23.shp
```
Once the required libraries are installed, you are on the internet, and you've downloaded and unpacked the vdatum files and AWIPS shapefiles, you can run the following program to process everything: main.py

Input file:
- NWM's Master List - Currently: Obs_Location_Requests_Science_Eval.xlsx

Output file:
- NWM_TWL_Forecast_locations_SciEval.xlsx
