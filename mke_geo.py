import pandas as pd
import numpy as np
import glob
import datetime
import sqlite3
import hashlib
import bs4 as BeautifulSoup
import requests as req
import re
import json
from bs4 import BeautifulSoup
import multiprocessing as mp
from multiprocessing import Pool
import pdb


num_cores = mp.cpu_count()
num_partitions = 16



# def geo_locate(row):
#     if not len(row['Full_Address']):
#         sub_df['x'] = None
#         sub_df['y'] = None
#         return None
#     gl = "http://maps2.milwaukee.gov/ArcGIS/rest/services/geocode/MAIthenDIME_geocode/GeocodeServer/findAddressCandidates?Street="
#     x = row['Full_Address']
#     address = x.replace(' ', '+')
#     try:
#         response = req.get(
#             gl+address+'&SingleLine=&outFields=Loc_name&outSR=&f=json')
#     except:
#         sub_df['x'] = None
#         sub_df['y'] = None
#         return None

#     if 'html' in str(response.content):
#         soup = BeautifulSoup(response.content, 'html.parser')
#         #print(soup)
#         #for i in soup.find('ul'):
#         if soup.find('ul') != None:
#             east, north = re.findall(r'[0-9/.]+', soup.find('ul').text)
#             zipcode = re.findall(r'[0-9]{5}', soup.find('ul').text)[0]
#             #if zipcode != None:
#                 #return [east, north, zipcode]
#             #else:
#             sub_df['x'] = east
#             sub_df['y'] = north
#             return None
#         else:
#             sub_df['x'] = None
#             sub_df['y'] = None
#             return None
#     else:
#         #print(address)
#         #print(response.content)
#         res = response.json()

#         #print(res)
#         if not len(res['candidates']):
#             sub_df['x'] = None
#             sub_df['y'] = None
#             return None
#         #print(res)
#         result = res['candidates'][0]
#         #print(result)
#         geodata = dict()
#         geodata['east'] = result['location']['x']
#         geodata['north'] = result['location']['y']

#         result1 = res['candidates'][0]

#         geodata['address'] = result1['address']

#         #print(geodata['address'])

#         if (len(geodata['address'].split(',')) == 2):

#             geodata['zip'] = geodata['address'].split(',')[1]

#         else:

#             geodata['zip'] = None

#         #print(result1)
#         #print(row['id'])
#     sub_df['x'] = geodata['east']
#     sub_df['y'] = geodata['north']
#     #sub = row['id'], geodata['east'], geodata['north']

def geo_locate(row):

    if not len(row['Full_Address']):
        #return [None,None,None]
        return (None, None)
    gl = "http://maps2.milwaukee.gov/ArcGIS/rest/services/geocode/MAIthenDIME_geocode/GeocodeServer/findAddressCandidates?Street="
    x = row['Full_Address']
    address = x.replace(' ', '+')
    try:
        response = req.get(
            gl+address+'&SingleLine=&outFields=Loc_name&outSR=&f=json')
    except:
        #return [None,None,None]
        return [None, None]

    if 'html' in str(response.content):
        soup = BeautifulSoup(response.content, 'html.parser')
        #print(soup)
        #for i in soup.find('ul'):
        if soup.find('ul') != None:
            east, north = re.findall(r'[0-9/.]+', soup.find('ul').text)
            zipcode = re.findall(r'[0-9]{5}', soup.find('ul').text)[0]
            if zipcode != None:
                return [east, north]
            else:
                #return [east,north,None]
                return [east, north]
        else:
            #return [None,None,None]
            return [None, None]
    else:
        #print(address)
        #print(response.content)
        res = response.json()

        #print(res)
        if 'candidates' not in res:
            return[None, None]
        elif not len(res['candidates']):
            #return [None,None,None]
            return [None, None]

        #print(res)
        result = res['candidates'][0]
        #print(result)
        geodata = dict()
        geodata['east'] = result['location']['x']
        geodata['north'] = result['location']['y']

        result1 = res['candidates'][0]

        geodata['address'] = result1['address']

        #print(geodata['address'])

        if (len(geodata['address'].split(',')) == 2):

            geodata['zip'] = geodata['address'].split(',')[1]

        else:

            geodata['zip'] = None

        #print(result1)
        #print(row['id'])
    return [geodata['east'], geodata['north']]


def parallelize_dataframe(df, func):
    num_cores = mp.cpu_count()
    num_partitions = 16
    df_split = np.array_split(df, num_partitions)
    #df_split.reset_index().rename(columns={'index':'split_idx'})
    pool = Pool(num_cores)
    out = pool.map_async(func, df_split)
    pool.close()
    pool.join()
    return out.get()


def batch_geocode(data):
    #data = pd.DataFrame(data)
    data['utm_coords'] = data.apply(geo_locate, axis=1)
    return data


def splitDataFrameList(df, target_column, col_list):
    ''' df = dataframe to split,
    target_column = the column containing the values to split
    separator = the symbol used to perform the split
    returns: a dataframe with each entry for the target column separated, with each element moved into a new row. 
    The values in the other columns are duplicated across the newly divided rows.
    '''
    row_accumulator = []

    def splitListToRows(row):
        #new_row = {}
        #print(row)
        split_row = row[target_column]
        new_row = row.to_dict()
        for col_name, s in zip(col_list, split_row):
            new_row[col_name] = s
        row_accumulator.append(new_row)

    df.apply(splitListToRows, axis=1)
    new_df = pd.DataFrame(row_accumulator)
    return new_df
