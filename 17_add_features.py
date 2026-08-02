import ee
import geopandas as gpd
import pandas as pd
from shapely.geometry import box

ee.Initialize(project='solar-cycle-430808-u7')

west, south, east, north = 74.15, 31.35, 74.45, 31.65
UTM_ZONE = 'EPSG:32643'  # 43N for Lahore, 32642 for Karachi

# --- Rebuild the same grid (identical to before, for consistency) ---
west, south, east, north = 74.15, 31.35, 74.45, 31.65
bounds_gdf = gpd.GeoDataFrame(geometry=[box(west, south, east, north)], crs='EPSG:4326')
bounds_utm = bounds_gdf.to_crs(UTM_ZONE)
minx, miny, maxx, maxy = bounds_utm.total_bounds


cell_size = 500
cells = []
x = minx
while x < maxx:
    y = miny
    while y < maxy:
        cells.append(box(x, y, x + cell_size, y + cell_size))
        y += cell_size
    x += cell_size

grid = gpd.GeoDataFrame(geometry=cells, crs=UTM_ZONE)
grid['cell_id'] = range(len(grid))
grid_latlon = grid.to_crs('EPSG:4326')

print(f"Grid has {len(grid_latlon)} cells")

# --- Landsat imagery (same as before) ---
lahore_bounds = ee.Geometry.Rectangle([west, south, east, north])

collection = (
    ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(lahore_bounds)
    .filterDate('2024-04-01', '2024-06-30')
    .filter(ee.Filter.lt('CLOUD_COVER', 20))
)
# Use a median composite instead of a single image — this fills gaps
# where our bounding box spans multiple Landsat paths/rows
best_image = collection.median()

lst = (best_image.select('ST_B10').multiply(0.00341802).add(149.0).subtract(273.15).rename('LST_Celsius'))

red = best_image.select('SR_B4').multiply(0.0000275).add(-0.2)
nir = best_image.select('SR_B5').multiply(0.0000275).add(-0.2)
swir = best_image.select('SR_B6').multiply(0.0000275).add(-0.2)  # shortwave infrared, new band we're using

ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')

# NDBI formula: (SWIR - NIR) / (SWIR + NIR)
# Positive values = built-up/concrete areas, negative = vegetation/water
ndbi = swir.subtract(nir).divide(swir.add(nir)).rename('NDBI')

# --- Elevation from SRTM (separate dataset, doesn't need date filtering) ---
elevation = ee.Image('USGS/SRTMGL1_003').select('elevation').rename('Elevation')

combined = lst.addBands(ndvi).addBands(ndbi).addBands(elevation)

# --- Convert grid to Earth Engine features ---
print("Converting grid to Earth Engine format...")
ee_features = []
for _, row in grid_latlon.iterrows():
    geom = ee.Geometry.Rectangle(list(row.geometry.bounds))
    ee_features.append(ee.Feature(geom, {'cell_id': int(row['cell_id'])}))

ee_grid = ee.FeatureCollection(ee_features)

# --- Compute all 4 bands per cell in one call ---
print("Computing satellite stats per cell (LST, NDVI, NDBI, Elevation)... this will take a few minutes")
results = combined.reduceRegions(
    collection=ee_grid,
    reducer=ee.Reducer.mean(),
    scale=100
)

features = results.getInfo()['features']
sat_rows = []
for f in features:
    props = f['properties']
    sat_rows.append({
        'cell_id': props.get('cell_id'),
        'LST_Celsius': props.get('LST_Celsius'),
        'NDVI': props.get('NDVI'),
        'NDBI': props.get('NDBI'),
        'Elevation': props.get('Elevation'),
    })

sat_df = pd.DataFrame(sat_rows)
print(f"Got satellite data for {len(sat_df)} cells")

# --- Merge with road density ---
road_df = pd.read_csv('lahore_road_density.csv')
final_df = sat_df.merge(road_df, on='cell_id', how='inner')

print(f"Final merged dataset: {final_df.shape}")
print(final_df.describe())

final_df.to_csv('lahore_final_dataset_v2.csv', index=False)
print("Saved as lahore_final_dataset_v2.csv")