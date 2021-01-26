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

