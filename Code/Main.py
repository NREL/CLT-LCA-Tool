######################################################################################################
##import modules required for the code
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

##import the user-defined functions
from Google_Maps_Functions import get_GM_API_Key
from Google_Maps_Functions import calculate_distance
from Functions import calc_timber_species_properties
from Functions import calculate_energy_impacts

###read data stored in the excel files

##Energy and CO2 impacts due to production of lumber. Source: CORRIM reports
Lumber_production_impact = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Lumber Production- Energy')
Lumber_production_impact_co2 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Lumber Production- CO2', nrows=4)

##table to map states to US regions (SE, PNW, INW, etc.)
state_region_map = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/State_Region_Map.xlsx", sheet_name='state_to_region')
state_region_map_ab  = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/State_Region_Map.xlsx", sheet_name='state_abbrv')

###Energy and CO2 impacts from transportation of goods
transportation_energy_impact_factors = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Transportation- Energy')
transportation_CO2_impact_factors = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Transportation- CO2')

###Data for stored building configurations
##table to map stored building names to their indices
building_name_numbers = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name="Index")

#TODO: DELETE WHEN EVERYTHING IS WORKING
building_area_sqft_required = 89989 ##default for now
building_area_sqm_required = building_area_sqft_required * 0.0929 ##conversion from sqft to sqm

###read the properties of timber species
timber_species_properties = pd.read_excel("...CLT-LCA-Tool/Data Sheets/CLT_Timber_types.xlsx",sheet_name="ALSC PS 20 Lumber Species",skiprows=1)

###read the inputs and quantities for CLT manufacturing
CLT_manufacturing_inventory = pd.read_excel('...CLT-LCA-Tool/Data Sheets/CLT_Manufacturing_Inputs.xlsx', sheet_name='Manufacturing Process Inputs', nrows=13)

###read the energy and CO2 impacts of electricity produced in different regions ##TODO: CONFIRM IF THIS IF FROM USLCI OR SIMAPRO
Electricity_impact_energy = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Electricity by state- Energy', usecols='A:G', nrows=53)
Electricity_impact_CO2 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Electricity by state- CO2', usecols='A:G', nrows=53)

###read the energy and CO2 impacts of CLT manufacturing inputs ##TODO: Cant be released publicly
CLT_Manufacturing_energy_impact_factors = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='CLT Manufacturing- Energy')
CLT_Manufacturing_CO2_impact_factors = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='CLT Manufacturing- CO2')

material_transport_distances = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name='Material Transport')

construction_fuels_CLT_building = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name='CLT Construction')

construction_fuels_trad_building = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name='Trad Construction')

###read the region-wise average transportation distances from forest to the sawmill
regional_forest_trans_dist = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Regional_Forest_Transport.xlsx")

###Input panel

# CLT_Sourcing_state = input("Enter the state from where the timber is being sourced: ")
# CLT_Mill_State = input("Enter the state from where the CLT mill is located: ")
# Timber_type = input("Enter the timber species: ")
# Building_Site_state = input("Enter the state from where the building is located: ")
# Asking the user for the choice of the building
# building_choice = input("Enter your building choice number:")
# building_area_sqft_required = input("Enter the required building area in square feet (Integer values only):")
# CLT_Mill_Lat = input("Enter the latitude of the CLT Mill")
# CLT_Mill_Long = input("Enter the longitude of the CLT Mill")
building_choice = 1  ##default for now
###TODO: Print building names here

###read building configurations data
###read the building name
building_name = building_name_numbers[building_name_numbers["Index"] == building_choice]["Building Name"].item()

###read the CLT building data
data_sheet_CLT_building = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name=building_name, header=None)

building_info_CLT_break_row = data_sheet_CLT_building[data_sheet_CLT_building.iloc[:, 0] == "Multiplier"].index[0]
building_info_CLT_building = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name=building_name, usecols='A:C', nrows = (building_info_CLT_break_row))

building_inventory_table_CLT_break_row = data_sheet_CLT_building[data_sheet_CLT_building.iloc[:, 0] == "END"].index[0]
building_inventory_table_CLT_building = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name=building_name, skiprows = (building_info_CLT_break_row+2), nrows= (building_inventory_table_CLT_break_row - building_info_CLT_break_row - 3))

building_area_sqft_default_CLT_building = building_info_CLT_building[building_info_CLT_building["Identifier"] == "Floor_Area_sqft"]["Value"]
building_area_multiplier_req_to_default_CLT = building_area_sqft_required/building_area_sqft_default_CLT_building

building_inventory_table_CLT_building["Normalized_Quantity_LCA"] = building_inventory_table_CLT_building["Quantity_LCA"] * building_area_multiplier_req_to_default_CLT.item()

###read concrete building data
data_sheet_trad_building = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name='Lever_Concrete', header=None)

building_info_trad_break_row = data_sheet_trad_building[data_sheet_trad_building.iloc[:, 0] == "Multiplier"].index[0]
building_info_trad_building = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name='Lever_Concrete', usecols='A:C', nrows=building_info_trad_break_row)

building_inventory_table_trad_break_row = data_sheet_trad_building[data_sheet_trad_building.iloc[:, 0] == "END"].index[0]
building_inventory_table_trad_building = pd.read_excel(".../CLT-LCA-Tool/Data Sheets/Building_Configurations.xlsx", sheet_name='Lever_Concrete', skiprows=(building_info_trad_break_row + 2),nrows= (building_inventory_table_trad_break_row - building_info_trad_break_row - 3))

