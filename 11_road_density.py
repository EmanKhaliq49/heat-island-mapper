import osmnx as ox
import geopandas as gpd
import pandas as pd
import networkx as nx
import time

# Increase timeout for Overpass requests
ox.settings.timeout = 180

# Full Lahore bounding box
west, south, east, north = 66.90, 24.75, 67.25, 25.05
mid_lon = (west + east) / 2
mid_lat = (south + north) / 2

# Split into 4 quadrants
quadrants = {
    'SW': (west, south, mid_lon, mid_lat),
    'SE': (mid_lon, south, east, mid_lat),
    'NW': (west, mid_lat, mid_lon, north),
    'NE': (mid_lon, mid_lat, east, north),
}

graphs = []
for name, bbox in quadrants.items():
    print(f"Fetching {name} quadrant...")
    for attempt in range(3):  # retry up to 3 times per quadrant
        try:
            g = ox.graph_from_bbox(bbox=bbox, network_type='drive')
            print(f"  {name}: {g.number_of_edges()} road segments")
            graphs.append(g)
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            time.sleep(5)
    else:
        print(f"  {name} failed after 3 attempts — skipping (we'll handle this if it happens)")

# Merge all quadrant graphs into one
print("Merging quadrants...")
full_graph = nx.compose_all(graphs)

roads_gdf = ox.graph_to_gdfs(full_graph, nodes=False, edges=True)
print(f"Total road segments fetched: {len(roads_gdf)}")

roads_gdf.to_file('karachi_roads.geojson', driver='GeoJSON')
print("Saved raw road network as karachi_roads.geojson")