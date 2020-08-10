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

# from itertools import tee ##this line may not be needed

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
Lumber_production_impact_co2 = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Lumber Production- CO2', nrows = 4)
###this sheet has inventory of manufacturing CLT###                                                                                             ####complete this process####
CLT_manufacturing_inventory = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='CLT Manufacturing Inventory',nrows=11)

###this sheet has impact values for electricity production in US states
Electricity_impact_energy = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Electricity by state- Energy', nrows=53)
Electricity_impact_CO2 = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Electricity by state- CO2', nrows=53)

###read in weight volume properties of timber
#in future, use this file for calculation using the waste percentage and delete the directly read in file.
#Lumber_species_properties = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/CLT_ Timber_types.xlsx', sheet_name='ALSC PS 20 Lumber Species', skiprows=[0])
lumber_species_properties_processed = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/CLT_ Timber_types.xlsx', sheet_name='ALSC PS 20 Lumber Species', skiprows=[0])

#GIS_Data_with_sawmills = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy2.xlsx")

CLT_Manufacturing_energy_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='CLT Manufacturing- Energy')

CLT_Manufacturing_CO2_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='CLT Manufacturing- CO2')

transportation_energy_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Transportation- Energy')

transportation_CO2_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Transportation- CO2')

transportation_CO2_impact_factors = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Transportation- CO2')

material_transport_distances = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Material Transport')

construction_fuels_CLT_building = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingMaterialsDistanceSheet.xlsx", sheet_name='CLT Construction')

construction_impacts_CLT_building = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Construction- Energy')

construction_impacts_CLT_building_CO2 = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Construction- CO2')

building_material_impacts = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Material Impacts- Energy')

building_material_impacts_co2 = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Material Impacts- CO2')

####################################################################################################

###derived variables###
CLT_Region = state_region_map.loc[state_region_map.State == CLT_Sourcing_state, 'Region'].item()

#CLTM_to_Building_Distance = calculate_distance(CLT_Mill_location1, building_location1, apikey_text)            ###update later
CLTM_to_Building_Distance = 700

CLT_density_SM_CLTM = lumber_species_properties_processed.loc[lumber_species_properties_processed["ALSC PS 20 Commercial Species"] == timber_type, 'Weight (kg/m3) : 12%'].item()

####################################################################################################

###Katerra = building choice 1 ###

if building_choice == 1:

    ###read in the materials inventory for the CLT building
    ###this sheet has basic building data : name, area, location, no of storeys, etc. ###
    building_inventories_info_CLT_building = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Building-Katerra', usecols='A:B', nrows=6, header=None)

    ###this sheet has the bill of materials###
    building_inventories_table_CLT_building = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Building-Katerra', skiprows=7,nrows=47)

    ###read in the sq ft
    sq_ft_CLT_building = building_inventories_info_CLT_building.iloc[4][1]

    ###calculate total CLT required for the building
    CLT_required = building_inventories_table_CLT_building.loc[building_inventories_table_CLT_building.Material == "CLT", 'Normalized_Quantity'].sum()

################################################################################################################

###create results dataframes ###

energy_impacts_CLT = pd.DataFrame(columns=["Phase", "Renewable, wind, solar, geothe", "Renewable, biomass", "Non renewable, fossil", "Non-renewable, nuclear", "Renewable, water", "Non-renewable, biomass"])
phases_1 = ["Lumber Production", "Transport to CLT Mill", "CLT Manufacturing", "Transport to building site"]
energy_impacts_CLT["Phase"] = phases_1

energy_impacts_CLT_building = pd.DataFrame(columns=["Phase", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ])
phases_2 = ["A1-A3", "A4", "A5"]
energy_impacts_CLT_building["Phase"] = phases_2

################################################################################################################

###Lumber production impact###

waste_percentage = 16

#for now, this file has been directly read in through Excel. In further iteration, make this a variable by using the waste_percentage.

#lumber_species_properties_processed = lumber_species_properties_processing(waste_percentage, Lumber_species_properties)

###add values for lumber transport and processing

lumber_required = CLT_required * lumber_species_properties_processed.loc[lumber_species_properties_processed["ALSC PS 20 Commercial Species"] == timber_type, 'Total 12% Wood Vol Req (m3/m3 CLT)'].item()

###############################################################################################################

