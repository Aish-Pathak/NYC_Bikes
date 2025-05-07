#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 18 09:29:07 2025

@author: aishwaryapathak
"""

import zipfile
import pandas as pd

# Listing ZIP filenames 

zip_filenames = [
    "202410-citibike-tripdata.zip",
    "202411-citibike-tripdata.zip",
    "202412-citibike-tripdata.zip",
    "202501-citibike-tripdata.zip",
    "202502-citibike-tripdata.zip",
    "202503-citibike-tripdata.csv.zip"
]

# Reading all CSV files from all ZIPs

dfs = []
for zip_file in zip_filenames:
    with zipfile.ZipFile(zip_file, 'r') as z:
        for file_name in z.namelist():
            if file_name.endswith('.csv'):
                with z.open(file_name) as f:
                    df = pd.read_csv(f)
                    dfs.append(df)

# Merging all DataFrames

merged_df = pd.concat(dfs, ignore_index=True)

# Saving to a single Pickle file

merged_df.to_pickle("merged_citibike_tripdata.pkl")

# Output summary

print("Columns:", merged_df.columns.tolist())
print("Merged dataset shape:", merged_df.shape)
#%%