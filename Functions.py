# import all required packages and functions
import googlemaps
import gmaps
import gmaps.datasets
import json
import requests
import pandas as pd
import math as math
import numpy
######function to get the Google Maps API Key from the text file
def get_GM_API_Key():
    with open('C:/Users/SATNOORK/Desktop/CLT Literature/apikey.txt') as f:
        apikey = f.readline()
        f.close
    return apikey
##################################################################################
##calculates and returns the driving distance between two points in kms
def calculate_distance(Origin, Destination, apikey):
    params = {
        'key': apikey,
        'origins': Origin,
        'destinations': Destination}
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    response = requests.get(url, params)

    ###suppress unnecessary output33
    #print(response.status_code == 200)
    #print(response.text)
    result = json.loads(response.text)
    #return(result)
    try: a = result['rows'][0]['elements'][0]['distance']['value'] / 1000  #distance in km
    except: a = float('NaN')
    return (a)

###################################################################################
###processes the dataframe from the spreadsheet
def lumber_species_properties_processing (Wastepercentage ,Lumber_species_properties) :

    ##read in the inputs
    Waste_or_coproducts_percentage = Wastepercentage
    Lumber_species_properties = Lumber_species_properties

    ##final denisty of the lumber used in CLT is for 12% moisture
    ##calculate the weight of 1 m3 CLT
    Lumber_species_properties['Final Product Weight (odkg/m3 CLT)'] = Lumber_species_properties['Specific Gravity : 12%'] * 1000

    ###calcualte how much lumber per m3 CLT goes into waste products
    Lumber_species_properties['Co Products Weight (odkg/m3 CLT)'] = Lumber_species_properties['Final Product Weight (odkg/m3 CLT)'] * Waste_or_coproducts_percentage / (100-Waste_or_coproducts_percentage)

    ###calculate total lumber weight required per m3 CLT
    Lumber_species_properties['Total Wood Weight (odkg/m3 CLT)'] = Lumber_species_properties['Final Product Weight (odkg/m3 CLT)'] + Lumber_species_properties['Co Products Weight (odkg/m3 CLT)']

    ###total m3 12% lumber required for 1m3 CLT panel production
    Lumber_species_properties['Total 12% Wood Vol Req (m3/m3 CLT)'] = Lumber_species_properties['Total Wood Weight (odkg/ m3 CLT)'] / Lumber_species_properties['Specific Gravity : 12%'] / 1000

    ###total m3 green lumber required for 1m3 CLT panel production
    Lumber_species_properties['Total Green Wood Vol Req (m3/m3 CLT)'] = Lumber_species_properties['Total Wood Weight (odkg/ m3 CLT)'] / Lumber_species_properties['Specific Gravity : Green'] / 1000

    return(Lumber_species_properties)
###################################################################################
###finds the feasible set of resources which can be used and returns the impacts of this lumber production
def calculate_lumber_impact(CLT_required,Filtered_GIS_Data, timber_type, CLT_Mill_location, State_Region_Key,Lumber_production_impact):
    Filtered_GIS_Data['Abs Distance Estimate'] = float(0)
    # this loop calculates the absolute distance factor between mill location and location of the resource based on coordinates
    for index, row in Filtered_GIS_Data.iterrows():
        if row['ForestType'] == timber_type:
            Filtered_GIS_Data['Abs Distance Estimate'][index] = math.sqrt(float((CLT_Mill_location[0] - row['G1000_latdd']) ** 2 + (CLT_Mill_location[1] - row['G1000_longdd']) ** 2))

    non_zero_distances = numpy.array(Filtered_GIS_Data['Abs Distance Estimate'])
    non_zero_distances = numpy.delete(non_zero_distances, numpy.argwhere(non_zero_distances == 0))
    tenth_percentile_value = numpy.percentile(non_zero_distances, 10)
    Calculation_matrix = Filtered_GIS_Data
    Calculation_matrix['Region'] = ''
    ##this loop eliminates null values and resource rows with abs distance factor not in the bottom 10% values
    for index, row in Filtered_GIS_Data.iterrows():
        if (row['Abs Distance Estimate'] >= tenth_percentile_value) or (row['Abs Distance Estimate'] == 0):
            Calculation_matrix.drop([index], inplace=True)

    ##this loop gives the region of the resource based on which state it is located in
    for index, row in State_Region_Key.iterrows():
        state = row['State']
        index_list_matrix = Calculation_matrix[Calculation_matrix['State'] == state].index.to_list()
        Calculation_matrix['Region'][index_list_matrix] = row['Region']

    Calculation_matrix_2 = pd.DataFrame(columns=Calculation_matrix.columns)
    timber_req_satisfied = float(0)
    count = 1

    while timber_req_satisfied < CLT_required:
        min_dist_index = Calculation_matrix.index[
            Calculation_matrix['Abs Distance Estimate'] == Calculation_matrix['Abs Distance Estimate'].min()]
        timber_req_satisfied += float(Calculation_matrix['m3 Timber available'][min_dist_index])
        Calculation_matrix_2 = Calculation_matrix_2.append(Calculation_matrix.loc[min_dist_index])
        Calculation_matrix.drop(min_dist_index, inplace=True)
        count += 1

    Calculation_matrix_2['Region Lumber Impact per m3'] = ''
    Calculation_matrix_2['Region Lumber Impact'] = ''

    for index, row in Calculation_matrix_2.iterrows():
        index1 = Lumber_production_impact.index[Lumber_production_impact['Region'] == row['Region']]
        Calculation_matrix_2['Region Lumber Impact per m3'][index] = Lumber_production_impact['Sawn lumber, softwood, planed, kiln dried, at planer, NE-NC/m3/RNA'][index1]

    total_lumber_impact = Calculation_matrix_2['Region Lumber Impact per m3'].multiply(
        Calculation_matrix_2['m3 Timber available']).sum()

    return (total_lumber_impact, Calculation_matrix_2)#

#############################################################################################################