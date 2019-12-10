#%%

import pandas as pd
import geopandas as gpd
import numpy as np
import glob
from datetime import datetime
import sqlite3
import hashlib
import sys
import pdb
from shapely.geometry import Point, LineString, Polygon
from shapely.wkt import loads
from pyproj import Proj, transform
#from mke_geo import parallelize_dataframe, batch_geocode, geo_locate, splitDataFrameList
import warnings
import json
#import psycopg2
#from bs4 import BeautifulSoup
#rom dask import dataframe as dd
#from dask.multiprocessing import get
#from geoalchemy2 import Geometry, WKTElement
from multiprocessing import cpu_count
#from utils import *

def convert_to_sf_type2(df):
    '''
    return sf
    '''
    return gpd.GeoDataFrame(df, geometry=df.geometry)


def crs_transform(sf):
    return sf.to_crs({'init': 'epsg:4326'})

def spatial_join(sf1, sf2):
    return gpd.sjoin(sf1,sf2, how='left', op='within')

def spatial_join_type2(sf1, sf2):
    return gpd.sjoin(sf1,sf2, how='left', op='intersects')


#%%
census_df = gpd.read_file('tl_2018_55_tract/tl_2018_55_tract.shp')

census_transformed = crs_transform(census_df)

#%%
nhood_fp = r'neighborhood/neighborhood.shp'

nhood_shp = gpd.read_file(nhood_fp)

#%%
blockgroup_shp = gpd.read_file('Census_Block_Groups/Census_Block_Groups.shp')

blockgroup_shp = crs_transform(blockgroup_shp)
#%%

#block_shp = gpd.read_file('')


nhood_shp = crs_transform(nhood_shp)

nhood_tract_join = spatial_join_type2(census_transformed,nhood_shp)

census_df = gpd.read_file('tl_2018_55_tract/tl_2018_55_tract.shp')

census_transformed = crs_transform(census_df)

census_info = pd.read_excel('tl_2018_55_tract/pdb2015tract_2010MRR_2017ACS_WI.xlsx', skiprows=[i for i in range(0,5)])

#census_info['Tract_str'] = census_info['Tract10'].apply(lambda x: "{:.2f}".format(x))

#nhood_tract_join['Name_str'] = nhood_tract_join['NAME'].apply(lambda x: "{:.2f}".format(float(x)))

nhood_tract_join['GEOID'] = nhood_tract_join['GEOID'].astype(int)

all_census_htc_info = pd.merge(census_info,nhood_tract_join, how='right', on='GEOID')

w_nhood = all_census_htc_info[pd.notna(all_census_htc_info.NEIGHBORHD)]

w_nhood['NHOOD_CONCAT'] = w_nhood[['NEIGHBORHD','GEOID']].groupby('GEOID').transform(lambda x: ', '.join(x))

w_nhood = w_nhood[['GEOID','NHOOD_CONCAT']].drop_duplicates(keep='first')

all_census_htc_info =  pd.merge(all_census_htc_info,w_nhood, how='left', on='GEOID').drop_duplicates(subset =['GEOID'],keep='first')

all_census_htc_info['NEIGHBORHD'] = all_census_htc_info.apply(lambda row: row['NHOOD_CONCAT'] if pd.notna(row['NHOOD_CONCAT']) else row['NEIGHBORHD'], axis =1 )

all_census_htc_info = convert_to_sf_type2(all_census_htc_info[pd.notnull(all_census_htc_info.State)])

all_census_htc_info.to_file("/Users/ayaspan/Documents/Personal/leaflet_census_map/nhoodxcensus.geojson", driver='GeoJSON')

#%%
neighborhood_shp.to_file("neighborhood.geoJson", driver='GeoJSON')

#%%

blockgroup_shp.to_file("blockgroup.geoJson", driver='GeoJSON')
