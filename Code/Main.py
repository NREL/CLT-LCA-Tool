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
from Functions import *


###read data from excel files
Lumber_production_impact = pd.read_excel('C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/LCA_Impact_Values.xlsx', sheet_name='Lumber Production- Energy')
Lumber_production_impact_co2 = pd.read_excel('C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/LCA_Impact_Values.xlsx', sheet_name='Lumber Production- CO2', nrows=4)
state_region_map = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/LCA_Impact_Values.xlsx", sheet_name='State_Region_Map')


###read transportation impact data
transportation_energy_impact_factors = pd.read_excel('C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/LCA_Impact_Values.xlsx', sheet_name='Transportation- Energy')
transportation_CO2_impact_factors = pd.read_excel('C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/LCA_Impact_Values.xlsx', sheet_name='Transportation- CO2')


###read clt building config data
building_name_numbers = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name="Index")
building_info_CLT_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name=building_name, usecols='A:B', nrows=8, header=None)
building_inventory_table_CLT_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name=building_name, skiprows = 9, nrows= 40)
###read concrete building data
building_info_trad_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name='Lever_Concrete', usecols='A:B', nrows=8, header=None)
building_inventory_table_trad_building = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/Building_Configurations.xlsx", sheet_name='Lever_Concrete', skiprows=9,nrows=40)


###import api_key from text file and configure the key
###this key will be required to calculate the distance between the clt mill and the building site

apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)


###DUMMY CASES
#### CASES ###
####Case A
# CLTM_to_Building_Distance = 566
# avg_sawmill_CLT_mill_distance = 463
# CLT_Sourcing_state = 'Washington'
# CLT_Mill_State = "Washington"
# timber_type = 'Douglas Fir'
# Building_Site_state = "Oregon"
# avg_distance_forest_sawmill = 103 ##join code for real values

# ####Case B
# CLTM_to_Building_Distance = 3086
# avg_sawmill_CLT_mill_distance = 3724
# CLT_Sourcing_state = 'Washington'
# CLT_Mill_State = "Arkansas"
# timber_type = 'Douglas Fir'
# Building_Site_state = "California"
# avg_distance_forest_sawmill = 103 ##join code for real values

# ####Case C
# CLTM_to_Building_Distance = 455
# avg_sawmill_CLT_mill_distance = 2834
# CLT_Sourcing_state = 'Arkansas'
# CLT_Mill_State = "Maine"
# timber_type = 'Longleaf Pine'
# Building_Site_state = "Massachusetts"
# avg_distance_forest_sawmill = 91 ##join code for real values

# ####Case D
# CLTM_to_Building_Distance = 3792
# avg_sawmill_CLT_mill_distance = 3161
# CLT_Sourcing_state = 'Arkansas'
# CLT_Mill_State = "Washington"
# timber_type = 'Longleaf Pine'
# Building_Site_state = "Georgia"
# avg_distance_forest_sawmill = 91

###Asking the user for the choice of the building
#building_choice = input("Enter your building choice number:")
building_choice = 1  ##default for now

#building_area_sqft_required = input("Enter the required building area in square feet (Integer values only):")
building_area_sqft_required = 8360 ##default for now

building_name = building_name_numbers[building_name_numbers["Index"] == building_choice]["Building Name"].item()

building_area_sqft_given_building = building_info_CLT_building.iloc[4][1]

multiplier = building_area_sqft_required/building_area_sqft_given_building

building_inventory_table_CLT_building["Normalized_Quantity_LCA"] = building_inventory_table_CLT_building["Quantity_LCA"] * multiplier

CLT_required = building_inventory_table_CLT_building.loc[building_inventory_table_CLT_building.Material == "CLT", 'Normalized_Quantity_LCA'].sum()

#CLT_Sourcing_state = input("Enter CLT Sourcing State:")
CLT_Sourcing_state = "Arkansas"
CLT_Region = state_region_map.loc[state_region_map.State == CLT_Sourcing_state, 'Region'].item()

