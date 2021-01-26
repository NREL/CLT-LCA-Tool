######################################################################################################
##import modules
import googlemaps
import gmaps
import gmaps.datasets
import json
import requests
import pandas as pd
import xlsxwriter
import math as math
import numpy as np
import matplotlib.pyplot as plt

##import functions
from Google_Maps_Functions import get_GM_API_Key
# from Functions import lumber_species_properties_processing
# from Functions import calculate_lumber_impact
# from Functions import calculate_distance
# from Functions import calculate_energy_impacts

###read data from excel files


###import api_key from text file and configure the key
###this key will be required to calculate the distance between the clt mill and the building site
apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)

###Asking the user for the choice of the building
#building_choice = input("Enter your building choice number:")
building_choice = 1  ##default for now
#building_area_sqft_required = input("Enter the required building area in square feet (Integer values only):")
building_area_sqft_required = 8360 ##default for now
building_name_numbers = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name="Index")
building_name = building_name_numbers[building_name_numbers["Index"] == building_choice]["Building Name"].item()

building_info_CLT_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name=building_name, usecols='A:B', nrows=8, header=None)

building_inventory_table_CLT_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name=building_name, skiprows = 9, nrows= 40)

building_area_sqft_given_building = building_info_CLT_building.iloc[4][1]

multiplier = building_area_sqft_required/building_area_sqft_given_building

building_inventory_table_CLT_building["Normalized_Quantity_LCA"] = building_inventory_table_CLT_building["Quantity_LCA"] * multiplier

CLT_required = building_inventory_table_CLT_building.loc[building_inventory_table_CLT_building.Material == "CLT", 'Quantity'].sum()

###read data for concrete building

building_info_trad_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name='Lever_Concrete', usecols='A:B', nrows=8, header=None)

building_inventory_table_trad_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name='Lever_Concrete', skiprows=9,nrows=40)

