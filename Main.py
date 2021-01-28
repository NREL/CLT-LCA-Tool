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

CLT_required = building_inventory_table_CLT_building.loc[building_inventory_table_CLT_building.Material == "CLT", 'Normalized_Quantity_LCA'].sum()

###read data for concrete building

building_info_trad_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name='Lever_Concrete', usecols='A:B', nrows=8, header=None)

building_inventory_table_trad_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name='Lever_Concrete', skiprows=9,nrows=40)

###create results dataframes ###

energy_impacts_CLT = pd.DataFrame(columns=["Phase", "Renewable, wind, solar, geothe", "Renewable, biomass", "Non renewable, fossil", "Non-renewable, nuclear", "Renewable, water", "Non-renewable, biomass"])
phases_1 = ["Lumber Production", "Transport to CLT Mill", "CLT Manufacturing", "Transport to building site"]
energy_impacts_CLT["Phase"] = phases_1

energy_impacts_CLT_building = pd.DataFrame(columns=["Phase", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ])
phases_2 = ["A1", "A2", "A3", "A4", "A5"]
energy_impacts_CLT_building["Phase"] = phases_2

###############################################################################################################
###module to calculate the impacts of lumber production###

###read timber data
timber_species_properties = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/CLT_Timber_types.xlsx",sheet_name="ALSC PS 20 Lumber Species",skiprows=1)

###waste_percentage = input("Enter the % of wood (by weight) lost in CLT manufacturing")
waste_percentage = 16

timber_species_properties["Final Product Weight (odkg/m3 CLT)_"] = timber_species_properties["Specific Gravity : 12%"]*1000
timber_species_properties["Co Products Weight (odkg/m3 CLT)_"] = timber_species_properties["Final Product Weight (odkg/m3 CLT)"]*waste_percentage/(100-waste_percentage)
timber_species_properties["Total Wood Weight (odkg/m3 CLT)_"] = timber_species_properties["Final Product Weight (odkg/m3 CLT)"] + timber_species_properties["Co Products Weight (odkg/m3 CLT)"]
timber_species_properties["Total 12% Wood Vol Req (m3/m3 CLT)_"] = timber_species_properties["Total Wood Weight (odkg/m3 CLT)"]/timber_species_properties["Specific Gravity : 12%"]/1000
timber_species_properties["Total Green Wood Vol Req (m3/m3 CLT)_"] = timber_species_properties["Total Wood Weight (odkg/m3 CLT)"]/timber_species_properties["Specific Gravity : Green"]/1000


#for now, this file has been directly read in through Excel. In further iteration, make this a variable by using the waste_percentage.

#lumber_species_properties_processed = lumber_species_properties_processing(waste_percentage, Lumber_species_properties)

###add values for lumber transport and processing

#lumber_required = CLT_required * lumber_species_properties_processed.loc[lumber_species_properties_processed["ALSC PS 20 Commercial Species"] == timber_type, 'Total 12% Wood Vol Req (m3/m3 CLT)'].item()