###create results dataframes ###

###this datafrane is just for the clt
energy_impacts_CLT = pd.DataFrame(columns=["Phase", "Renewable, wind, solar, geothe", "Renewable, biomass", "Non renewable, fossil", "Non-renewable, nuclear", "Renewable, water", "Non-renewable, biomass"])
phases_1 = ["Lumber Production", "Transport to CLT Mill", "CLT Manufacturing", "Transport to building site"]
energy_impacts_CLT["Phase"] = phases_1


###
energy_impacts_CLT_building = pd.DataFrame(columns=["Phase", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ])
phases_2 = ["A1", "A2", "A3", "A4", "A5"]
energy_impacts_CLT_building["Phase"] = phases_2

###############################################################################################################
###module to calculate the impacts of lumber production###

###read timber data
timber_species_properties = pd.read_excel("C:/Users/SATNOORK/Documents/GitHub/CLT-LCA-Tool/CLT_Timber_types.xlsx",sheet_name="ALSC PS 20 Lumber Species",skiprows=1)
##timber_type = input("Enter the timber species preferred for clt manufacturing")
timber_type = "Douglas Fir"
###waste_percentage = input("Enter the % of wood (by weight) lost in CLT manufacturing")
waste_percentage = 16

timber_species_properties = calc_timber_species_properties(timber_species_properties, waste_percentage)

###add values for lumber transport and processing

lumber_required = CLT_required * timber_species_properties.loc[timber_species_properties["ALSC PS 20 Commercial Species"] == timber_type, 'Total 12% Wood Vol Req (m3/m3 CLT)'].item()

#####################add to main results matrix
a = "Lumber Production"
b = "A1"
c = "CLT"
d, e, f, g, h, i = calculate_energy_impacts(lumber_required, Lumber_production_impact, "Region", CLT_Region)

co2 = lumber_required * Lumber_production_impact_co2.loc[Lumber_production_impact_co2["Region"] == CLT_Region, "Impact: CO2 emissions"].item()
##create main results matrix
results_bCLT_energy = pd.DataFrame([[a,b,c,d,e,f,g,h,i]], columns=["Process", "Phase", "Material", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ])
results_bCLT_CO2 = pd.DataFrame([[a,b,c,co2]], columns=["Process", "Phase" , "Material", "CO2"])

# ###########Lumber transport to CLT Mill  ###############assume 12% density#################****************

a = "Lumber Transport SM_CLT"
b = "A2"
c = "CLT"

if avg_sawmill_CLT_mill_distance <= 200:   ###update the number

    ###check###
    input_weight = avg_sawmill_CLT_mill_distance * (CLT_required *CLT_density_SM_CLTM + 5.4158) / 1000
    d, e, f, g, h, i = calculate_energy_impacts(input_weight, transportation_energy_impact_factors, "Vehicle", "Combination Truck (Short-haul)")

    co2 = avg_sawmill_CLT_mill_distance *(CLT_required * CLT_density_SM_CLTM + 5.4158) / 1000 * transportation_CO2_impact_factors.loc[
        transportation_CO2_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Impact: CO2 emissions"].item()

if avg_sawmill_CLT_mill_distance > 200:

    ###check###
    input_weight = avg_sawmill_CLT_mill_distance * (CLT_required * CLT_density_SM_CLTM + 5.4158) / 1000
    d, e, f, g, h, i = calculate_energy_impacts(input_weight, transportation_energy_impact_factors, "Vehicle", "Combination Truck (Long-haul)")

    co2 = avg_sawmill_CLT_mill_distance *(CLT_required * CLT_density_SM_CLTM + 5.4158)/ 1000 * transportation_CO2_impact_factors.loc[
        transportation_CO2_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Impact: CO2 emissions"].item()
results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a,b,c,d,e,f,g,h,i]],columns=["Process", "Phase" , "Material", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ]))
results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a,b,c,co2]],columns=["Process", "Phase" , "Material", "CO2" ]))

