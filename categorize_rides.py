#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  3 21:48:06 2025

@author: aishwaryapathak
"""
import pandas as pd
import geopandas as gpd
from datetime import time
from shapely.geometry import Point

#%% Load Data
rides = pd.read_pickle("merged_citibike_tripdata.pkl")
#%%
poly = gpd.read_file("nyc-congestion.gpkg", layer="nyc-congestion-mid")
poly = poly.to_crs(epsg=4326)

#%% Filter Rides Data to find before and after congestion policy rides during peak period 

rides['started_at'] = pd.to_datetime(rides['started_at'])
rides['day_of_week'] = rides['started_at'].dt.day_name()
rides['day_type'] = rides['started_at'].dt.dayofweek.map(lambda x: 'Weekend' if x >= 5 else 'Weekday')
rides['start_time'] = rides['started_at'].dt.time

# Define peak hours
weekday_hours = (time(5, 0), time(21, 0))
weekend_hours = (time(9, 0), time(21, 0))

# Filter by time
time_filtered = rides[
    ((rides['day_type'] == 'Weekday') & 
     (rides['start_time'] >= weekday_hours[0]) & 
     (rides['start_time'] <= weekday_hours[1])) |
    ((rides['day_type'] == 'Weekend') & 
     (rides['start_time'] >= weekend_hours[0]) & 
     (rides['start_time'] <= weekend_hours[1]))
].copy()

# Split by congestion policy date
cutoff = pd.Timestamp("2025-01-05")
before_df = time_filtered[time_filtered['started_at'] < cutoff].copy()
after_df = time_filtered[time_filtered['started_at'] >= cutoff].copy()

before_df.to_pickle("before_congestion.pkl")
after_df.to_pickle("after_congestion.pkl")
print("Saved filtered data before and after congestion policy.")

#%% Function to Classify Ride Location Categories
def categorize_rides(df, name, poly):
    # Use EPSG:4326 consistently for all layers
    start_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.start_lng, df.start_lat), crs="EPSG:4326")
    end_gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.end_lng, df.end_lat), crs="EPSG:4326")
    
    # Spatial join to check if points are within the polygon
    df['start_in_poly'] = ~gpd.sjoin(start_gdf, poly, how="left", predicate="within").index_right.isna()
    df['end_in_poly'] = ~gpd.sjoin(end_gdf, poly, how="left", predicate="within").index_right.isna()

    # Categorize trips based on spatial relationships
    df['category'] = df.apply(
        lambda row: 'inside_inside' if row['start_in_poly'] and row['end_in_poly']
        else 'inside_outside' if row['start_in_poly']
        else 'outside_inside' if row['end_in_poly']
        else 'outside_outside',
        axis=1
    )

    # Save the categorized DataFrame
    df.to_pickle(f"{name}_categorized.pkl")
    print(f"Saved categorized data: {name}_categorized.pkl")

    return df['category'].value_counts()
# Counts by category before_df and after_df:
before_category_counts = categorize_rides(before_df, "before_congestion", poly)
after_category_counts = categorize_rides(after_df, "after_congestion", poly)

# Print the counts
print("Before Category Counts:\n", before_category_counts)
print("After Category Counts:\n", after_category_counts)  

#%%
