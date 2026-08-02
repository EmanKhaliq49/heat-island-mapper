import osmnx as ox
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

UTM_ZONE = 'EPSG:32642'  # Karachi's UTM zone

# Pull the coastline — use a slightly wider box than our study area,
# since the coastline itself may extend beyond our exact bounding box
coast_bbox = (66.70, 24.60, 67.45, 25.15)

print("Fetching coastline data from OpenStreetMap...")
coastline = ox.features_from_bbox(bbox=coast_bbox, tags={'natural': 'coastline'})
print(f"Found {len(coastline)} coastline segments")

# Reproject to metric CRS for accurate distance calculations
coastline_utm = coastline.to_crs(UTM_ZONE)

# Combine all coastline segments into one geometry for distance calculations
coastline_union = coastline_utm.geometry.union_all()

# Load our existing Karachi dataset
df = pd.read_csv('karachi_final_dataset_v2.csv')

# Convert each cell's lon/lat into a point, reproject to UTM
points = gpd.GeoDataFrame(
    df,
    geometry=[Point(xy) for xy in zip(df['lon'], df['lat'])],
    crs='EPSG:4326'
)
points_utm = points.to_crs(UTM_ZONE)

# Compute distance from each point to the nearest coastline point, in meters
print("Computing distance to coast for each cell...")
points_utm['distance_to_coast_m'] = points_utm.geometry.distance(coastline_union)

# Save the enriched dataset
output = points_utm.drop(columns='geometry')
output.to_csv('karachi_final_dataset_v3.csv', index=False)

print(f"Saved {len(output)} cells with coast distance")
print(output['distance_to_coast_m'].describe())