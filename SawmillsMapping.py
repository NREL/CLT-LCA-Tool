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
##read Lumber GIS Data
Filtered_GIS_Data = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy.xlsx", sheet_name='SawmillTrial')

###read sawmills data  ###why only Washington?
Sawmills_data = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/GID data/SawmillData.xlsx", sheet_name='SMLocs')
Sawmills_state_map = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/GID data/SawmillData.xlsx", sheet_name='Sheet 2')
###add columns to the read data
Filtered_GIS_Data['Sawmills'] = ''
Filtered_GIS_Data['Distance'] = ''
######################################################################################################
###maybe make this code more efficient by using DistMatrix API only once for each cell and then lookup values from this one



for index, row in Filtered_GIS_Data.iterrows():

    ##create lists for each row entry in the data
    list_sawmills = list()
    dist = list()
    cell_loc = str(row['G1000_latdd']) + ', ' + str(row['G1000_longdd'])
    ### create an additional line of code to match with the state.
    for index1, row1 in Sawmills_data.iterrows():
        sawmill_loc = str(row1['LAT']) + ', ' + str(row1['LON'])
        #print(cell_loc)
        #print(sawmill_loc)
        if (row1["State_AB"] in row["States_Mapped"]):
            ##calculate distance between cell and sawmill
            distance_cell_sawmill = calculate_distance(cell_loc, sawmill_loc, apikey_text)

            if distance_cell_sawmill <= 150: ##change this number as and when required
                list_sawmills.append(row1['MILL2005_1'])
                ##appends distances from the cell to all sawmills only if it is lesser than a particular value ####change this value and make it variable for all regions
                dist.append(distance_cell_sawmill)

    ##list of acceptable sawmills for that cell location
    Filtered_GIS_Data['Sawmills'][index] = list_sawmills
    ##distances of the acceptable sawmills from that cell location
    Filtered_GIS_Data['Distance'][index] = dist

Filtered_GIS_Data.to_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy2.xlsx")

