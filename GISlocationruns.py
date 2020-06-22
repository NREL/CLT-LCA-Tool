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

############################################
apikey_text = get_GM_API_Key()
gmaps.configure(api_key=apikey_text)
###########################################

lat1 = 45.639

long1 = -122.624

cord1 = str(lat1) +', '+ str(long1)
#print(cord1)
latseattle = 48.0966
longseattle = -124.683

cordseattle = str(latseattle) +', '+ str(longseattle)

distance_1_seattle = calculate_distance(cord1, cordseattle, apikey_text)
print(distance_1_seattle)