building_area_sqft_default_trad_building = building_info_CLT_building[building_info_CLT_building["Identifier"] == "Floor_Area_sqft"]["Value"]
building_area_multiplier_req_to_default_trad = building_area_sqft_required/building_area_sqft_default_trad_building

building_inventory_table_trad_building["Normalized_Quantity_LCA"] = building_inventory_table_trad_building["Quantity_LCA"] * building_area_multiplier_req_to_default_trad.item()

CLT_required = building_inventory_table_CLT_building.loc[building_inventory_table_CLT_building.LCA_Material == "CLT", 'Normalized_Quantity_LCA'].sum()
##waste_percentage = input("Enter the % of wood (by weight) lost in CLT manufacturing")
waste_percentage = 16 ###default

## Analyzed CASES ###
##Case A
CLT_Sourcing_state = 'Washington'
CLT_Mill_State = "Washington"
timber_type = 'Douglas Fir'
Building_Site_state = "Oregon"
CLT_Mill_Lat = 47.6592
CLT_Mill_Long = -117.4231
Building_Lat = 45.5041
Building_Long = -122.6681

# ####Case B
# CLT_Sourcing_state = 'Washington'
# CLT_Mill_State = "Arkansas"
# timber_type = 'Douglas Fir'
# Building_Site_state = "California"
# CLT_Mill_Lat = 33.2520
# CLT_Mill_Long = -93.2379
# Building_Lat = 37.7677
# Building_Long = -122.3875

####Case C
# CLT_Sourcing_state = 'Arkansas'
# CLT_Mill_State = "Maine"
# timber_type = 'Longleaf Pine'
# Building_Site_state = "Massachusetts"
# CLT_Mill_Long = -68.5033
# CLT_Mill_Lat = 45.36221
# Building_Lat = 42.3576
# Building_Long = -71.0593

# ####Case D
# CLT_Sourcing_state = 'Arkansas'
# CLT_Mill_State = "Washington"
# timber_type = 'Longleaf Pine'
# Building_Site_state = "Georgia"
# CLT_Mill_Long = -117.4231
# CLT_Mill_Lat = 47.6592
# Building_Lat = 33.7519
# Building_Long = -84.3849

CLT_Region = state_region_map.loc[state_region_map.State == CLT_Sourcing_state, 'Region'].item()
CLT_Sourcing_state_ab = state_region_map_ab.loc[state_region_map_ab.State_Name == CLT_Sourcing_state, 'State'].item()
avg_distance_forest_sawmill = regional_forest_trans_dist.loc[regional_forest_trans_dist["Region"] == CLT_Region, 'Forest_Sawmill_Transport_Distance'].item()
###import api_key from text file and configure the key
###this key will be required to calculate the distance between the clt mill and the building site

apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)

###############################################################################################################
####calculate the distance between the sawmill and the CLT mill
sawmills_by_species_processed_data = pd.read_excel('.../CLT-LCA-Tool/Mill Datasets/state_timber_sawmill_dataset_' + CLT_Sourcing_state_ab + '.xlsx')
sawmills_filtered_by_species = sawmills_by_species_processed_data[sawmills_by_species_processed_data["Timber_Type"] == timber_type]
sawmills_filtered_by_species_y = sawmills_by_species_processed_data[sawmills_by_species_processed_data["Available"] == 'Y']
sawmills_filtered_by_species_n = sawmills_by_species_processed_data[sawmills_by_species_processed_data["Available"] == 'N']
sawmills_filtered_by_species_n["Total_plus_nan_area"] = sawmills_filtered_by_species_n["Total Area"] + sawmills_filtered_by_species_n["Nan Area"]
sawmills_filtered_by_species_n = sawmills_filtered_by_species_n[sawmills_filtered_by_species_n["Total_plus_nan_area"] > 15]
sawmills_filtered_by_species_n = sawmills_filtered_by_species_n.drop(["Total_plus_nan_area"], axis=1)
sawmills_filtered_by_species_all = sawmills_filtered_by_species_y.append(sawmills_filtered_by_species_n)
sawmills_filtered_by_species_all["Dist_i"] = 0
sawmills_filtered_by_species_all = sawmills_filtered_by_species_all.reset_index()
sawmills_filtered_by_species_all = sawmills_filtered_by_species_all.drop(["index"], axis = 1)

# for index, row in sawmills_filtered_by_species_all.iterrows():
#     #print(index)
#     saw_mill_coordinates = str(row['LAT']) + ', ' + str(row['LON'])
#     #print(saw_mill_coordinates)
#     # print(row["Mill_ID_U"])
#     clt_mill_coordinates = str(CLT_Mill_Lat) + ', ' + str(CLT_Mill_Long)
#     #print(clt_mill_coordinates)
#     sawmill_clt_dist_i = calculate_distance(saw_mill_coordinates, clt_mill_coordinates, apikey_text)
#     #print(sawmill_clt_dist_i)
#     sawmills_filtered_by_species_all.at[index, "Dist_i"] = sawmill_clt_dist_i
#     #print(sawmills_filtered_by_species_all)
#     print(index)
# print(sawmills_filtered_by_species_all)
# avg_dist_sawmill_CLT_mill = sawmills_filtered_by_species_all["Dist_i"].mean()
avg_dist_sawmill_CLT_mill = 481.1730

clt_mill_coordinates = str(CLT_Mill_Lat) + ', ' + str(CLT_Mill_Long)
building_coordinates = str(Building_Lat) + ', ' + str(Building_Long)
CLTM_to_Building_Distance = calculate_distance(clt_mill_coordinates, building_coordinates, apikey_text)

##############################################################################################################

