######################################################################################################
# import all required packages and functions
from Functions import get_GM_API_Key
from Functions import lumberspeciespropoertiesprocessing
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

######################################################################################################
###import api_key from text file and configure the key
apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)
######################################################################################################

###temporary input panel to get input from the user

# location = input("Enter the location of the building")


# timber_type = input("Enter the desired timber type to be used in the CLT panel")

# building_choice = input("Enter the option number of the building from the descriptions")
building_choice = 1
###assume Katerra CLT building for now


###below inputs not needed for now as building inventory is directly taken as a case study from Katerra
# square_footage = float(input("Enter the total square footage of the building"))
##square_footage = float(5000)

# no_of_floors = int(input("Enter the number of floors in the building"))
###no_of_floors = 8


#######################################################################################################
####function to get cooridantes of a place
# Import required library
# loc = input("Enter place: ")
# def get_coordinates(location, apikey=apikey_text):
#     place = location
#     #Place your google map API_KEY to a variable
#     #Store google geocoding api url in a variable
#     url = 'https://maps.googleapis.com/maps/api/geocode/json?'
#     # call get method of request module and store respose object
#     CO = requests.get(url + 'address =' + place + '&key =' + apikey)
#     #Get json format result from the above response object
#     coordinates = CO.json()
#     #print the value of res
#     return coordinates

#######################################################################################################
###get coordinates of SF
# building_location_coordinates = get_coordinates(loc)
# print(building_location_coordinates)
#######################################################################################################

###function to estimate the amount of materials needed
###return list of amounts

###temporary list to use
material_amounts_data = [['Concrete', 1], ['Timber', 2], ['Material 1', 3], ['Material 2', 4], ['Material 3', 5]]
material_amounts = pd.DataFrame(material_amounts_data, columns=['Material', 'Amounts'])
#######################################################################################################
###Excel file inputs
###import input output analysis file
input_output_energy = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/Input_Output_File.xlsx")
Lumber_species_properties = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/CLT_ Timber_types.xlsx',
                                          sheet_name='ALSC PS 20 Lumber Species', skiprows=[0])
###Read excel file for lumber properties and GIS timber key
Lumber_species_Data_key = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/CLT_ Timber_types.xlsx',
                                        sheet_name='GIS Data Key')
Lumber_production_impact = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx',
                                         sheet_name='Lumber Production')
CLT_mfc_impact = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx',
                               sheet_name='CLT Manufacturing')
CLT_trans_impact = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx',
                               sheet_name='Transportation')
Filtered_GIS_Data = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy.xlsx")

