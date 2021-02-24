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

