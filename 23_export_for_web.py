import pandas as pd
import json

def export_city(csv_path, output_path, city_name):
    df = pd.read_csv(csv_path)
    
    # Round values to keep file size small and clean
    records = []
    for _, row in df.iterrows():
        record = {
            'lat': round(row['lat'], 5),
            'lon': round(row['lon'], 5),
            'temp': round(row['LST_Celsius'], 2),
            'ndvi': round(row['NDVI'], 3),
            'ndbi': round(row['NDBI'], 3),
            'elevation': round(row['Elevation'], 1),
            'roads': round(row['road_length_m'], 0),
        }
        if 'distance_to_coast_m' in df.columns:
            record['coast_dist'] = round(row['distance_to_coast_m'], 0)
        records.append(record)
    
    with open(output_path, 'w') as f:
        json.dump({'city': city_name, 'cells': records}, f)
    
    print(f"Exported {len(records)} cells for {city_name} to {output_path}")

export_city('lahore_final_dataset_v2.csv', 'lahore_data.json', 'Lahore')
export_city('karachi_final_dataset_v3.csv', 'karachi_data.json', 'Karachi')