timber_species_properties_processed = calc_timber_species_properties(timber_species_properties, waste_percentage)
CLT_density_SM_CLTM = 1.19/1.12 * timber_species_properties_processed.loc[timber_species_properties_processed["ALSC PS 20 Commercial Species"] == timber_type, 'Weight (kg/m3) : 12%'].item()
###standards say moisture content after processing in sawmill is 19 %
CLT_density_CLTM_BuildingSite = timber_species_properties_processed.loc[timber_species_properties_processed["ALSC PS 20 Commercial Species"] == timber_type, 'Weight (kg/m3) : 12%'].item()

###add values for lumber transport and processing

lumber_required = CLT_required * timber_species_properties.loc[timber_species_properties["ALSC PS 20 Commercial Species"] == timber_type, 'Total 12% Wood Vol Req (m3/m3 CLT)'].item()
####################################################

###TODO: These sheets cannot be released publicly
construction_impacts_energy = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Construction- Energy')

construction_impacts_CO2 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Construction- CO2')

building_material_impacts_a1 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Material Impacts- Energy A1')

building_material_impacts_a2 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Material Impacts- Energy A2')

building_material_impacts_a3 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Material Impacts- Energy A3')

building_material_impacts_co2_a1 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Material Impacts- CO2 A1')

building_material_impacts_co2_a2 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Material Impacts- CO2 A2')

building_material_impacts_co2_a3 = pd.read_excel('.../CLT-LCA-Tool/Data Sheets/LCA_Impact_Values.xlsx', sheet_name='Material Impacts- CO2 A3')

###this datafrane is just for the clt
##TODO: Does this order need to be corrected?
energy_impacts_CLT = pd.DataFrame(columns=["Phase", "Renewable, wind, solar, geothe", "Renewable, biomass", "Non renewable, fossil", "Non-renewable, nuclear", "Renewable, water", "Non-renewable, biomass"])
###TODO: Do we need this phases? Or are changes required here?
phases_1 = ["Lumber Production", "Transport to CLT Mill", "CLT Manufacturing", "Transport to building site"]
energy_impacts_CLT["Phase"] = phases_1

###
energy_impacts_CLT_building = pd.DataFrame(columns=["Phase", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ])
###TODO: Do we need this phases? Or are changes required here?
phases_2 = ["A1", "A2", "A3", "A4", "A5"]
energy_impacts_CLT_building["Phase"] = phases_2
print("abcd")
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

if avg_dist_sawmill_CLT_mill <= 200:   ###update the number

    ###check###
    input_weight = avg_dist_sawmill_CLT_mill * (CLT_required * CLT_density_SM_CLTM + 5.4158) / 1000
    d, e, f, g, h, i = calculate_energy_impacts(input_weight, transportation_energy_impact_factors, "Vehicle", "Combination Truck (Short-haul)")

    co2 = input_weight * transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Impact: CO2 emissions"].item()

if avg_dist_sawmill_CLT_mill > 200:

    ###check###
    input_weight = avg_dist_sawmill_CLT_mill * (CLT_required * CLT_density_SM_CLTM + 5.4158) / 1000
    d, e, f, g, h, i = calculate_energy_impacts(input_weight, transportation_energy_impact_factors, "Vehicle", "Combination Truck (Long-haul)")

    co2 = input_weight * transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Impact: CO2 emissions"].item()

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a,b,c,d,e,f,g,h,i]],columns=["Process", "Phase" , "Material", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ]))
results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a,b,c,co2]],columns=["Process", "Phase" , "Material", "CO2" ]))

######CLT transport to building site########  ###############assume 12% density#################****************
a = "CLT Transport CLT Mill_BuildingSite"
b = "A4"
c = "CLT"

if CLTM_to_Building_Distance <= 322:   ###in km ##taken from USLCI process documentation ### how many tonnes???
    input_weight = CLTM_to_Building_Distance * (CLT_required * CLT_density_CLTM_BuildingSite + 5.4158) / 1000
    d, e, f, g, h, i = calculate_energy_impacts(input_weight, transportation_energy_impact_factors, "Vehicle", "Combination Truck (Short-haul)")

    co2 = input_weight * transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Impact: CO2 emissions"].item()

if CLTM_to_Building_Distance > 322:
    input_weight = CLTM_to_Building_Distance * (CLT_required * CLT_density_CLTM_BuildingSite + 5.4158) / 1000

    d, e, f, g, h, i = calculate_energy_impacts(input_weight, transportation_energy_impact_factors, "Vehicle", "Combination Truck (Short-haul)")

    co2 = input_weight * transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Impact: CO2 emissions"].item()

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a,b,c,d,e,f,g,h,i]],columns=["Process", "Phase" , "Material", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ] ))
results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a,b,c,co2]],columns=["Process", "Phase" , "Material", "CO2" ]))
##################################################################################################

######CLT Manufacturing Impact#####

CLT_Mfc_Electricity = CLT_manufacturing_inventory.loc[CLT_manufacturing_inventory["Input"] == "Electricity"].sum()
#CLT_Mfc_Energy_Impacts = pd.DataFrame(columns = ["Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water"])
#CLT_Mfc_Energy_Impacts = pd.concat(CLT_manufacturing_inventory, CLT_Mfc_Energy_Impacts)

#row_no_used = len(results_bCLT_energy.index)

