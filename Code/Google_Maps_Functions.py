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
    #enter your api key here
    with open('.../apikey.txt') as f:
        apikey = f.readline()
        f.close
    return apikey

def calculate_distance(Origin, Destination, apikey):
    params = {
        'key': apikey,
        'origins': Origin,
        'destinations': Destination,
        'mode': 'Driving'}
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

from math import radians, cos, sin, asin, sqrt


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


