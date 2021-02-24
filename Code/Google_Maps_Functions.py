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

def get_GM_API_Key():
    with open('C:/Users/SATNOORK/Desktop/CLT Literature/apikey.txt') as f:
        apikey = f.readline()
        f.close
    return apikey

def calculate_distance(Origin, Destination, apikey):
    params = {
        'key': apikey,
        'origins': Origin,
        'destinations': Destination}
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    response = requests.get(url, params, verify=False)

    ###suppress unnecessary output33
    #print(response.status_code == 200)
    #print(response.text)
    result = json.loads(response.text)
    #return(result)
    try: a = result['rows'][0]['elements'][0]['distance']['value'] / 1000  #distance in km
    except: a = float('NaN')
    return (a)