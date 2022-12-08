###This code filters the original timber forestry dataset to include only the species suitable for clt manufacturing

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
#import matplotlib.pypl

# from itertools import tee ##this line may not be needed

Forest_Data = pd.read_excel(".../CLT-LCA-Tool/Mill Datasets/Forestry_Data_GIS/G5km_OutputSummary.xlsx")

#print(Forest_Data)

clt_suitable_species = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/CLT_Timber_types.xlsx", sheet_name = 'CLT_Suit_Species')

clt_suitable_species_list = clt_suitable_species["Forest_Type"].tolist()
timber_ownership_list = ['Other', 'PIF', 'PIO', 'PRV', 'PVT']

filter_suitable_species = Forest_Data["Forest_Type"].isin(clt_suitable_species_list)
print(filter_suitable_species)
Forest_Data_Filtered_1 = Forest_Data[filter_suitable_species]
filter_ownership = Forest_Data_Filtered_1["Ownership"].isin(timber_ownership_list)
print(filter_ownership)
Forest_Data_Filtered_2 = Forest_Data_Filtered_1[filter_ownership]

Forest_Data_Filtered_2.to_excel(".../CLT-LCA-Tool/Mill Datasets/Forestry_Data_GIS/G5km_OutputSummary_Filtered.xlsx", engine = 'xlsxwriter', index = False)

