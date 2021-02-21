# import libraries
import requests
import json
import numpy as np
import pandas as pd

# DataFrame Column Processing Function Inventory: Functions to be mapped to respective columns.
def float_maker(num):
    return float(num)

def na_fixer(num):
    if num == 'Not Available':
        return 0.0
    else:
        return float(num)
    
def spell_fix(name):
    name = str(name)
    if 'Huntingtn' in name:
        name = 'Huntington'
        return name
    else:
        return name
    
def suffix_maker(name):
    if 'Avenue' in name:
        name = name.replace('Avenue','AVE')
        return name
    elif 'St.' in name:
        name = name.replace('St.','ST')
        return name
    elif 'Ave.' in name:
        name = name.replace('Ave.','AVE')
        return name
    elif 'Ave' in name:
        name = name.replace('Ave','AVE')
        return name
    elif 'Road' in name:
        name = name.replace('Road','RD')
        return name
    elif 'Street' in name:
        name = name.replace('Street','ST')
        return name
    elif 'Square' in name:
        name = name.replace('Square','SQ')
        return name
    elif 'Place' in name:
        name = name.replace('Place','PL')
        return name
    elif 'Highway' in name:
        name = name.replace('Highway','HW')
        return name
    elif 'Parkway' in name:
        name = name.replace('Parkway','PW')
        return name
    else:
        return name
    
def char_remove(name):
    if '.' in name:
        name = name.replace('.','')
        return name
    elif '(' in name:
        name = name.replace('(','')
        return name
    elif ')' in name:
        name = name.replace(')','')
        return name
    elif '-' in name:
        name = name.replace('-','')
        return name
    else:
        return name

def uppercase(name):
    name = name.upper()
    return name

def lowercase(name):
    name = name.lower()
    return name

# Dynamic statistics for ranking and database support.
def energy_ranker(num):
#     edge case of uncertain energy use value
    if num == 0.0:
        num = 'Good Case Client: Moderate Priority'
        return num
    elif num <= np.percentile(df['site_energy_usage_kBTU/sf'],25) and num > 0:
        num = 'Long Term Benefit: Less Priority'
        return num
    elif num > np.percentile(df['site_energy_usage_kBTU/sf'],25) and num <= np.percentile(df['site_energy_usage_kBTU/sf'],50):
        num = 'Good Case Client: Moderate Priority'
        return num
    elif num > np.percentile(df['site_energy_usage_kBTU/sf'],50) and num <= np.percentile(df['site_energy_usage_kBTU/sf'],75):
        num = 'Ideal Client: High Priority'
        return num
    elif num > np.percentile(df['site_energy_usage_kBTU/sf'],75):
        num = 'Energy Intensive: Highest Priority'
        return num
    else:
        num = 'Good Case Client: Moderate Priority'
        return num
    
def e_place(name):
    name = str(name)
    if name[-2:] == 'AV':
        name = name + 'E'
        return name
    else:
        return name
    
def space_fix(name):
    if ' S' in name:
        name = name.replace(' ','')
        return name
    else:
        return name
    
def space_fix_num(name):
    name = name.replace(' ','')
    return name

def str_make(name):
    return str(name)

def num_fix(num):
    if not num[:2].isnumeric():
        num = 'NULL'
        return num
    else:
        return num

# Combined data for past 5 years used for prototype retrieved locally.
df = pd.read_csv('local_data.csv')

# File refreshes each year.
# df = pd.read_excel('https://data.boston.gov/dataset/b09a8b71-274b-4365-9ce6-49b8b44602ef/resource/033c30b4-8d28-40ad-9572-43d8455aaab6/download/berdo-disclosure-for-calendar-year-2019-final.xlsx')

# API call for owner data joining.
url2 = 'https://data.boston.gov/api/3/action/datastore_search_sql?sql=SELECT%20*%20from%20"391a32e6-d4bb-48d3-a990-cb35a5768a40"'
result2 = requests.get(url2)
dict2 = json.loads(result2.text)
resultdf2 = pd.DataFrame(dict2)
df2 = pd.DataFrame(resultdf2['result'][1])

# Column to drop from local data.
# df.drop(columns=['Unnamed: 0'],inplace=True)

# Columns to drop from API call data.
# df.drop(columns=['Years Reported','User Sumbitted Link'],inplace=True)


