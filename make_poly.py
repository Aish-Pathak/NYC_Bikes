import shapely
import geopandas as gpd
import contextily as ctx
import matplotlib.pyplot as plt

input_file = "nyc-congestion-boundary.gpkg"
output_file = 'nyc-congestion.gpkg'

#%%
# Read the original street segment data
raw = gpd.read_file(input_file)
raw = raw.to_crs(epsg=4326)

# Project to meters for accurate buffering
raw_proj = raw.to_crs(epsg=3857)

# Dissolve all geometries to a single MultiLineString
dis = raw_proj.dissolve()

# Create a buffer to close small gaps
buf_width = 50  # in meters
buffered = dis.buffer(buf_width)

# Extract outer polygon (largest if multiple)
if buffered.geometry.type.iloc[0] == 'MultiPolygon':
    largest = max(buffered.geometry.iloc[0], key=lambda p: p.area)
else:
    largest = buffered.geometry.iloc[0]

# Create GeoSeries for 'mid' polygon
mid = gpd.GeoSeries([largest], crs=raw_proj.crs)

# Reproject back to EPSG:4326 for saving and plotting with basemap
dis = dis.to_crs(epsg=4326)
mid = mid.to_crs(epsg=4326)

# Save to GeoPackage
mid.to_file(output_file, layer='mid', driver='GPKG')

#%%
# Plotting for reference
fig, ax = plt.subplots(dpi=300, figsize=(12, 10))
dis.plot(ax=ax, color='#F0F0F0', lw=1, edgecolor='#4B4B4B',facecolor='#E0F8E0',alpha=0.2)
mid.plot(ax=ax, color='#D3F2D1', lw=1, edgecolor='#006400',facecolor='#E0F8E0', alpha=0.2)
mid.boundary.plot(ax=ax, color='#006402',facecolor='#E0F8E0', lw=2,alpha=0.2)

ctx.add_basemap(ax, crs=dis.crs.to_string(), source=ctx.providers.CartoDB.Positron)
ax.set_title("NYC Congestion Pricing Zone Polygon", fontsize=22, fontweight='bold')

ax.set_axis_off()
ax.grid(False)
ax.set_xticks([])
ax.set_yticks([])

fig.tight_layout(pad=3)


plt.savefig("nyc-congestion-zone.png", dpi=300, bbox_inches='tight')
plt.show()
#%%