Sawmills_data_Washington = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/mill2005w.xlsx",sheet_name='Washington')
pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/mill2005w.xlsx",sheet_name='Washington')
GIS_Data_Key = pd.DataFrame(
    pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISData - Copy.xlsx", sheet_name="Sheet2"))
State_Region_Key = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Sheet1')
Transport_impact_factor = pd.read_excel('C:/Users/SATNOORK/Desktop/CLT Literature/LCA_Impact_Values.xlsx', sheet_name='Transportation')
#######################################################################################################
###form a results dataframe
Output = pd.DataFrame(input_output_energy["Input"])

Output["Energy Input"] = material_amounts["Amounts"] * input_output_energy["Energy Input"]

########################################################################################################

# Waste_or_coproducts_percentage = float(input("Enter the % in weight of wood which goes into co-products in the CLT manufacturing process"))

##default value for now based on the Katerra paper

##process Lumber Species Properties

##########################################################################################################

Lumber_species_properties = lumberspeciespropoertiesprocessing(16, Lumber_species_properties)

##########################################################################################################
###calculate lumber production impacts for different tree species per m3 of CLT

Lumber_production_impact_by_species = Lumber_species_properties['Total Green Wood Vol Req (odkg/m3)'] * \
                                      Lumber_production_impact[
                                          'Sawn lumber, softwood, planed, kiln dried, at planer, NE-NC/m3/RNA']

# Denver = '39.7392, -104.9903'
building_location = [39.7392, -104.9903]
building_location1 = '39.7392, -104.9903'
timber_type = 'Douglas-fir'
timber_type_code = 29  ##write code to lookup the code
# CLT_Mill_location = '42.8621, -112.4506'
CLT_Mill_location =[42.8621, -112.4506]  ### in Idaho
CLT_Mill_location1 ='42.8621, -112.4506'
timber_source_state = 'Washington'
##########################################################################################################
##calculate total lumber prodution impact
total_l_i, matrix_new = calculate_lumber_impact(CLT_required,Filtered_GIS_Data, timber_type, CLT_Mill_location, State_Region_Key,Lumber_production_impact)

CLT_mfc_impact["Total Impact"] = CLT_required * CLT_mfc_impact['Impact (kg CO2 eq/m3)']

#calculate total manufacturing impact
total_mfc_impact = CLT_mfc_impact["Total Impact"].sum()

# calculate transportation impact from mill to building

##calculate distance between the CLT mill and the building location
distance_CLTMill_BuildingLoc = calculate_distance(CLT_Mill_location1, building_location1, apikey_text)

###calculate weight of CLT transported from the mill to the building location
total_weight_CLT = CLT_required * Lumber_species_properties['Weight (kg/m3) : 12%'][Lumber_species_properties.index[Lumber_species_properties['Forest Type Code'] == timber_type_code]]
total_tonne_km = total_weight_CLT * distance_CLTMill_BuildingLoc
total_trans_impact = total_tonne_km * float(CLT_trans_impact['Emissions per tonne-km'])
total_CO2_impact = total_mfc_impact + total_trans_impact

#function to get the building inventory
##building_choice is 1 for the Katerra building
if building_choice == 1:
    ###read in the materials inventory for the CLT building
    building_inventories_info = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Building-Katerra', usecols='A:B', nrows=6, header=None)
    building_inventories_table = pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/BuildingConfigurations.xlsx", sheet_name='Building-Katerra', skiprows=7)
    ###read in the multiplier
    sq_ft_ratio = building_inventories_info.iloc[4][6]

    ###calculate total CLT required for the building
    CLT_required = building_inventories_table['Normalized Quantity'][building_inventories_table.index[building_inventories_table['Material'] == 'CLT']].sum()*sq_ft_ratio


    ###push back this idea for now; this detail can ba added later
    ####sq_ft_per_floor_ratio = float(square_footage/no_of_floors/building_inventories_info.iloc[4][1]*building_inventories_info.iloc[5][1])
    ##depend_on_square_footage = ['Beams and columns', 'Columns', 'Connections', 'Girders', 'Fireproofing paint', 'BRBs', 'Shear walls', 'Exterior glazing', 'Exterior mullions', 'Insulation', 'Exterior wall', 'Air barrier', 'Insulated panel', 'Hat channels', 'Finish', 'Roof CLT', 'Underlayment membrane', 'Insulation build-up', 'Adhesive', 'Rigid board', 'Waterproofing', 'Insulation']
    ##depend_on_sq_ft_per_floor = ['Slab', 'Topping slab', 'Acoustic underlayment', 'Column footings', 'Mat foundation', 'Slab-on-grade', 'Slab-on-grade underlayment', 'Subgrade columns', 'Subgrade walls and footings', 'Suspended slabs', 'Carrier rails']

    ##building_inventories_table['Actual Energy Impact'] = ''
    ##building_inventories_table['Actual CO2 Impact'] = ''

    ###code debugger: ignore
    ###print('a')
    ##################

    ####for index, row in building_inventories_table.iterrows():
        ###code debugger: ignore
        ###print('b')
        ############

        # if row['Item'] in depend_on_square_footage:
        #     building_inventories_table['Actual Energy Impact'][index] = building_inventories_table['Impact: Energy'][index]*sq_ft_ratio
        #     building_inventories_table['Actual CO2 Impact'][index] = building_inventories_table['Impact: CO2'][
        #                                                                     index] * sq_ft_ratio
        #     print('c')
        # if row['Item'] in depend_on_sq_ft_per_floor:
        #     building_inventories_table['Actual Energy Impact'][index] = building_inventories_table['Impact: Energy'][
        #                                                                     index] * sq_ft_per_floor_ratio
        #     building_inventories_table['Actual CO2 Impact'][index] = building_inventories_table['Impact: CO2'][
        #                                                                     index] * sq_ft_per_floor_ratio
        #     print('d')
    # Energy_impact_except_CLT = building_inventories_table['Actual Energy Impact'].sum()
    # CO2_impact_except_CLT = building_inventories_table['Actual CO2 Impact'].sum()

    ##now find the total impact due to materials other than CLT
    ##these are stored in the


###function to ......
##### if the forest cell is selected, calculate the distances based on the sawmills in the dictionary
# for row, index in Filtered_GIS_Data.iterrows():
#     if (row['ForestType'] == timber_type) and (row['State'] == timber_source_state):

###assign sawmills for each figure id
for index, row in Filtered_GIS_Data.iterrows():
    list_sawmills = list()
    cell_loc = str(row['G1000_latdd']) + ', ' + str(row['G1000_longdd'])
    for index1, row1 in Sawmills_data_Washington.iterrows():
        sawmill_loc = str(row1['LAT']) + ', ' + str(row1['LON'])
        distance_cell_sawmill = calculate_distance(cell_loc, sawmill_loc, apikey_text)
        if distance_cell_sawmill <=150:
            list_sawmills.append(row1['MILL2005_1'])
    row['Sawmills'] = list_sawmills



###def findmills (x,y,z):

