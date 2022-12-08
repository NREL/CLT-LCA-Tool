######################################################################################################
# import all required packages and functions
from Google_Maps_Functions import *
import googlemaps
import gmaps
import gmaps.datasets
import json
import requests
import pandas as pd
import math as math
import numpy

######################################################################################################
#import all mill files
mills_s = pd.read_excel(".../CLT-LCA-Tool/Mill Datasets/MasterDatasetMills.xlsx", sheet_name = "South")
mills_w = pd.read_excel(".../CLT-LCA-Tool/Mill Datasets/MasterDatasetMills.xlsx", sheet_name = "West")
mills_t = pd.read_excel(".../CLT-LCA-Tool/Mill Datasets/MasterDatasetMills.xlsx", sheet_name = "Texas")
mills_ne = pd.read_excel(".../CLT-LCA-Tool/Mill Datasets/MasterDatasetMills.xlsx", sheet_name = "NorthEast")
mills_nc = pd.read_excel(".../GitHub/CLT-LCA-Tool/Mill Datasets/MasterDatasetMills.xlsx", sheet_name = "NorthCentral")

mills_file_by_region = [mills_s,mills_w,mills_t,mills_ne,mills_nc]
mills_master_dataset = pd.DataFrame(columns=mills_s.columns)
sawmills_master_dataset = pd.DataFrame(columns=mills_s.columns)
for file in mills_file_by_region:
    filtered_file = file[(file["TYPE_NEW"].str.lower() == "sawmill") & (file["PRECISE_TY"].str.lower() == "sawmill")]
    sawmills_master_dataset = sawmills_master_dataset.append(filtered_file)
    mills_master_dataset = mills_master_dataset.append(file)


sawmills_master_dataset.insert(0,"Mill_ID_U", range(1, len(sawmills_master_dataset)+1))
mills_master_dataset.insert(0,"Mill_ID_U", range(1, len(mills_master_dataset)+1))
#print(mills_master_dataset)
sawmills_master_dataset.to_excel(".../CLT-LCA-Tool/Mill Datasets/Sawmills_Dataset.xlsx", engine = "xlsxwriter", index = False)
mills_master_dataset.to_excel(".../CLT-LCA-Tool/Mill Datasets/Mills_Dataset.xlsx", engine = "xlsxwriter", index = False)