#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  3 15:26:49 2025

@author: aishwaryapathak
"""


import os
import zipfile
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point, LineString, MultiLineString
#%%
before_df = pd.read_pickle("before_congestion_categorized.pkl")
after_df = pd.read_pickle("after_congestion_categorized.pkl")

#%%
# Calculating Total Average Daily Rides
# Total rides
total_rides_before = before_df['ride_id'].count()
total_rides_after = after_df['ride_id'].count()

# Extracting date
before_df['date'] = pd.to_datetime(before_df['started_at'], format="%Y-%m-%d %H:%M:%S.%f").dt.date
after_df['date'] = pd.to_datetime(after_df['started_at'], format="%Y-%m-%d %H:%M:%S.%f").dt.date

# Counting unique days
days_before = before_df['date'].nunique()
days_after = after_df['date'].nunique()

# Average daily rides
avg_daily_rides_before = total_rides_before / days_before
avg_daily_rides_after = total_rides_after / days_after

# Print results
print(f"Average daily rides (before): {avg_daily_rides_before:.2f}")
print(f"Average daily rides (after): {avg_daily_rides_after:.2f}")


#%% 
# Calculating Average Daily Rides by Category
before_cat = before_df.groupby('category')['ride_id'].count() / days_before
after_cat = after_df.groupby('category')['ride_id'].count() / days_after
avg_cat_df = pd.DataFrame({
    'Before': before_cat,
    'After': after_cat
}).fillna(0)
print(avg_cat_df)
#%%
# Plotting Average Daily Rides by Category Bar Chart

plt.style.use('ggplot')
fig, ax = plt.subplots(figsize=(10, 6))
avg_cat_df.plot(kind='bar', ax=ax, color=['#4C9F70', '#1D84B5'], edgecolor='black')
ax.set_title('Average Daily Rides by Category', fontsize=16, pad=15)
ax.set_ylabel('Average Daily Rides', fontsize=13)
ax.set_xlabel('Category', fontsize=13)
ax.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.7)
ax.set_axisbelow(True)
plt.xticks(rotation=45, ha='right', fontsize=11)
for container in ax.containers:
    ax.bar_label(container, fmt='%.0f', label_type='edge', padding=3, fontsize=11)
ax.legend(title='Period', fontsize=10, title_fontsize=12, loc='upper right')
plt.tight_layout()

plt.savefig('avg_daily_rides_by_category.png', dpi=300)
plt.show()

#%%
# Defining a dictionary to combine the categories
category_map = {
    'inside_inside': 'Within Congestion Zone',
    'inside_outside': 'Border Rides',
    'outside_inside': 'Border Rides',
}

# Creating a new combined category column
before_df['combined_category'] = before_df['category'].map(category_map)
after_df['combined_category'] = after_df['category'].map(category_map)

# Calculating the average daily rides for each combined category
before_combined = before_df.groupby('combined_category')['ride_id'].count() / days_before
after_combined = after_df.groupby('combined_category')['ride_id'].count() / days_after

# Combining the results for plotting
avg_combined_df = pd.DataFrame({
    'Before': before_combined,
    'After': after_combined
}).fillna(0)

#%%
# Plotting Average Daily Rides - Border Rides vs Within Congestion Zone Rides

fig, ax = plt.subplots(figsize=(10, 6))
avg_combined_df.plot(kind='bar', ax=ax, color=['#4C9F70', '#1D84B5'], edgecolor='black')
ax.set_title('Average Daily Rides: Within Zone vs Border Rides(Inside Outside & Outside Inside)', fontsize=16, pad=15)
ax.set_ylabel('Average Daily Rides', fontsize=13)
ax.set_xlabel('Category', fontsize=13)
ax.grid(axis='y', linestyle='--', linewidth=0.7, alpha=0.7)
ax.set_axisbelow(True)
plt.xticks(rotation=0, ha='center', fontsize=11)

for container in ax.containers:
    ax.bar_label(container, fmt='%.0f', label_type='edge', padding=3, fontsize=11)

ax.legend(title='Period', fontsize=11, title_fontsize=12, loc='upper right')
plt.tight_layout()

plt.savefig('average_daily_total_rides.png', dpi=300)
plt.show()

#%%
# Trend by category and month 

before_df['year_month'] = before_df['started_at'].dt.to_period('M')
after_df['year_month'] = after_df['started_at'].dt.to_period('M')

# Grouping by month and category
before_grouped = before_df.groupby(['year_month', 'category']).agg(
    total_rides=('ride_id', 'count'),
    unique_days=('started_at', lambda x: x.dt.date.nunique())
).reset_index()

after_grouped = after_df.groupby(['year_month', 'category']).agg(
    total_rides=('ride_id', 'count'),
    unique_days=('started_at', lambda x: x.dt.date.nunique())
).reset_index()

# Computing average daily rides
before_grouped['avg_daily_rides'] = before_grouped['total_rides'] / before_grouped['unique_days']
after_grouped['avg_daily_rides'] = after_grouped['total_rides'] / after_grouped['unique_days']

# Adding a "Period" column
before_grouped['Period'] = 'Before'
after_grouped['Period'] = 'After'

# Combining datasets
trend_df = pd.concat([before_grouped, after_grouped])
trend_df['year_month'] = trend_df['year_month'].astype(str)

#%%
# Making trend line to see patterns of rides by category and month
sns.set(style="whitegrid")

plt.figure(figsize=(12, 6))
sns.lineplot(
    data=trend_df,
    x='year_month',
    y='avg_daily_rides',
    hue='category',
    style='Period',
    markers=True,
    dashes=False,
    linewidth=2.2
)

plt.title('Monthly Trend of Average Daily Rides by Category', fontsize=16, pad=15)
plt.xlabel('Month', fontsize=13)
plt.ylabel('Average Daily Rides', fontsize=13)
plt.xticks(rotation=45)

plt.legend(
    title='Category / Period',
    fontsize=10,
    title_fontsize=11,
    loc='upper left',
    bbox_to_anchor=(1.02, 1),
    borderaxespad=0
)
plt.tight_layout()

plt.savefig('monthly_trend_by_category.png', dpi=300)
plt.show()
#%%
# Defining 2 weeks blocks
# Define the end date of the before data
last_date_before = before_df['date'].max()

# Block 3 (most recent before policy)
block3_start = last_date_before - pd.Timedelta(days=13)
block3_end = last_date_before

# Block 2
block2_end = block3_start - pd.Timedelta(days=1)
block2_start = block2_end - pd.Timedelta(days=13)

# Block 1 (oldest)
block1_end = block2_start - pd.Timedelta(days=1)
block1_start = block1_end - pd.Timedelta(days=13)

# After block
first_date_after = after_df['date'].min()
after_block_end = first_date_after + pd.Timedelta(days=13)

# Filter data for each block
before1 = before_df[(before_df['date'] >= block1_start) & (before_df['date'] <= block1_end)].copy()
before2 = before_df[(before_df['date'] >= block2_start) & (before_df['date'] <= block2_end)].copy()
before3 = before_df[(before_df['date'] >= block3_start) & (before_df['date'] <= block3_end)].copy()
after = after_df[(after_df['date'] >= first_date_after) & (after_df['date'] <= after_block_end)].copy()

# Function to compute average daily rides per category
def compute_avg_daily(df, label):
    result = df.groupby('category').size().reset_index(name='total_rides')
    result['avg_daily_rides'] = result['total_rides'] / 14  # 2 weeks = 14 days
    result['period'] = label
    return result[['category', 'avg_daily_rides', 'period']]

# Apply function to each block
block1_avg = compute_avg_daily(before1, 'Before-3')
block2_avg = compute_avg_daily(before2, 'Before-2')
block3_avg = compute_avg_daily(before3, 'Before-1')
after_avg = compute_avg_daily(after, 'After')

# Combine all into one dataframe
combined_avg_df = pd.concat([block1_avg, block2_avg, block3_avg, after_avg])
combined_avg_df['period'] = pd.Categorical(
    combined_avg_df['period'],
    categories=['Before-3', 'Before-2', 'Before-1', 'After'],
    ordered=True
)

#%%

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Ensure period ordering
combined_avg_df['period'] = pd.Categorical(
    combined_avg_df['period'],
    categories=['Before-3', 'Before-2', 'Before-1', 'After'],
    ordered=True
)

# Setup
plt.figure(figsize=(12, 7))
palette = sns.color_palette("Set2")

# Create bar plot
sns.barplot(
    data=combined_avg_df,
    x='period',
    y='avg_daily_rides',
    hue='category',
    palette=palette
)

plt.axvspan(2.5, 3.5, color='gray', alpha=0.2)
plt.text(2.55, combined_avg_df['avg_daily_rides'].max() * 0.95, 'Policy\nImplemented',
         fontsize=12, color='black', ha='left', va='top')

plt.title("Average Daily Citi Bike Rides by Category\nBefore and After Congestion Pricing", fontsize=16, weight='bold')
plt.xlabel("2-Week Time Block", fontsize=12)
plt.ylabel("Average Daily Rides", fontsize=12)
plt.xticks(rotation=45, fontsize=10)
plt.yticks(fontsize=10)
plt.grid(True, which='major', axis='y', linestyle='--', alpha=0.7)


plt.legend(title='Category', fontsize=10, title_fontsize=12)

plt.tight_layout()


plt.savefig("weekly_analysis_barchart.png", dpi=300)
plt.show()