# energy_impacts_CLT[4][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact.Region == CLT_Region, "Renewable, wind, solar, geothe"].item()
# energy_impacts_CLT[5][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact.Region == CLT_Region, "Renewable, biomass"].item()
# energy_impacts_CLT[1][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact.Region == CLT_Region, "Non renewable, fossil"].item()
# energy_impacts_CLT[2][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact.Region == CLT_Region, "Non-renewable, nuclear"].item()
# energy_impacts_CLT[6][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact.Region == CLT_Region, "Renewable, water"].item()
# energy_impacts_CLT[3][1] = lumber_required * Lumber_production_impact.loc[Lumber_production_impact.Region == CLT_Region, "Non-renewable, biomass"].item()

#####################add to maine results matrix

a = "Lumber Production"
b = "A1-A3"
c = "CLT"
d = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Non renewable, fossil"].item()
e = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Non-renewable, nuclear"].item()
f = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Non-renewable, biomass"].item()
g = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Renewable, wind, solar, geothe"].item()
h = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Renewable, biomass"].item()
i = lumber_required * Lumber_production_impact.loc[Lumber_production_impact["Region"] == CLT_Region, "Renewable, water"].item()

co2 = lumber_required * Lumber_production_impact_co2.loc[Lumber_production_impact_co2["Region"] == CLT_Region, "Impact: CO2 emissions"].item()
##create main results matrix
results_bCLT_energy = pd.DataFrame([[a,b,c,d,e,f,g,h,i]],columns=["Process", "Phase" , "Material", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ])
results_bCLT_CO2 = pd.DataFrame([[a,b,c,co2]],columns=["Process", "Phase" , "Material", "CO2"])
################################################################################################################

###Lumber transportation impact###

####get dataframe file of GIS Data with appended sawmills and distances (file has been read in at the beginning of the code for now, change to read according to the state later

###this loop is not needed maybe####################
# GIS_Data_with_sawmills['Distance_SM_CLTM'] = ''
# distance_forest_sawmill = 0
# no_of_calc_forest_sawmill = 0
# for index, row in GIS_Data_with_sawmills.iterrows():
#     if row["ForestType"] == timber_type:
#         distance_forest_sawmill = distance_forest_sawmill + sum(row["Distance"])
#         no_of_calc_forest_sawmill = no_of_calc_forest_sawmill + len(row["Distance"])
#
# avg_distance_forest_sawmill = distance_forest_sawmill/no_of_calc_forest_sawmill


###get from MappintSMtoCLTM function: avg_sawmill_CLT_mill_distance

############Lumber transport to CLT Mill  ###############assume 12% density#################****************
a = "Lumber Transport SM_CLT"
b = "A1-A3"
c = "CLT"
avg_sawmill_CLT_mill_distance = 2000
avg_distance_forest_sawmill = 100 ##join code for real values
if avg_distance_forest_sawmill <= 200:   ###update the number

    ###check###

    d = avg_distance_forest_sawmill *CLT_required *CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Non renewable, fossil"].item()
    e = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Non-renewable, nuclear"].item()
    f = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Non-renewable, biomass"].item()
    g = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Renewable, wind, solar, geothe"].item()
    h = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Renewable, biomass"].item()
    i = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Renewable, water"].item()
    co2 = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_CO2_impact_factors.loc[
        transportation_CO2_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Impact: CO2 emissions"].item()

if avg_distance_forest_sawmill > 200:

    ###check###
    d = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Non renewable, fossil"].item()
    e = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Non-renewable, nuclear"].item()
    f = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Non-renewable, biomass"].item()
    g = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Renewable, wind, solar, geothe"].item()
    h = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Renewable, biomass"].item()
    i = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Renewable, water"].item()
    co2 = avg_distance_forest_sawmill *CLT_required * CLT_density_SM_CLTM * transportation_CO2_impact_factors.loc[
        transportation_CO2_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Impact: CO2 emissions"].item()

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a,b,c,d,e,f,g,h,i]],columns=["Process", "Phase" , "Material", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ]))
results_bCLT_CO2 = results_bCLT_energy.append(pd.DataFrame([[a,b,c,co2]],columns=["Process", "Phase" , "Material", "CO2" ]))

######CLT transport to building site########  ###############assume 12% density#################****************
a = "Lumber Transport CLT_SM"
b = "A4"
c = "CLT"

