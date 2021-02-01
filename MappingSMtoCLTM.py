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

##load data
Filtered_GIS_Data = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy2.xlsx", sheet_name='SawmillTrial') ##TODO: sheetname = Sheet 1?
Sawmills_data_Washington = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/mill2005w.xlsx", sheet_name='Washington')

### create a list to include sawmills of interest
sawmill_list_grand = list()

####combine all sawmills into one grand list
for index, row in Filtered_GIS_Data.iterrows():
    sawmill_list_grand = sawmill_list_grand + (row['Sawmills'])
####remove duplicate sawmill IDs
sawmill_list_grand = list(set(sawmill_list_grand))

####create a new dataframe for mapping distances to CLT Location
Sawmill_CLTMill_distances = pd.DataFrame(columns=['Sawmill', 'Lat', 'Long', 'Distance'])
####add unique sawmill IDs to the dataframe
Sawmill_CLTMill_distances.assign(Sawmill=sawmill_list_grand)


###output a list with sawmill distance from the CLT mill###
CLTMillLocation = ''   #TODO: add location coordinates
for index, row in Sawmill_CLTMill_distances.iterrows():
    row['Lat'] = Sawmills_data_Washington.loc[Sawmills_data_Washington.MILL2005_1 == row['Sawmill'], 'LAT']
    row['Long'] = Sawmills_data_Washington.loc[Sawmills_data_Washington.MILL2005_1 == row['Sawmill'], 'LONG']
    Coordinates = str(row['Lat']) + ', ' + str(row['Long'])
    Sawmill_CLTMill_distances['Distance'][index] = calculate_distance(Coordinates, CLTMillLocation, apikey_text)

avg_sawmill_CLT_mill_distance = Sawmill_CLTMill_distances['Distance'].mean()