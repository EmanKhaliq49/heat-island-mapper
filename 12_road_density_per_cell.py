import geopandas as gpd
import numpy as np
from shapely.geometry import box

print("Loading road network...")
roads = gpd.read_file('karachi_roads.geojson')

# Reproject to a metric coordinate system (UTM zone 43N covers Karachi)
# This makes distance/length calculations accurate in meters, not degrees
roads_utm = roads.to_crs('EPSG:32642')

# Rebuild our grid, but this time in meters for precision
west, south, east, north = 66.90, 24.75, 67.25, 25.05
bounds_gdf = gpd.GeoDataFrame(geometry=[box(west, south, east, north)], crs='EPSG:4326')
bounds_utm = bounds_gdf.to_crs('EPSG:32642')
minx, miny, maxx, maxy = bounds_utm.total_bounds

cell_size = 500  # meters, matches our earlier grid
cells = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        cells.append(box(x, y, x + cell_size, y + cell_size))
        y += cell_size
    x += cell_size

grid = gpd.GeoDataFrame(geometry=cells, crs='EPSG:32642')
grid['cell_id'] = range(len(grid))
print(f"Built grid with {len(grid)} cells")

# Spatial join: find which roads fall in which cells, then sum length per cell
print("Computing road length per cell... this may take a minute")
roads_utm['length_m'] = roads_utm.geometry.length

joined = gpd.overlay(roads_utm[['geometry', 'length_m']], grid, how='intersection')
joined['segment_length_m'] = joined.geometry.length  # length of the clipped piece within the cell

road_density = joined.groupby('cell_id')['segment_length_m'].sum().reset_index()
road_density.columns = ['cell_id', 'road_length_m']

# Merge back with grid to get cell centers, convert back to lat/lon
grid = grid.merge(road_density, on='cell_id', how='left')
grid['road_length_m'] = grid['road_length_m'].fillna(0)  # cells with no roads = 0

grid_latlon = grid.to_crs('EPSG:4326')
grid_latlon['centroid'] = grid_latlon.geometry.centroid
grid_latlon['lon'] = grid_latlon['centroid'].x
grid_latlon['lat'] = grid_latlon['centroid'].y

output = grid_latlon[['cell_id', 'lon', 'lat', 'road_length_m']]
output.to_csv('karachi_road_density.csv', index=False)

print(f"Saved {len(output)} cells with road density")
print(output.describe())