for index, row in CLT_manufacturing_inventory.iterrows():
    a = row["Process"]
    b = "A3"
    c = "CLT"
    if row["Input"] != "Electricity":
        Mat_or_fuel_amount_required = CLT_required * row["Amount (Baseline)"]
        d, e, f, g, h, i = calculate_energy_impacts(Mat_or_fuel_amount_required, CLT_Manufacturing_energy_impact_factors, "Material", row["Input"])

        co2 = CLT_required *row["Amount (Baseline)"] * CLT_Manufacturing_CO2_impact_factors.loc[CLT_Manufacturing_CO2_impact_factors["Material"] == row["Input"],"Impact: CO2 emissions"].item()

    if row["Input"] == "Electricity":
        Electricity_required = CLT_required * row["Amount (Baseline)"]
        d, e, f, g, h, i = calculate_energy_impacts(Electricity_required, Electricity_impact_energy, "State", CLT_Mill_State)

        co2 = Electricity_required * Electricity_impact_CO2.loc[Electricity_impact_CO2["State"] == CLT_Mill_State,"CO2"].item()

    results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]], columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
    results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

d_road, e_road, f_road, g_road, h_road, i_road = calculate_energy_impacts(1,transportation_energy_impact_factors,"Vehicle","Combination Truck (Long-haul)")
d_rail, e_rail, f_rail, g_rail, h_rail, i_rail = calculate_energy_impacts(1, transportation_energy_impact_factors, "Vehicle", "Transport, Rail")

###TODO is this A2 or A3
###for clt this is A2, but for the building it will be included in A3
for index, row in CLT_manufacturing_inventory.iterrows():
    a = row["Process"]
    b = "A3"
    c = "CLT"

    if row["Input"] != "Electricity" and row["Input"] != "Natural Gas":
        material_row_index = material_transport_distances.index[material_transport_distances["LCA_Material"] == row["Input"]]
        co2_road = transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Impact: CO2 emissions"]

        co2_rail = transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Transport, Rail", "Impact: CO2 emissions"]

        d = CLT_required * (row['Amount (Baseline)'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * d_road + material_transport_distances["Rail"][material_row_index].item() * d_rail)).item()
        e = CLT_required * (row['Amount (Baseline)'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * e_road + material_transport_distances["Rail"][material_row_index].item() * e_rail)).item()
        f = CLT_required * (row['Amount (Baseline)'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * f_road + material_transport_distances["Rail"][material_row_index].item() * f_rail)).item()
        g = CLT_required * (row['Amount (Baseline)'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * g_road + material_transport_distances["Rail"][material_row_index].item() * g_rail)).item()
        h = CLT_required * (row['Amount (Baseline)'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * h_road + material_transport_distances["Rail"][material_row_index].item() * h_rail)).item()
        i = CLT_required * (row['Amount (Baseline)'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * i_road + material_transport_distances["Rail"][material_row_index].item() * i_rail)).item()
        co2 = CLT_required * (row['Amount (Baseline)'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * co2_road.item() + material_transport_distances["Rail"][material_row_index].item() * co2_rail.item())).item()

        results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],
                                                                      columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass",
                                                                               "Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
        results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

################## CLT Building Materials Impacts#################

#CLT_building_materials_mfc_energy_impacts = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_energy_impacts)

##correct 20
for index, row in building_inventory_table_CLT_building.iterrows():

    a = row["LCA_Material"]      ##+ production?
    b = 'A1'
    if row["Building_Inventory_Material"] != "CLT":
        c = "Other"
        d, e, f, g, h, i = calculate_energy_impacts(row['Normalized_Quantity_LCA'], building_material_impacts_a1, "Material", row['LCA_Material'])

        co2 = row['Normalized_Quantity_LCA'] * building_material_impacts_co2_a1.loc[building_material_impacts_co2_a1.Material == row['LCA_Material'], "Impact: CO2 emissions"].item()

        results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],
                                                                      columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass",
                                                                               "Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
        results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

    a = row["Building_Inventory_Material"]  ##+ production?
    b = 'A2'
    if row["Building_Inventory_Material"] != "CLT":
        c = "Other"
        d, e, f, g, h, i = calculate_energy_impacts(row['Normalized_Quantity_LCA'], building_material_impacts_a2, "Material", row['LCA_Material'])

        co2 = row['Normalized_Quantity_LCA'] * building_material_impacts_co2_a2.loc[building_material_impacts_co2_a2.Material == row['LCA_Material'], "Impact: CO2 emissions"].item()

        results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],
                                                                      columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass",
                                                                               "Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
        results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

    a = row["LCA_Material"]  ##+ production?
    b = 'A3'
    if row["Building_Inventory_Material"] != "CLT":
        c = "Other"
        d, e, f, g, h, i = calculate_energy_impacts(row['Normalized_Quantity_LCA'], building_material_impacts_a3, "Material", row['LCA_Material'])

        co2 = row['Normalized_Quantity_LCA'] * building_material_impacts_co2_a3.loc[building_material_impacts_co2_a3.Material == row['LCA_Material'], "Impact: CO2 emissions"].item()

        results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],
                                                                      columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass",
                                                                               "Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
        results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

###add row for total of all
d_road, e_road, f_road, g_road, h_road, i_road = calculate_energy_impacts(1, transportation_energy_impact_factors, "Vehicle", "Combination Truck (Long-haul)")

d_rail, e_rail, f_rail, g_rail, h_rail, i_rail = calculate_energy_impacts(1, transportation_energy_impact_factors, "Vehicle", "Transport, Rail")

