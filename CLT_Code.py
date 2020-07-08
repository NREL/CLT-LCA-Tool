######################################################################################################
# import all required packages and functions
from Functions import get_GM_API_Key
from Functions import lumber_species_properties_processing
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

####################################################################################################

###import api_key from text file and configure the key
apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)

####################################################################################################

###add input panel here
####assume Katerra CLT building for now
building_choice = 1
building_location1 = '39.7392, -104.9903'
CLT_Sourcing_state = 'Washington'
timber_type = 'Douglas Fir'
timber_type_code = 29  ##write code to lookup the code
CLT_Mill_location1 ='42.8621, -112.4506' ### in Idaho

####################################################################################################

###import required Excel File/Sheets

###this sheet can map each state to its particular region: PNW, SE, NE-NC, INW, etc. ###
state_region_map = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx", sheet_name='State_Region_Map')

###this sheet has impacts of growing lumber in differnet areas ###
Lumber_production_impact = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Lumber Production- Energy')

###this sheet has inventory of manufacturing CLT###                                                                                             ####complete this process####
CLT_manufacturing_inventory = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='CLT Manufacturing Inventory')

###this sheet has impact values for electricity production in US states
Electricity_impact_energy = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Electricity by state- Energy', nrows=53)
Electricity_impact_CO2 = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Electricity by state- CO2', nrows=53)

###read in weight volume properties of timber
#in future, use this file for calculation using the waste percentage and delete the directly read in file.
#Lumber_species_properties = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/CLT_ Timber_types.xlsx', sheet_name='ALSC PS 20 Lumber Species', skiprows=[0])
lumber_species_properties_processed = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/CLT_ Timber_types.xlsx', sheet_name='ALSC PS 20 Lumber Species', skiprows=[0])

GIS_Data_with_sawmills = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy2.xlsx")

CLT_Manufacturing_energy_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='CLT Manufacturing- Energy')

CLT_Manufacturing_CO2_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='CLT Manufacturing- CO2')

transportation_energy_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Transportation- Energy')

transportation_CO2_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Transportation- CO2')

material_transport_distances = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Material Transport')
###################################################################################################

###derived variables###
CLT_Region = state_region_map.loc[state_region_map.State == CLT_Sourcing_state, 'Region'].item()

CLTM_to_Building_Distance = calculate_distance(CLT_Mill_location1, building_location1, apikey_text)

###################################################################################################

###Katerra = building choice 1 ###

if building_choice == 1:

    ###read in the materials inventory for the CLT building
    ###this sheet has basic building data : name, area, location, no of storeys, etc. ###
    building_inventories_info_CLT_building = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Building-Katerra', usecols='A:B', nrows=6, header=None)

    ###this sheet has the bill of materials###
    building_inventories_table_CLT_building = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Building-Katerra', skiprows=7)

    ###this sheet has the impacts of building materials
    building_material_impacts = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Material Impacts')

    ###read in the sq ft
    sq_ft_CLT_building = building_inventories_info_CLT_building.iloc[4][1]

    ###calculate total CLT required for the building
    CLT_required = building_inventories_table_CLT_building.loc[building_inventories_table_CLT_building.Material == "CLT", 'Normalized_Quantity'].sum()

################################################################################################################
###create results dataframes ###

energy_impacts_CLT = pd.DataFrame(columns=["Phase", "Renewable, wind, solar, geothe", "Renewable, biomass", "Non renewable, fossil", "Non-renewable, nuclear", "Renewable, water", "Non-renewable, biomass"])
phases_1 = ["Lumber Production", "Transport to CLT Mill", "CLT Manufacturing", "Transport to building site"]
energy_impacts_CLT["Phase"] = phases_1

energy_impacts_CLT_building = pd.DataFrame(columns=["Phase", "Renewable, wind, solar, geothe", "Renewable, biomass", "Non renewable, fossil", "Non-renewable, nuclear", "Renewable, water", "Non-renewable, biomass"])
phases_2 = ["A1-A3", "A4", "A5"]
energy_impacts_CLT_building["Phase"] = phases_2

################################################################################################################

###Lumber production impact###

waste_percentage = 16

#for now, this file has been directly read in through Excel. In further iteration, make this a variable by using the waste_percentage.

#lumber_species_properties_processed = lumber_species_properties_processing(waste_percentage, Lumber_species_properties)

###add values for lumber trasnport and processing

lumber_required = CLT_required * lumber_species_properties_processed.loc[lumber_species_properties_processed["ALSC PS 20 Commercial Species"] == timber_type, 'Total 12% Wood Vol Req (m3/m3 CLT)'].item()

