######################################################################################################
# import all required packages and functions
from Functions import get_GM_API_Key
from Functions import lumberspeciespropoertiesprocessing
from Functions import calculate_lumber_impact
from Functions import calculate_distance
import googlemaps
import gmaps
import gmaps.datasets
import json
import requests
import pandas as pd
import math as math
import numpy

# from itertools import tee

######################################################################################################
###import api_key from text file and configure the key
apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)

######################################################################################################

Filtered_GIS_Data = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy.xlsx", sheet_name='SawmillTrial')
Sawmills_data_Washington = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/mill2005w.xlsx", sheet_name='Washington_SawmillTrial')
Filtered_GIS_Data['Sawmills'] = ''
Filtered_GIS_Data['Distance'] = ''
######################################################################################################

for index, row in Filtered_GIS_Data.iterrows():
    list_sawmills = list()
    dist = list()
    cell_loc = str(row['G1000_latdd']) + ', ' + str(row['G1000_longdd'])
    for index1, row1 in Sawmills_data_Washington.iterrows():
        sawmill_loc = str(row1['LAT']) + ', ' + str(row1['LON'])
        print(cell_loc)
        print(sawmill_loc)
        distance_cell_sawmill = calculate_distance(cell_loc, sawmill_loc, apikey_text)
        dist.append(distance_cell_sawmill)
        if distance_cell_sawmill <= 150: ##change this number as and when required
            list_sawmills.append(row1['MILL2005_1'])
    Filtered_GIS_Data['Sawmills'][index] = list_sawmills
    Filtered_GIS_Data['Distance'][index] = dist

Filtered_GIS_Data.to_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy2.xlsx")