for index, row in building_inventory_table_CLT_building.iterrows():

    a = row["LCA_Material"]
    b = 'A4'
    if row["LCA_Material"] != "CLT":
        c = "Other"
        material_row_index = material_transport_distances.index[material_transport_distances["LCA_Material"] == row["LCA_Material"]]
        #### add impacts nos for road and rail

        co2_road = transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Impact: CO2 emissions"]

        co2_rail = transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Transport, Rail", "Impact: CO2 emissions"]

        d = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index].item() * d_road + material_transport_distances["Rail"][material_row_index].item() * d_rail)).item()
        e = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index].item() * e_road + material_transport_distances["Rail"][material_row_index].item() * e_rail)).item()
        f = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index].item() * f_road + material_transport_distances["Rail"][material_row_index].item() * f_rail)).item()
        g = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index].item() * g_road + material_transport_distances["Rail"][material_row_index].item() * g_rail)).item()
        h = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index].item() * h_road + material_transport_distances["Rail"][material_row_index].item() * h_rail)).item()
        i = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index].item() * i_road + material_transport_distances["Rail"][material_row_index].item() * i_rail)).item()
        co2 = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index].item() * co2_road.item() + material_transport_distances["Rail"][material_row_index].item() * co2_rail.item())).item()

        results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],
                                                                      columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass",
                                                                               "Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
        results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

###add row for total of all

##################################################################################################
#CLT_building_materials_mfc_energy_impacts = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_mfc_energy_impacts)

##########################################
construction_fuels_CLT_building_1 = construction_fuels_CLT_building[["Fuel", "Amount"]]
##convert amount to L or kWh from L/sqm to kWh/sqm
construction_fuels_CLT_building_1["Amount"] = construction_fuels_CLT_building_1["Amount"] * building_area_sqft_default_CLT_building.item() * 0.092903  ###factor converts sqm to sqft ##amount in L ##amount in kWh
##################################################################################################

# CLT_building_materials_const_energy_impacts = pd.DataFrame(columns = ["Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ])
# CLT_building_materials_const_energy_impacts = pd.concat(construction_fuels_CLT_building_1, CLT_building_materials_const_energy_impacts)
#calculations for diesel
a = "Construction Machinery- Diesel"
b = "A5"
c = "NA"

d, e, f, g, h, i = calculate_energy_impacts(construction_fuels_CLT_building_1["Amount"][0]/1000, construction_impacts_energy, "Process", "Diesel")
co2 = construction_fuels_CLT_building_1["Amount"][0] * construction_impacts_CO2.loc[construction_impacts_CO2.Process == "Diesel", "Impact: CO2 emissions"].item()/1000

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))
##################################################################################################
#Electricity_impact_energy.loc[Electricity_impact_energy["State"] == Building_Site_state,"Non renewable, fossil"].item()
#calculations for gasoline
a = "Construction Machinery- Gasoline"
b = "A5"
c = "NA"

d, e, f, g, h, i = calculate_energy_impacts(construction_fuels_CLT_building_1["Amount"][1]/1000, construction_impacts_energy, "Process", "Gasoline")

co2 = construction_fuels_CLT_building_1["Amount"][1] * construction_impacts_CO2.loc[construction_impacts_CO2.Process == "Gasoline", "Impact: CO2 emissions"].item()/1000

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))
#calculations for electricity
a = "Construction Machinery- Electricity"
b = "A5"
c = "NA"

d,e,f,g,h,i = calculate_energy_impacts(construction_fuels_CLT_building_1["Amount"][2], Electricity_impact_energy, "State", Building_Site_state)

co2 = construction_fuels_CLT_building_1["Amount"][2] * Electricity_impact_CO2.loc[Electricity_impact_CO2["State"] == Building_Site_state,"CO2"].item()

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bCLT_CO2 = results_bCLT_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

##############################################################################################################################################
####trad building calculations start here
results_bTrad_energy = pd.DataFrame(columns= ["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"])
results_bTrad_CO2 = pd.DataFrame(columns= ["Process", "Phase", "Material", "CO2"])

for index, row in building_inventory_table_trad_building.iterrows():

    a = row["LCA_Material"]      ##+ production?
    b = 'A1'
    if row["Building_Inventory_Material"] != "CLT":  ##this might not be needed as there is no CLT
        c = "Other"

        d, e, f, g, h, i = calculate_energy_impacts(row['Normalized_Quantity_LCA'], building_material_impacts_a1, "Material", row['LCA_Material'])

        co2 = row['Normalized_Quantity_LCA'] * building_material_impacts_co2_a1.loc[building_material_impacts_co2_a1.Material == row['LCA_Material'], "Impact: CO2 emissions"].item()

    results_bTrad_energy = results_bTrad_energy.append(pd.DataFrame([[a,b,c,d,e,f,g,h,i]],columns=["Process", "Phase" , "Material", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ] ))
    results_bTrad_CO2 = results_bTrad_CO2.append(pd.DataFrame([[a,b,c,co2]],columns=["Process", "Phase" , "Material", "CO2" ]))

    a = row["LCA_Material"]  ##+ production?
    b = 'A2'
    if row["Building_Inventory_Material"] != "CLT":  ##this might not be needed as there is no CLT
        c = "Other"

        d, e, f, g, h, i = calculate_energy_impacts(row['Normalized_Quantity_LCA'], building_material_impacts_a2, "Material", row['LCA_Material'])

        co2 = row['Normalized_Quantity_LCA'] * building_material_impacts_co2_a2.loc[building_material_impacts_co2_a2.Material == row['LCA_Material'], "Impact: CO2 emissions"].item()

    results_bTrad_energy = results_bTrad_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],
                                                                    columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass",
                                                                             "Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
    results_bTrad_CO2 = results_bTrad_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

    a = row["LCA_Material"]  ##+ production?
    b = 'A3'
    if row["Building_Inventory_Material"] != "CLT":  ##this might not be needed as there is no CLT
        c = "Other"

        d, e, f, g, h, i = calculate_energy_impacts(row['Normalized_Quantity_LCA'], building_material_impacts_a3, "Material", row['LCA_Material'])

        co2 = row['Normalized_Quantity_LCA'] * building_material_impacts_co2_a3.loc[building_material_impacts_co2_a3.Material == row['LCA_Material'], "Impact: CO2 emissions"].item()

    results_bTrad_energy = results_bTrad_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],
                                                                    columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass",
                                                                             "Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
    results_bTrad_CO2 = results_bTrad_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

