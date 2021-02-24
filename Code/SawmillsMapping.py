######################################################################################################
# import all required packages and functions
# from Functions import get_GM_API_Key
# from Functions import lumber_species_properties_processing
# from Functions import calculate_lumber_impact
# from Functions import calculate_distance
# from Functions import calculate_energy_impacts
from Google_Maps_Functions import *
import googlemaps
import gmaps
import gmaps.datasets
import json
import requests
import pandas as pd
import xlsxwriter
import warnings
warnings.filterwarnings('ignore')
import math as math
import numpy as np
#import matplotlib
import matplotlib.pyplot as plt

# from itertools import tee ##this line may not be needed


###import api_key from text file and configure the key
apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)
Sawmills_Data = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Mill Datasets/MasterDatasetSawmills.xlsx")
states_list = ["WA", "AR"]

Sawmills_WA = Sawmills_Data[Sawmills_Data["STATE"] == "WA"]
print(Sawmills_WA["STATE"])
Sawmills_AR = Sawmills_Data[Sawmills_Data["STATE"] == "AR"]

#Mills_WA = pd.read_excel('C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Forest_GIS_Data.xlsx', sheet_name='DFWA')
#Mills_AR = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/Mill Datasets/mill2005south.xls', sheet_name='AR')

###rows having Douglas fir in Washington
DFWA = pd.read_excel('C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Forest_GIS_Data_WA.xlsx')
print(DFWA.head())
###rows having loblolly pine in Arkansas
#LPAR = pd.read_excel('C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Forest_GIS_Data.xlsx', sheet_name='LPAR')
#("DONE")

Sawmills_WA["Total Area"] = 0
Sawmills_WA["Counted"] = ""
Sawmills_AR["Total Area"] = ""
Sawmills_AR["Counted"] = 0
count_mill = 0
index_count = 0

for index, row in Sawmills_WA.iterrows():
    mill_coordinates = str(row['LAT']) + ', ' + str(row['LON'])

    for index_f, row_f in DFWA.iterrows():
        forest_coordinates = str(row_f['G5km_Lat']) + ', ' + str(row_f['G5km_Lon'])
        distance_f_m = calculate_distance(forest_coordinates, mill_coordinates, apikey_text)

        print(index_f)
        print(distance_f_m)
        previous_total_area = Sawmills_WA["Total Area"].iloc[index_count]
        #print(row_f["Area_km2"])
        #print(previous_total_area)

        if distance_f_m <= 200:
            Sawmills_WA.loc[index, "Total Area"] = previous_total_area + row_f["Area_km2"]


        if (distance_f_m > 200) & (distance_f_m <= 225):
            Sawmills_WA.loc[index, "Total Area"] = previous_total_area + 0.5 * row_f["Area_km2"]
            #print(Sawmills_WA["Total Area"].iloc[index_count])
        if (distance_f_m > 225) & (distance_f_m <= 250):
            Sawmills_WA.loc[index, "Total Area"] = previous_total_area + 0.1 * row_f["Area_km2"]

        if Sawmills_WA["Total Area"].iloc[index_count] >= 5:
            #print(Sawmills_WA["Total Area"].iloc[index_count])
            break

        print(Sawmills_WA["Total Area"].iloc[index_count])

    if row["Total Area"] >= 5:
        Sawmills_WA.loc[index, "Counted"] = "Y"
    count_mill = count_mill + 1
    print(str("mill" + str(count_mill)))

    index_count = index_count + 1

Sawmills_WA.to_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Mill Datasets/DFWAcalculateddata.xlsx")

print("DONE DONE DONE")



