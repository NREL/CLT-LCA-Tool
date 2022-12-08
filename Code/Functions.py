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

def calc_timber_species_properties(timber_species_properties,waste_percentage):
    timber_species_properties["Final Product Weight (odkg/m3 CLT)"] = timber_species_properties["Specific Gravity : 12%"]*1000
    timber_species_properties["Co Products Weight (odkg/m3 CLT)"] = timber_species_properties["Final Product Weight (odkg/m3 CLT)"]*waste_percentage/(100-waste_percentage)
    timber_species_properties["Total Wood Weight (odkg/m3 CLT)"] = timber_species_properties["Final Product Weight (odkg/m3 CLT)"] + timber_species_properties["Co Products Weight (odkg/m3 CLT)"]
    timber_species_properties["Total 12% Wood Vol Req (m3/m3 CLT)"] = timber_species_properties["Total Wood Weight (odkg/m3 CLT)"]/timber_species_properties["Specific Gravity : 12%"]/1000
    timber_species_properties["Total Green Wood Vol Req (m3/m3 CLT)"] = timber_species_properties["Total Wood Weight (odkg/m3 CLT)"]/timber_species_properties["Specific Gravity : Green"]/1000
    return timber_species_properties

def calculate_energy_impacts(input_variable, input_sheet, lookup_column, lookup_variable):
    d = input_variable * input_sheet.loc[input_sheet[lookup_column] == lookup_variable, "Non renewable, fossil"].item()
    e = input_variable * input_sheet.loc[input_sheet[lookup_column] == lookup_variable, "Non-renewable, nuclear"].item()
    f = input_variable * input_sheet.loc[input_sheet[lookup_column] == lookup_variable, "Non-renewable, biomass"].item()
    g = input_variable * input_sheet.loc[input_sheet[lookup_column] == lookup_variable, "Renewable, wind, solar, geothe"].item()
    h = input_variable * input_sheet.loc[input_sheet[lookup_column] == lookup_variable, "Renewable, biomass"].item()
    i = input_variable * input_sheet.loc[input_sheet[lookup_column] == lookup_variable, "Renewable, water"].item()

    return(d,e,f,g,h,i)

def calculate_sawmill_CLT_mill_distance(species, mill_state, CLT_mill_lat, CLT_mill_long, apikey):
    from Google_Maps_Functions import get_GM_API_Key
    from Google_Maps_Functions import calculate_distance
    sawmills_by_species_processed_data  = pd.read_excel('.../CLT-LCA-Tool/Mill Datasets/state_timber_sawmill_dataset_' + mill_state + '.xlsx')
    sawmills_filtered_by_species = sawmills_by_species_processed_data[sawmills_by_species_processed_data["Timber_Type"] == species]
    sawmills_filtered_by_species["Dist_i"] = 0
    for index, row in sawmills_filtered_by_species.iterrows():
        saw_mill_coordinates = str(row['LAT']) + ', ' + str(row['LON'])
        #mill_lat = row['LAT']
        #mill_long = row['LON']
        #print(row["Mill_ID_U"])
        clt_mill_coordinates = str(CLT_mill_lat) + ', ' + str(CLT_mill_long)
        sawmill_clt_dist_i = calculate_distance(saw_mill_coordinates, clt_mill_coordinates, apikey)
        sawmills_filtered_by_species.iloc[index]["Dist_i"] = sawmill_clt_dist_i

    avg_dist_sawmill_CLT_mill = sawmills_filtered_by_species["Dist_i"].mean()