#######################################################################################################
d_road, e_road, f_road, g_road, h_road, i_road = calculate_energy_impacts(1, transportation_energy_impact_factors, "Vehicle", "Combination Truck (Long-haul)")
d_rail, e_rail, f_rail, g_rail, h_rail, i_rail = calculate_energy_impacts(1, transportation_energy_impact_factors, "Vehicle", "Transport, Rail")

for index, row in building_inventory_table_trad_building.iterrows():

    a = row["LCA_Material"]
    b = 'A4'
    if row["LCA_Material"] != "CLT":
        c = "Other"

        co2_road = transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Impact: CO2 emissions"]

        co2_rail = transportation_CO2_impact_factors.loc[transportation_CO2_impact_factors.Vehicle == "Transport, Rail", "Impact: CO2 emissions"]

        material_row_index = material_transport_distances.index[material_transport_distances["LCA_Material"] == row["LCA_Material"]]
        #### add impacts nos for road and rail
        d = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * d_road + material_transport_distances["Rail"][material_row_index].item() * d_rail)).item()
        e = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * e_road + material_transport_distances["Rail"][material_row_index].item() * e_rail)).item()
        f = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * f_road + material_transport_distances["Rail"][material_row_index].item() * f_rail)).item()
        g = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * g_road + material_transport_distances["Rail"][material_row_index].item() * g_rail)).item()
        h = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * h_road + material_transport_distances["Rail"][material_row_index].item() * h_rail)).item()
        i = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * i_road + material_transport_distances["Rail"][material_row_index].item() * i_rail)).item()
        co2 = (row['Normalized_Quantity_Weight'] * material_transport_distances["Factor"][material_row_index] * (
                    material_transport_distances["Road"][material_row_index].item() * co2_road.item() + material_transport_distances["Rail"][material_row_index].item() * co2_rail.item())).item()

    #if row["Material"] == "CLT":
        ###delete this particular row

    results_bTrad_energy = results_bTrad_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]], columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
    results_bTrad_CO2 = results_bTrad_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

#CLT_building_materials_mfc_energy_impacts = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_mfc_energy_impacts)

##########################################
construction_fuels_trad_building_1 = construction_fuels_trad_building[["Fuel", "Amount"]]
##convert amount to L or kWh from L/sqm to kWh/sqm
construction_fuels_trad_building_1["Amount"] = construction_fuels_trad_building_1["Amount"] * building_area_sqft_required * 0.092903  ###factor converts sqm to sqft ##amount in L ##amount in kWh
##################################################################################################

#calculations for diesel
a = "Construction Machinery- Diesel"
b = "A5"
c = "NA"

d, e, f, g, h, i = calculate_energy_impacts(construction_fuels_trad_building_1["Amount"][0]/1000, construction_impacts_energy, "Process", "Diesel")

co2 = construction_fuels_trad_building_1["Amount"][0] * construction_impacts_CO2.loc[construction_impacts_CO2.Process == "Diesel", "Impact: CO2 emissions"].item() /1000

results_bTrad_energy = results_bTrad_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bTrad_CO2 = results_bTrad_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))
##################################################################################################
#calculations for gasoline
a = "Construction Machinery- Gasoline"
b = "A5"
c = "NA"

d, e, f, g, h, i = calculate_energy_impacts(construction_fuels_trad_building_1["Amount"][1]/1000, construction_impacts_energy, "Process", "Gasoline")

co2 = construction_fuels_trad_building_1["Amount"][1] * construction_impacts_CO2.loc[construction_impacts_CO2.Process == "Gasoline", "Impact: CO2 emissions"].item()/1000

results_bTrad_energy = results_bTrad_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bTrad_CO2 = results_bTrad_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))
#calculations for electricity
a = "Construction Machinery- Electricity"
b = "A5"
c = "NA"

d, e, f, g, h, i = calculate_energy_impacts(construction_fuels_trad_building_1["Amount"][2], Electricity_impact_energy, "State", Building_Site_state)

co2 = construction_fuels_trad_building_1["Amount"][2] * Electricity_impact_CO2.loc[Electricity_impact_CO2["State"] == Building_Site_state,"CO2"].item()

results_bTrad_energy = results_bTrad_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bTrad_CO2 = results_bTrad_CO2.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

###################################################################################################

results_bCLT_energy["Total Energy"] = results_bCLT_energy.apply(lambda row: row[3] + row[4] + row[5] + row[6] + row[7] + row[8], axis=1)

results_bTrad_energy["Total Energy"] = results_bTrad_energy.apply(lambda row: row[3] + row[4] + row[5] + row[6] + row[7] + row[8], axis=1)