if CLTM_to_Building_Distance <= 322:   ###in km ##taken from USLCI process documentation ### how many tonnes???
    d = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Non renewable, fossil"].item()
    e = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Non-renewable, nuclear"].item()
    f = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Non-renewable, biomass"].item()
    g = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Renewable, wind, solar, geothe"].item()
    h = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Renewable, biomass"].item()
    i = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Renewable, water"].item()
    co2 = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_CO2_impact_factors.loc[
        transportation_CO2_impact_factors.Vehicle == "Combination Truck (Short-haul)", "Impact: CO2 emissions"].item()

if CLTM_to_Building_Distance > 322:
    d = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Non renewable, fossil"].item()
    e = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Non-renewable, nuclear"].item()
    f = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Non-renewable, biomass"].item()
    g = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Renewable, wind, solar, geothe"].item()
    h = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Renewable, biomass"].item()
    i = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_energy_impact_factors.loc[
        transportation_energy_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Renewable, water"].item()
    co2 = CLTM_to_Building_Distance *CLT_required * CLT_density_SM_CLTM * transportation_CO2_impact_factors.loc[
        transportation_CO2_impact_factors.Vehicle == "Combination Truck (Long-haul)", "Impact: CO2 emissions"].item()

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a,b,c,d,e,f,g,h,i]],columns=["Process", "Phase" , "Material", "Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ] ))
results_bCLT_CO2 = results_bCLT_energy.append(pd.DataFrame([[a,b,c,co2]],columns=["Process", "Phase" , "Material", "CO2" ]))
##################################################################################################

######CLT Manufacturing Impact#####

CLT_Mfc_Electricity = CLT_manufacturing_inventory.loc[CLT_manufacturing_inventory["Input"] == "Electricity"].sum()
#CLT_Mfc_Energy_Impacts = pd.DataFrame(columns = ["Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water"])
#CLT_Mfc_Energy_Impacts = pd.concat(CLT_manufacturing_inventory, CLT_Mfc_Energy_Impacts)

#row_no_used = len(results_bCLT_energy.index)

for index, row in CLT_manufacturing_inventory.iterrows():
    a = row["Process"]
    b = "A1-A3"
    c = row["Input"]
    if row["Input"] != "Electricity":
        d = row["Amount"] * CLT_Manufacturing_energy_impact_factors.loc[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"],"Non renewable, fossil"].item()
        e = row["Amount"] * CLT_Manufacturing_energy_impact_factors.loc[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"],"Non-renewable, nuclear"].item()
        f = row["Amount"] * CLT_Manufacturing_energy_impact_factors.loc[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"],"Non-renewable, biomass"].item()
        g = row["Amount"] * CLT_Manufacturing_energy_impact_factors.loc[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"],"Renewable, wind, solar, geothe"].item()
        h = row["Amount"] * CLT_Manufacturing_energy_impact_factors.loc[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"],"Renewable, biomass"].item()
        i = row["Amount"] * CLT_Manufacturing_energy_impact_factors.loc[CLT_Manufacturing_energy_impact_factors["Material"] == row["Input"],"Renewable, water"].item()
        co2 = row["Amount"] * CLT_Manufacturing_CO2_impact_factors.loc[CLT_Manufacturing_CO2_impact_factors["Material"] == row["Input"],"Impact: CO2 emissions"].item()

    if row["Input"] == "Electricity":
        d = row["Amount"] * Electricity_impact_energy.loc[Electricity_impact_energy["State"] == CLT_Sourcing_state,"Non renewable, fossil"].item()
        e = row["Amount"] * Electricity_impact_energy.loc[Electricity_impact_energy["State"] == CLT_Sourcing_state,"Non-renewable, nuclear"].item()
        f = row["Amount"] * Electricity_impact_energy.loc[Electricity_impact_energy["State"] == CLT_Sourcing_state,"Non-renewable, biomass"].item()
        g = row["Amount"] * Electricity_impact_energy.loc[Electricity_impact_energy["State"] == CLT_Sourcing_state,"Renewable, wind, solar, geothe"].item()
        h = row["Amount"] * Electricity_impact_energy.loc[Electricity_impact_energy["State"] == CLT_Sourcing_state,"Renewable, biomass"].item()
        i = row["Amount"] * Electricity_impact_energy.loc[Electricity_impact_energy["State"] == CLT_Sourcing_state,"Renewable, water"].item()
        co2 = row["Amount"] * Electricity_impact_CO2.loc[Electricity_impact_CO2["State"] == CLT_Sourcing_state,"CO2 (kg CO2 eq/kWh)"].item()

    results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]], columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
    results_bCLT_CO2 = results_bCLT_energy.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))

################## CLT Building Materials Impacts#################

CLT_building_materials_energy_impacts = pd.DataFrame(columns = ["Non renewable, fossil","Non-renewable, nuclear","Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water"])

#CLT_building_materials_mfc_energy_impacts = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_energy_impacts)

##correct 20
for index, row in building_inventories_table_CLT_building.iterrows():

    a = row["LCA_Material_Name"]      ##+ production?
    b = 'A1-A3'
    if row["Material"] != "CLT":
        c = "Other"
        d = row['Normalized_Quantity'] * building_material_impacts.loc[building_material_impacts.Material == row['LCA_Material_Name'], "Non renewable, fossil"].item()
        e = row['Normalized_Quantity'] * building_material_impacts.loc[building_material_impacts.Material == row['LCA_Material_Name'], "Non-renewable, nuclear"].item()
        f = row['Normalized_Quantity'] * building_material_impacts.loc[building_material_impacts.Material == row['LCA_Material_Name'], "Non-renewable, biomass"].item()
        g = row['Normalized_Quantity'] * building_material_impacts.loc[building_material_impacts.Material == row['LCA_Material_Name'], "Renewable, wind, solar, geothe"].item()
        h = row['Normalized_Quantity'] * building_material_impacts.loc[building_material_impacts.Material == row['LCA_Material_Name'], "Renewable, biomass"].item()
        i = row['Normalized_Quantity'] * building_material_impacts.loc[building_material_impacts.Material == row['LCA_Material_Name'], "Renewable, water"].item()
        co2 = row['Normalized_Quantity'] * building_material_impacts_co2.loc[building_material_impacts_co2.Material == row['LCA_Material_Name'], "Impact: CO2 emissions"].item()

    #if row["Material"] == "CLT":
        ###delete this particular row

    results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]], columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
    results_bCLT_CO2 = results_bCLT_energy.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))
