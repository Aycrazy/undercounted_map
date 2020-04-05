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


def create_portion_of_agg(df, perc_col, col_list, geo):

    for col in col_list:
        df[col+'_{0}_{1}'.format('prop',geo)] = df[perc_col]*df[col]


#Census Tract to Neighborhood crosswalk
#credit John Johnson
#source: https://github.com/jdjohn215/Milwaukee-Geo-Crosswalks/blob/master/Crosswalks/2017CensusTracts_to_Neighborhoods.csv

cross_df = pd.read_csv('https://raw.githubusercontent.com/jdjohn215/Milwaukee-Geo-Crosswalks/master/Crosswalks/2017CensusTracts_to_Neighborhoods.csv')

#%%
census_df = gpd.read_file('tl_2018_55_tract/tl_2018_55_tract.shp')

census_transformed = crs_transform(census_df)

#%%
nhood_fp = r'tl_2018_55_tract/neighborhood.shp'

nhood_shp = gpd.read_file(nhood_fp)

#%%
blockgroup_shp = gpd.read_file('Census_Block_Groups/Census_Block_Groups.shp')

blockgroup_shp = crs_transform(blockgroup_shp)
#%%
cross_df['tract'] = cross_df['tract'].astype(int)
census_transformed['GEOID'] = census_transformed['GEOID'].astype(int)

cross_x_nhood_geo_sf = pd.merge(cross_df,census_transformed, how = 'inner', left_on='tract', right_on = 'GEOID')

#%%
#block_shp = gpd.read_file('')


nhood_shp = crs_transform(nhood_shp)

#nhood_tract_join = spatial_join_type2(census_transformed,nhood_shp)

census_df = gpd.read_file('tl_2018_55_tract/tl_2018_55_tract.shp')

census_transformed = crs_transform(census_df)

census_info = pd.read_excel('tl_2018_55_tract/pdb2015tract_2010MRR_2017ACS_WI.xlsx', skiprows=[i for i in range(0,5)])

#%%
#NEW -----------------------------
cross_geo_wide_df = pd.merge(cross_x_nhood_geo_sf, census_info, how='left', left_on='tract', right_on = 'GEOID')

htc_cols = cross_geo_wide_df.columns[26:].to_list()

#create_portion_of_agg(cross_geo_wide_df, 'pct.of.tract', htc_cols, 'tract')

create_portion_of_agg(cross_geo_wide_df, 'pct.of.neighborhood', htc_cols, 'neighborhood')

cross_wide_prop_df = cross_geo_wide_df[['neighborhood'] + cross_geo_wide_df.columns.to_list()[86:]]

nhood_tract_weighted_df = cross_wide_prop_df.groupby(['neighborhood']).sum()

nhood_tract_weighted_df = pd.merge(nhood_tract_weighted_df, nhood_shp, how = 'left', left_on = 'neighborhood', right_on = 'NEIGHBORHD')

nhood_tract_weighted_sf = convert_to_sf_type2(nhood_tract_weighted_df)


#NEW -------------------------
#%%
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

all_census_htc_info.to_file("/Users/ayaspan/Documents/Personal//undercounted_map/nhoodxcensus.geojson", driver='GeoJSON')

nhood_tract_weighted_sf.to_file("/Users/ayaspan/Documents/Personal//undercounted_map/nhood_htc.geojson", driver='GeoJSON')

#%%
neighborhood_shp.to_file("neighborhood.geoJson", driver='GeoJSON')

#%%

blockgroup_shp.to_file("blockgroup.geoJson", driver='GeoJSON')

#%%

#Zipcode crosswalk work

zips_sf = gpd.read_file('tl_2017_55079_faces/tl_2017_55079_faces.shp')

zips_shp = crs_transform(zips_sf)

nhood_shp = crs_transform(nhood_shp)

nhood_zips_sf2 = spatial_join_type2(zips_shp,nhood_shp)

nhood_zips_sf1 = spatial_join(zips_shp,nhood_shp)


# %%

nhood_zips_sf2.to_file("nhood_x_zip.geoJson", driver='GeoJSON')

nhood_zips_sf2.to_file("nhood_x_zip.shp")

# %%