results_bCLT_energy_scaled = results_bCLT_energy
results_bCLT_energy_scaled["Non renewable, fossil"] = results_bCLT_energy_scaled["Non renewable, fossil"] / 1000000
results_bCLT_energy_scaled["Non-renewable, nuclear"] = results_bCLT_energy_scaled["Non-renewable, nuclear"] / 1000000
results_bCLT_energy_scaled["Non-renewable, biomass"] = results_bCLT_energy_scaled["Non-renewable, biomass"] / 1000000
results_bCLT_energy_scaled["Renewable, wind, solar, geothe"] = results_bCLT_energy_scaled["Renewable, wind, solar, geothe"] / 1000000
results_bCLT_energy_scaled["Renewable, biomass"] = results_bCLT_energy_scaled["Renewable, biomass"] / 1000000
results_bCLT_energy_scaled["Renewable, water"] = results_bCLT_energy_scaled["Renewable, water"] / 1000000
results_bCLT_energy_scaled["Total Energy"] = results_bCLT_energy_scaled["Total Energy"] / 1000000

results_bTrad_energy_scaled = results_bTrad_energy
results_bTrad_energy_scaled["Non renewable, fossil"] = results_bTrad_energy_scaled["Non renewable, fossil"] / 1000000
results_bTrad_energy_scaled["Non-renewable, nuclear"] = results_bTrad_energy_scaled["Non-renewable, nuclear"] / 1000000
results_bTrad_energy_scaled["Non-renewable, biomass"] = results_bTrad_energy_scaled["Non-renewable, biomass"] / 1000000
results_bTrad_energy_scaled["Renewable, wind, solar, geothe"] = results_bTrad_energy_scaled["Renewable, wind, solar, geothe"] / 1000000
results_bTrad_energy_scaled["Renewable, biomass"] = results_bTrad_energy_scaled["Renewable, biomass"] / 1000000
results_bTrad_energy_scaled["Renewable, water"] = results_bTrad_energy_scaled["Renewable, water"] / 1000000
results_bTrad_energy_scaled["Total Energy"] = results_bTrad_energy_scaled["Total Energy"] / 1000000

results_bCLT_CO2_scaled = results_bCLT_CO2
results_bCLT_CO2_scaled["CO2"] = results_bCLT_CO2_scaled["CO2"]/1000000

results_bTrad_CO2_scaled = results_bTrad_CO2
results_bTrad_CO2_scaled["CO2"] = results_bTrad_CO2_scaled["CO2"]/1000000

#graph_summed_1_energy = results_bCLT_energy.groupby(by = "Phase")['Total Energy'].sum()

a = results_bCLT_energy.query("Phase == 'A1'")["Total Energy"].sum()
b = results_bCLT_energy.query("Phase == 'A2'")["Total Energy"].sum()
c = results_bCLT_energy.query("Phase == 'A3'")["Total Energy"].sum()
d = results_bCLT_energy.query("Phase == 'A4'")["Total Energy"].sum()
e = results_bCLT_energy.query("Phase == 'A5'")["Total Energy"].sum()

graph_1_energy = pd.DataFrame([[a,b,c]], columns = ["A1-A3", "A4", "A5"])

a = results_bTrad_energy.query("Phase == 'A1'")["Total Energy"].sum()
b = results_bTrad_energy.query("Phase == 'A2'")["Total Energy"].sum()
c = results_bTrad_energy.query("Phase == 'A3'")["Total Energy"].sum()
d = results_bTrad_energy.query("Phase == 'A4'")["Total Energy"].sum()
e = results_bTrad_energy.query("Phase == 'A5'")["Total Energy"].sum()

#c = results_bTrad_energy.query("Phase == 'A5'")["Total Energy"].sum()  ##remove comment after correcting the construction section

graph_1_energy = graph_1_energy.append(pd.DataFrame([[a,b,c]], columns = ["A1-A3", "A4", "A5"]))
graph_1_energy.index = ['CLT_Building', 'Traditional_Building']

results_bCLT_energy_scaled_grouped = results_bCLT_energy_scaled.groupby(['Process','Phase'])[['Non renewable, fossil','Non-renewable, nuclear', 'Non-renewable, biomass', 'Renewable, wind, solar, geothe', 'Renewable, biomass', 'Renewable, water', 'Total Energy' ]].sum()
results_bTrad_energy_scaled_grouped = results_bTrad_energy_scaled.groupby(['Process','Phase'])[['Non renewable, fossil','Non-renewable, nuclear', 'Non-renewable, biomass', 'Renewable, wind, solar, geothe', 'Renewable, biomass', 'Renewable, water', 'Total Energy' ]].sum()
results_bCLT_CO2_scaled_grouped = results_bCLT_CO2_scaled.groupby(['Process','Phase'])['CO2'].sum()
results_bTrad_CO2_scaled_grouped = results_bTrad_CO2_scaled.groupby(['Process','Phase'])['CO2'].sum()


writer = pd.ExcelWriter('.../GitHub/CLT-LCA-Tool/Results/CaseXX.xlsx', engine ='xlsxwriter')
results_bCLT_energy_scaled.to_excel(writer, sheet_name="CLT Energy")
results_bTrad_energy_scaled.to_excel(writer, sheet_name="Trad Energy")
results_bCLT_CO2_scaled.to_excel(writer, sheet_name="CLT CO2")
results_bTrad_CO2_scaled.to_excel(writer, sheet_name="Trad CO2")
results_bCLT_energy_scaled_grouped.to_excel(writer, sheet_name="CLT Energy Grouped")
results_bTrad_energy_scaled_grouped.to_excel(writer, sheet_name="Trad Energy Grouped")
results_bCLT_CO2_scaled_grouped.to_excel(writer, sheet_name="CLT CO2 Grouped")
results_bTrad_CO2_scaled_grouped.to_excel(writer, sheet_name="Trad CO2 Grouped")

writer.save()
#writer.close()


