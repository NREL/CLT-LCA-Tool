######################################################################################################
# import all required packages and functions
from Functions import get_GM_API_Key
from Functions import lumber_species_properties_processing
from Functions import calculate_lumber_impact
from Functions import calculate_distance
from Functions import calculate_energy_impacts
import googlemaps
import gmaps
import gmaps.datasets
import json
import requests
import pandas as pd
import xlsxwriter
import math as math
import numpy as np
#import matplotlib
import matplotlib.pyplot as plt

# from itertools import tee ##this line may not be needed