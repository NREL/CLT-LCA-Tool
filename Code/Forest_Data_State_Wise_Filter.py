###This code filters the original timber forestry dataset to include only the species suitable for clt manufacturing

######################################################################################################
# import all required packages and functions
# from Functions import get_GM_API_Key
# from Functions import lumber_species_properties_processing
# from Functions import calculate_lumber_impact
# from Functions import calculate_distance
# from Functions import calculate_energy_impacts
from Google_Maps_Functions import *
###import api_key from text file and configure the key
apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)
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
#import matplotlib.pypl

# from itertools import tee ##this line may not be needed

#base_name = 'G5km_OutputSummary'
Forest_Data_Filtered = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Mill Datasets/Forestry_Data_GIS/G5km_OutputSummary_Filtered.xlsx")
states = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Data Sheets/CLT_Timber_types.xlsx", sheet_name = 'State')
states_list = states["State"].tolist()

for state in states_list:
    state_forest_data = Forest_Data_Filtered[Forest_Data_Filtered["State_AB"] == state]
    state_forest_data.to_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Mill Datasets/Forestry_Data_GIS/Forestry_Data_GIS_by_State/G5km_OutputSummary_"+state+".xlsx", engine = 'xlsxwriter', index = False)