####plot bar graph 1: CLT building: Energy consumption by Phase and energy type
CLT_energy_grouped_by_phase_with_total = results_bCLT_energy_scaled.groupby(["Phase"]).sum()
CLT_energy_grouped_by_phase = CLT_energy_grouped_by_phase_with_total.drop(["Total Energy"], axis = 1)
CLT_energy_grouped_by_phase_t_for_graph = CLT_energy_grouped_by_phase.transpose()

CLT_energy_grouped_by_phase_t_for_graph.plot(kind = "bar", stacked= True)
plt.ylabel('Primary Energy Consumption per floor area in MJ')
plt.title('Phase-wise life-cycle impacts energy consumption for the CLT building')
plt.legend()

####plot bar graph 2: CLT building: Normalized energy consumption by Phase and energy type
CLT_energy_grouped_by_phase_scaled = CLT_energy_grouped_by_phase.apply(lambda x: x*100/x.sum())
CLT_energy_grouped_by_phase_scaled_t_for_graph = CLT_energy_grouped_by_phase_scaled.transpose()

CLT_energy_grouped_by_phase_scaled_t_for_graph.plot(kind = "bar", stacked= True)
plt.ylabel('% Primary Energy Consumption')
plt.title('Normalized Phase-wise life-cycle impacts for the CLT building')
plt.legend()

####plot bar graph 1 RC building: Normalized energy consumption by Phase and energy type
Trad_energy_grouped_by_phase_with_total = results_bTrad_energy_scaled.groupby(["Phase"]).sum()
Trad_energy_grouped_by_phase = Trad_energy_grouped_by_phase_with_total.drop(["Total Energy"], axis = 1)
Trad_energy_grouped_by_phase_t_for_graph = Trad_energy_grouped_by_phase.transpose()

Trad_energy_grouped_by_phase_t_for_graph.plot(kind = "bar", stacked= True)
plt.ylabel('Primary Energy Consumption per floor area in MJ')
plt.title('Phase-wise life-cycle energy consumption for the traditional building')
plt.legend()

####plot bar graph 1 RC building: Normalized energy consumption by Phase and energy type
Trad_energy_grouped_by_phase_scaled = Trad_energy_grouped_by_phase.apply(lambda x: x*100/x.sum())
Trad_energy_grouped_by_phase_scaled_t_for_graph = Trad_energy_grouped_by_phase_scaled.transpose()

Trad_energy_grouped_by_phase_scaled_t_for_graph.plot(kind = "bar", stacked= True)
plt.ylabel('Primary Energy Consumption per floor area in MJ')
plt.title('Normalized Phase-wise life-cycle energy consumption for the traditional building')
plt.legend()

####plot bar graph 3 CLT+Trad building: Total energy consumption by phase
CLT_energy_grouped_by_phase_with_total[["Total Energy"]].transpose().plot(kind = "bar", stacked= True)
comparative_total_energy_grouped_by_phase = CLT_energy_grouped_by_phase_with_total[["Total Energy"]]
comparative_total_energy_grouped_by_phase.rename(columns = {"Total Energy": "CLT Total Energy"})
comparative_total_energy_grouped_by_phase["RC Total Energy"] = Trad_energy_grouped_by_phase_with_total["Total Energy"]
comparative_total_energy_grouped_by_phase = comparative_total_energy_grouped_by_phase.transpose()
comparative_total_energy_grouped_by_phase.plot(kind = "bar", stacked = True)
plt.ylabel('Total Primary Energy Consumption per floor area in MJ')
plt.title('Phase-wise life-cycle total energy consumption for the CLT and RC buildings')
plt.legend()

####plot bar graph 3 CLT+Trad building: Total energy consumption by phase
comparative_fossil_total_energy_grouped_by_CLT_transport_other = pd.DataFrame(columns= ["Total Energy", "Non renewable, fossil"],index=["Tranportation of sawn lumber and CLT panels", "Other"])
ctea2a4 = results_bCLT_energy_scaled[["Total Energy"]].where((results_bCLT_energy_scaled["Material"] == "CLT") & ((results_bCLT_energy_scaled["Phase"] == "A2")|(results_bCLT_energy_scaled["Phase"] == "A4"))).sum().item()
cte = results_bCLT_energy_scaled[["Total Energy"]].sum().item()
ctfea2a4 = results_bCLT_energy_scaled[["Non renewable, fossil"]].where((results_bCLT_energy_scaled["Material"] == "CLT") & ((results_bCLT_energy_scaled["Phase"] == "A2")|(results_bCLT_energy_scaled["Phase"] == "A4"))).sum().item()
ctfe = results_bCLT_energy_scaled[["Non renewable, fossil"]].sum().item()
comparative_fossil_total_energy_grouped_by_CLT_transport_other.loc["Tranportation of sawn lumber and CLT panels"]["Total Energy"] = ctea2a4
comparative_fossil_total_energy_grouped_by_CLT_transport_other.loc["Tranportation of sawn lumber and CLT panels"]["Non renewable, fossil"] = ctfea2a4
comparative_fossil_total_energy_grouped_by_CLT_transport_other.loc["Other"]["Total Energy"] = cte - ctea2a4
comparative_fossil_total_energy_grouped_by_CLT_transport_other.loc["Other"]["Non renewable, fossil"] = ctfe - ctfea2a4
#print(comparative_fossil_total_energy_grouped_by_CLT_transport_other)
comparative_fossil_total_energy_grouped_by_CLT_transport_other.transpose().plot(kind = "bar", stacked = True)
plt.ylabel('Total Primary Energy Consumption per floor area in MJ')
plt.title('Share of transportation of sawn lumber and CLT panels in the total primary energy consumption of the CLT building for life-cycle phases A1--A5')
plt.legend()

plt.show()