df['Address'].fillna('NULL',inplace=True)
df[' Total Site Energy (kBTU) '].fillna('NULL',inplace=True)
df['Site EUI (kBTU/sf)'].fillna(0,inplace=True)
df['% Electricity'].fillna('Not available',inplace=True)
df['GHG Intensity (kgCO2/sf)'].fillna('Not available',inplace=True)
df['User Submitted Info'].fillna('None',inplace=True)
df[' Onsite Renewable (kWh) '].fillna(0,inplace=True)
df['% Steam'].fillna(0,inplace=True)
df['Energy Star Certified'].fillna('None',inplace=True)
df['Tax Parcel'].fillna('Unknown',inplace=True)
df['Property Uses'].fillna('Unknown',inplace=True)
df['Energy Star Score'].fillna('Not applicable to this property type',inplace=True)


df = df[df['Address'] != 'NULL'].copy()
df = df[df[' Total Site Energy (kBTU) '] != 'NULL'].copy()
df['Site EUI (kBTU/sf)'] = df['Site EUI (kBTU/sf)'].map(na_fixer)

df = df.drop_duplicates(subset=['Address']).copy()

df = df[['Property Name','Property Type','Property Uses','Year Built',
                    'Address','ZIP',' Gross Area (sq ft) ','Site EUI (kBTU/sf)',
                   ' Total Site Energy (kBTU) ','% Electricity',
                   'GHG Intensity (kgCO2/sf)',' Onsite Renewable (kWh) ']].copy()

# rename DataFrame columes to remove spaces, characters, and capital letters.
renames = ['property_name','property_type','property_uses','year_built',
                    'address','ZIP','gross_area_sqft','site_energy_usage_kBTU/sf',
                   'total_site_energy_kBTU','percentage_electricity',
                   'GHG_intensity_kgCO2/sf','onsite_renewable_kWh']

df.columns = renames
df.reset_index(inplace=True)
df.drop(columns='index',inplace=True)

df['address'] = df['address'].map(spell_fix)
df['address'] = df['address'].map(suffix_maker)
df['address'] = df['address'].map(char_remove)
df['address'] = df['address'].map(uppercase)

# Join inventory data for ownership information
df2.rename(columns={'owner_list':'owner'},inplace=True)

df2['st_num'].fillna('None',inplace=True)
df2['st_name'].fillna('None',inplace=True)
df2['st_name_suf'].fillna('None',inplace=True)
df2['owner'].fillna('None',inplace=True)

df2['st_name_suf'] = df2['st_name_suf'].map(e_place)
df2['st_name_suf'] = df2['st_name_suf'].map(space_fix)
df2['st_num'] = df2['st_num'].map(str_make)
df2['st_num'] = df2['st_num'].map(space_fix_num)
df2['st_num'] = df2['st_num'].map(num_fix)

df2 = df2[df2['owner'] != 'None'].copy()
df2 = df2[df2['st_num'] != 'None'].copy()
df2 = df2[df2['st_name'] != 'None'].copy()
df2 = df2[df2['st_name_suf'] != 'None'].copy()
df2 = df2[df2['st_name_suf'] != ' '].copy()
df2 = df2[df2['st_num'] != ' '].copy()
df2 = df2[df2['st_name'] != ' '].copy()
df2 = df2[df2['st_name_suf'] != 'nan'].copy()

df2['address'] = df2['st_num'] + ' ' + df2['st_name'] + ' ' + df2['st_name_suf']
df2['address'].fillna('NULL',inplace=True)
df2 = df2[df2['address'] != 'NULL'].copy()
df2['address'] = df2['address'].map(char_remove)

df2 = df2.drop_duplicates(subset=['address']).copy()
df2.reset_index(inplace=True)
df2.drop(columns='index',inplace=True)
df2 = df2[['address','owner']].copy()
df2 = df2.copy()

# Merge both DataFrames to include name of owner.
df = df.merge(df2,how='left',left_on='address',right_on='address').copy()

# dynamic statstics for ranking
df['customer_rank'] = df['site_energy_usage_kBTU/sf'].map(energy_ranker).copy()

df = df.copy()

# https://stackoverflow.com/questions/46831294/convert-each-row-of-pandas-dataframe-to-a-separate-json-string
json_file = df.apply(lambda x: x.to_json(),axis=1)

# data appended to previous database: Export to json object.
json_file.to_json('app_data.json')