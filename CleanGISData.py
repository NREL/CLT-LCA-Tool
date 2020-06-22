####This function takes GIS data from the original excel file and extracts only non-tribe data which has the acceptable softwood species


###import all required packages
import pandas as pd
GIS_Data = pd.DataFrame(pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISData - Copy.xlsx", sheet_name="Sheet1"))
GIS_Data_Key = pd.DataFrame(pd.read_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISData - Copy.xlsx", sheet_name="Sheet2"))
col_names = GIS_Data.columns
Filtered_GIS_Data = pd.DataFrame(columns=col_names)
Filtered_GIS_Data['Region'] = ""
index = 0
for ft in GIS_Data['ForestType']:
    if ((GIS_Data_Key['ALSC Species Name'].str.contains(ft)).any() & (GIS_Data['Owner'].iloc[[index]] != 'Tribe')).all() :
        Filtered_GIS_Data = Filtered_GIS_Data.append(GIS_Data.iloc[[index]])
    index = index + 1


Filtered_GIS_Data.to_excel("C:/Users/SATNOORK/Desktop/CLT Literature/SampleGISDataFiltered - Copy.xlsx")

