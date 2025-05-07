#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  4 13:00:36 2025

@author: aishwaryapathak
"""


import os
import zipfile
import pandas as pd
import seaborn as sns
import geopandas as gpd
import contextily as ctx
from shapely.ops import split
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString, MultiLineString

# Reading the roads shapefile
roads = gpd.read_file("tl_2021_36061_roads.zip")
roads.columns 

#%%
# Streets of interest
target_streets = [
    'W 60th St', 'E 60th St', 'F D R Dr', 'West St',
    '12th Ave', 'Lincoln Hwy', 'Battery Park Viaduct'
]

# Filter roads
main_segments = roads[roads['FULLNAME'].isin(target_streets)].copy()
# Remove unwanted LINEARIDs from main_segments
unwanted_ids = ['1106087451467', '1106087451466', '1104989403283']
main_segments = main_segments[~main_segments['LINEARID'].isin(unwanted_ids)].copy()

fdr = main_segments[main_segments['FULLNAME'] == 'F D R Dr']
others = main_segments[main_segments['FULLNAME'] != 'F D R Dr']

# Cut F D R Dr south of (-73.958472, 40.759057)
cut_point = Point(-73.958472, 40.759057).buffer(0.0001)
fdr_merged = fdr.unary_union
split_parts = split(fdr_merged, cut_point)
fdr_south = [g for g in split_parts.geoms if g.centroid.y < 40.759057]

fdr_trimmed = gpd.GeoDataFrame({'FULLNAME': ['F D R Dr'] * len(fdr_south), 'geometry': fdr_south}, crs=roads.crs)
selected_roads = pd.concat([others, fdr_trimmed], ignore_index=True)
dissolved = selected_roads.dissolve(by='FULLNAME').reset_index()

# Connect W 60th Street to E 60th Street
def coords(geom):
    return list(geom.coords) if isinstance(geom, LineString) else list(geom.geoms[0].coords)

# Creating the W 60th to E 60th connector
try:
    w60 = coords(dissolved.loc[dissolved['FULLNAME'] == 'W 60th St', 'geometry'].values[0])
    e60 = coords(dissolved.loc[dissolved['FULLNAME'] == 'E 60th St', 'geometry'].values[0])
    connector_we = gpd.GeoDataFrame({'FULLNAME': ['W-E 60th Connector'], 'geometry': [LineString([w60[-1], e60[0]])]}, crs=roads.crs)
except:
    connector_we = gpd.GeoDataFrame()  # Empty in case of error

# Connect W 60th Street to 12th Ave at (40.773361, -73.992951)
try:
    connection_point = [(-73.992951, 40.773361)]  # Coordinates for 12th Ave at the given location
    connector_w12th = gpd.GeoDataFrame({
        'FULLNAME': ['W-E 60th St Connector'],
        'geometry': [LineString([w60[-1], connection_point[0]])]
    }, crs=roads.crs)
except:
    connector_w12th = gpd.GeoDataFrame()  # Empty in case of error

# Combine connectors and dissolve final roads
final = pd.concat([dissolved, connector_we, connector_w12th], ignore_index=True)

#%%
# Plotting for reference

fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
final.plot(ax=ax, column='FULLNAME', linewidth=2.5, cmap='Set2', legend=True,
           legend_kwds={'loc': 'lower right', 'fontsize': 7, 'title': 'Street'})



ctx.add_basemap(ax, crs=final.crs.to_string(), source=ctx.providers.CartoDB.Positron)
ax.set_title("NYC Congestion Pricing Zone Boundary", fontsize=16, weight='bold')
ax.set_axis_off()
plt.tight_layout()
plt.savefig("nyc_congestion_boundary.png", dpi=300, bbox_inches='tight')
plt.show()

#%% Export to GeoPackage

final.to_crs(epsg=4326).to_file("nyc-congestion-boundary.gpkg", driver="GPKG")


#%%