####add row for total of all

# = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_energy_impacts)

for index, row in building_inventories_table_CLT_building.iterrows():

    a = row["LCA_Material_Name"]
    b = 'A4'
    if row["LCA_Material_Name"] != "CLT":
        c = "Other"
        material_row_index = material_transport_distances.index[material_transport_distances["LCA_Material_Name"] == row["LCA_Material_Name"]]
        #### add impacts nos for road and rail
        d = (row['Normalized_Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])).item()
        e = (row['Normalized_Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])).item()
        f = (row['Normalized_Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])).item()
        g = (row['Normalized_Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])).item()
        h = (row['Normalized_Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])).item()
        i = (row['Normalized_Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])).item()
        co2 = (row['Normalized_Quantity'] * material_transport_distances["Factor"][material_row_index] * (material_transport_distances["Road"][material_row_index] + material_transport_distances["Rail"][material_row_index])).item()

    #if row["Material"] == "CLT":
        ###delete this particular row

    results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]], columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
    results_bCLT_CO2 = results_bCLT_energy.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))
####add row for total of all

##################################################################################################
#CLT_building_materials_mfc_energy_impacts = pd.concat(building_inventories_table_CLT_building, CLT_building_materials_mfc_energy_impacts)

##########################################
construction_fuels_CLT_building_1 = construction_fuels_CLT_building[["Fuel", "Amount"]]
##convert amount to L or kWh from L/sqm to kWh/sqm
construction_fuels_CLT_building_1["Amount"] = construction_fuels_CLT_building_1["Amount"] * sq_ft_CLT_building * 0.092903  ###factor converts sqm to sqft
construction_fuels_CLT_building_1["Hrs"] = ""
construction_fuels_CLT_building_1["Hrs"][0] = construction_fuels_CLT_building_1["Amount"][2]/15 ###assume 15L used per hr of machinery use
construction_fuels_CLT_building_1["Kms"] = ""
construction_fuels_CLT_building_1["Kms"][1] = construction_fuels_CLT_building_1["Amount"][2]/8 ###assume 8L used per km of transport in large vehicle
construction_fuels_CLT_building_1["Hrs"][2] = 0   ###put in values for electricity
##################################################################################################

# CLT_building_materials_const_energy_impacts = pd.DataFrame(columns = ["Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass", "Renewable, wind, solar, geothe", "Renewable, biomass",   "Renewable, water" ])
# CLT_building_materials_const_energy_impacts = pd.concat(construction_fuels_CLT_building_1, CLT_building_materials_const_energy_impacts)
#calculations for diesel
a = "Construction x"
b = "A5"
c = "NA"
d = construction_fuels_CLT_building_1["Hrs"][1] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Diesel", "Non renewable, fossil"].item()
e = construction_fuels_CLT_building_1["Hrs"][1] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Diesel", "Non-renewable, nuclear"].item()
f = construction_fuels_CLT_building_1["Hrs"][1] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Diesel", "Non-renewable, biomass"].item()
g = construction_fuels_CLT_building_1["Hrs"][1] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Diesel", "Renewable, wind, solar, geothe"].item()
h = construction_fuels_CLT_building_1["Hrs"][1] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Diesel", "Renewable, biomass"].item()
i = construction_fuels_CLT_building_1["Hrs"][1] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Diesel", "Renewable, water"].item()
co2 = construction_fuels_CLT_building_1["Hrs"][1] * construction_impacts_CLT_building_CO2.loc[construction_impacts_CLT_building_CO2.Process == "Diesel", "Impact: CO2 emissions"].item()

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bCLT_CO2 = results_bCLT_energy.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))
##################################################################################################
#calculations for gasoline
a = "Construction y"
b = "A5"
c = "NA"
d = construction_fuels_CLT_building_1["Kms"][0] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Gasoline", "Non renewable, fossil"].item()
e = construction_fuels_CLT_building_1["Kms"][0] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Gasoline", "Non-renewable, nuclear"].item()
f = construction_fuels_CLT_building_1["Kms"][0] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Gasoline", "Non-renewable, biomass"].item()
g = construction_fuels_CLT_building_1["Kms"][0] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Gasoline", "Renewable, wind, solar, geothe"].item()
h = construction_fuels_CLT_building_1["Kms"][0] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Gasoline", "Renewable, biomass"].item()
i = construction_fuels_CLT_building_1["Kms"][0] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Gasoline", "Renewable, water"].item()
co2 = construction_fuels_CLT_building_1["Kms"][0] * construction_impacts_CLT_building_CO2.loc[construction_impacts_CLT_building_CO2.Process == "Gasoline", "Impact: CO2 emissions"].item()

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bCLT_CO2 = results_bCLT_energy.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))
#calculations for electricity
a = "Construction z"
b = "A5"
c = "NA"
d = construction_fuels_CLT_building_1["Hrs"][2] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Electricity", "Non renewable, fossil"].item()
e = construction_fuels_CLT_building_1["Hrs"][2] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Electricity", "Non-renewable, nuclear"].item()
f = construction_fuels_CLT_building_1["Hrs"][2] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Electricity", "Non-renewable, biomass"].item()
g = construction_fuels_CLT_building_1["Hrs"][2] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Electricity", "Renewable, wind, solar, geothe"].item()
h = construction_fuels_CLT_building_1["Hrs"][2] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Electricity", "Renewable, biomass"].item()
i = construction_fuels_CLT_building_1["Hrs"][2] * construction_impacts_CLT_building.loc[construction_impacts_CLT_building.Process == "Electricity", "Renewable, water"].item()
co2 = construction_fuels_CLT_building_1["Hrs"][2] * construction_impacts_CLT_building_CO2.loc[construction_impacts_CLT_building.Process == "Electricity", "Impact: CO2 emissions" ].item()

results_bCLT_energy = results_bCLT_energy.append(pd.DataFrame([[a, b, c, d, e, f, g, h, i]],columns=["Process", "Phase", "Material", "Non renewable, fossil", "Non-renewable, nuclear", "Non-renewable, biomass","Renewable, wind, solar, geothe", "Renewable, biomass", "Renewable, water"]))
results_bCLT_CO2 = results_bCLT_energy.append(pd.DataFrame([[a, b, c, co2]], columns=["Process", "Phase", "Material", "CO2"]))