energy_impacts_CLT[1][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Renewable, wind, solar, geothe"].item()
energy_impacts_CLT[2][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Renewable, biomass"].item()
energy_impacts_CLT[3][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Non renewable, fossil"].item()
energy_impacts_CLT[4][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Non-renewable, nuclear"].item()
energy_impacts_CLT[5][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Renewable, water"].item()
energy_impacts_CLT[6][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Non-renewable, biomass"].item()

################################################################################################################

###Lumber transportation impact###

####get dataframe file of GIS Data with appended sawmills and distances (file has been read in at the beginning of the code for now, change to read according to the state later

###this loop is not needed maybe
GIS_Data_with_sawmills['Distance_SM_CLTM'] = ''
distance_forest_sawmill = 0
no_of_calc_forest_sawmill = 0
for index, row in GIS_Data_with_sawmills.iterrows():
    if row["ForestType"] == timber_type:
        distance_forest_sawmill = distance_forest_sawmill + sum(row["Distance"])
        no_of_calc_forest_sawmill = no_of_calc_forest_sawmill + len(row["Distance"])

avg_distance_forest_sawmill = distance_forest_sawmill/no_of_calc_forest_sawmill


###get from MappintSMtoCLTM function: avg_sawmill_CLT_mill_distance

############Lumber transport to CLT Mill  ###############add truck loading factors#################****************
avg_sawmill_CLT_mill_distance = 2000
if avg_distance_forest_sawmill <= 200:   ###update the number
    energy_impacts_CLT[1][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[1][2]
    energy_impacts_CLT[2][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[2][2]
    energy_impacts_CLT[3][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[3][2]
    energy_impacts_CLT[4][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[4][2]
    energy_impacts_CLT[5][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[5][2]
    energy_impacts_CLT[6][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[6][2]

if avg_distance_forest_sawmill > 200:
    energy_impacts_CLT[1][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[1][1]
    energy_impacts_CLT[2][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[2][1]
    energy_impacts_CLT[3][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[3][1]
    energy_impacts_CLT[4][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[4][1]
    energy_impacts_CLT[5][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[5][1]
    energy_impacts_CLT[6][2] = avg_distance_forest_sawmill * transportation_energy_impact_factors[6][1]

######CLT transport to building site########  ###############add truck loading factors#################****************

if CLTM_to_Building_Distance <= 200:   ###update the number
    energy_impacts_CLT[1][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[1][2]
    energy_impacts_CLT[2][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[2][2]
    energy_impacts_CLT[3][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[3][2]
    energy_impacts_CLT[4][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[4][2]
    energy_impacts_CLT[5][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[5][2]
    energy_impacts_CLT[6][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[6][2]

if avg_distance_forest_sawmill > 200:
    energy_impacts_CLT[1][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[1][1]
    energy_impacts_CLT[2][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[2][1]
    energy_impacts_CLT[3][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[3][1]
    energy_impacts_CLT[4][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[4][1]
    energy_impacts_CLT[5][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[5][1]
    energy_impacts_CLT[6][2] = CLTM_to_Building_Distance * transportation_energy_impact_factors[6][1]

######CLT Manufacturing Impact#####

CLT_Mfc_Electricity = CLT_manufacturing_inventory.loc[CLT_manufacturing_inventory["Input"] == "Electricity"].sum()
CLT_Mfc_Energy_Impacts = pd.DataFrame(columns = ["Renewable, wind, solar, geothe", "Renewable, biomass", "Non renewable, fossil", "Non-renewable, nuclear", "Renewable, water", "Non-renewable, biomass"])
CLT_Mfc_Energy_Impacts = pd.concat(CLT_manufacturing_inventory, CLT_Mfc_Energy_Impacts)

for index, row in CLT_Mfc_Energy_Impacts.iterrows():
    if row["Input"] != "Electricity":
        CLT_Mfc_Energy_Impacts[4][index] = CLT_Mfc_Energy_Impacts[3][index] * CLT_Manufacturing_energy_impact_factors[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"]][1]
        CLT_Mfc_Energy_Impacts[5][index] = CLT_Mfc_Energy_Impacts[3][index] * CLT_Manufacturing_energy_impact_factors[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"]][2]
        CLT_Mfc_Energy_Impacts[6][index] = CLT_Mfc_Energy_Impacts[3][index] * CLT_Manufacturing_energy_impact_factors[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"]][3]
        CLT_Mfc_Energy_Impacts[7][index] = CLT_Mfc_Energy_Impacts[3][index] * CLT_Manufacturing_energy_impact_factors[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"]][4]
        CLT_Mfc_Energy_Impacts[8][index] = CLT_Mfc_Energy_Impacts[3][index] * CLT_Manufacturing_energy_impact_factors[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"]][5]
        CLT_Mfc_Energy_Impacts[9][index] = CLT_Mfc_Energy_Impacts[3][index] * CLT_Manufacturing_energy_impact_factors[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"]][6]

    if row["Input"] == "Electricity":
        CLT_Mfc_Energy_Impacts[4][index] = CLT_Mfc_Energy_Impacts[3][index] * Electricity_impact_energy[Electricity_impact_energy["State"] == CLT_Region][1]
        CLT_Mfc_Energy_Impacts[5][index] = CLT_Mfc_Energy_Impacts[3][index] * Electricity_impact_energy[Electricity_impact_energy["State"] == CLT_Region][2]
        CLT_Mfc_Energy_Impacts[6][index] = CLT_Mfc_Energy_Impacts[3][index] * Electricity_impact_energy[Electricity_impact_energy["State"] == CLT_Region][3]
        CLT_Mfc_Energy_Impacts[7][index] = CLT_Mfc_Energy_Impacts[3][index] * Electricity_impact_energy[Electricity_impact_energy["State"] == CLT_Region][4]
        CLT_Mfc_Energy_Impacts[8][index] = CLT_Mfc_Energy_Impacts[3][index] * Electricity_impact_energy[Electricity_impact_energy["State"] == CLT_Region][5]
        CLT_Mfc_Energy_Impacts[9][index] = CLT_Mfc_Energy_Impacts[3][index] * Electricity_impact_energy[Electricity_impact_energy["State"] == CLT_Region][6]


###assign values in the matrix
energy_impacts_CLT[1][2] = CLT_Mfc_Energy_Impacts["Renewable, wind, solar, geothe"].sum()
energy_impacts_CLT[2][2] = CLT_Mfc_Energy_Impacts["Renewable, biomass"].sum()
energy_impacts_CLT[3][2] = CLT_Mfc_Energy_Impacts["Non renewable, fossil"].sum()
energy_impacts_CLT[4][2] = CLT_Mfc_Energy_Impacts["Non-renewable, nuclear"].sum()
energy_impacts_CLT[5][2] = CLT_Mfc_Energy_Impacts["Renewable, water"].sum()
energy_impacts_CLT[6][2] = CLT_Mfc_Energy_Impacts["Non-renewable, biomass"].sum()

################## CLT Building Materials Impacts#################

CLT_building_materials_energy_impacts = pd.DataFrame(columns = ["Renewable, wind, solar, geothe", "Renewable, biomass", "Non renewable, fossil", "Non-renewable, nuclear", "Renewable, water", "Non-renewable, biomass"])

CLT_building_materials_mfc_energy_impacts = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_energy_impacts)



for index, row in CLT_building_materials_mfc_energy_impacts.iterrows():

    if row["Material"] != "CLT":
        CLT_building_materials_mfc_energy_impacts[8][index] = row['Normalized Quantity'] * building_material_impacts.loc[building_material_impacts.LCA_Material_Name == row['LCA_Material_Name']][1]
        CLT_building_materials_mfc_energy_impacts[9][index] = row['Normalized Quantity'] * building_material_impacts.loc[building_material_impacts.LCA_Material_Name == row['LCA_Material_Name']][2]
        CLT_building_materials_mfc_energy_impacts[10][index] = row['Normalized Quantity'] * building_material_impacts.loc[building_material_impacts.LCA_Material_Name == row['LCA_Material_Name']][3]
        CLT_building_materials_mfc_energy_impacts[11][index] = row['Normalized Quantity'] * building_material_impacts.loc[building_material_impacts.LCA_Material_Name == row['LCA_Material_Name']][4]
        CLT_building_materials_mfc_energy_impacts[12][index] = row['Normalized Quantity'] * building_material_impacts.loc[building_material_impacts.LCA_Material_Name == row['LCA_Material_Name']][5]
        CLT_building_materials_mfc_energy_impacts[13][index] = row['Normalized Quantity'] * building_material_impacts.loc[building_material_impacts.LCA_Material_Name == row['LCA_Material_Name']][6]


    if row["Material"] == "CLT":
        ###delete this particular row

####add row for total of all

CLT_building_materials_trans_energy_impacts = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_energy_impacts)

for index, row in CLT_building_materials_trans_energy_impacts.iterrows():
    if row["Material"] != "CLT":
        material_row_index = material_transport_distances.loc[material_transport_distances.LCA_Material_Name == row["Material"]]

    #### add impacts nos for road and rail
        CLT_building_materials_trans_energy_impacts[8][index] = row['Normalized Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])
        CLT_building_materials_trans_energy_impacts[9][index] = row['Normalized Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])
        CLT_building_materials_trans_energy_impacts[10][index] = row['Normalized Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])
        CLT_building_materials_trans_energy_impacts[11][index] = row['Normalized Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])
        CLT_building_materials_trans_energy_impacts[12][index] = row['Normalized Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])
        CLT_building_materials_trans_energy_impacts[13][index] = row['Normalized Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])

    if row["Material"] == "CLT":
        ###delete this particular row

####add row for total of all

##########################################
CLT_building_materials_mfc_energy_impacts = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_mfc_energy_impacts)




