import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString

def convert_CSVfile_to_JSONfile(json_input_path: str) -> str:
    json_input_path = json_input_path.strip().replace('"', '')

    with open(json_input_path, 'r') as file:
        data = json.load(file)

    infrastructure_information = data['infrastructure_information']
    with open(infrastructure_information, 'r') as file:
        data = json.load(file)

    network_files = data['network_csv_files']
    all_network_data = {'nodes': [], 'edges': []}

    for network in network_files:
        points_file = network['points']
        lines_file = network['lines']

        # Read points CSV
        points_df = pd.read_csv(points_file)
        # Create geometry Points from coordinate columns (assuming 'X' and 'Y' or 'Longitude' and 'Latitude')
        points_df['geometry'] = points_df.apply(lambda row: Point(row['X'], row['Y']), axis=1)

        points_df['node_properties'] = points_df.apply(
            lambda row: {'Code': row['Code'], 'Facility': row['Facility'],
                         'Service Area': row['SA'], 'Location': row['location'], 'Demands': row['Demands'],
                         'Coordinates': [row['X'], row['Y']],
                         'Infrastructure Type': row['IT']}, axis=1)

        # Read lines CSV
        lines_df = pd.read_csv(lines_file)
        # Assuming lines CSV has start and end node coordinates or IDs — here we just pass attributes
        lines_df['edge_properties'] = lines_df.apply(
            lambda row: {'Code': row['Code'], 'Start': row['Start_node'], 'End': row['End_node'],
                         'Infrastructure Type': row['IT']}, axis=1)

        all_network_data['nodes'].extend(points_df['node_properties'].tolist())
        all_network_data['edges'].extend(lines_df['edge_properties'].tolist())

    output_json_path = 'infrastructure_networks.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(all_network_data, outfile, indent=4)

    # Update global JSON
    with open(json_input_path, 'r') as file:
        global_data = json.load(file)
    global_data['infrastructure_networks'] = output_json_path
    with open(json_input_path, 'w') as file:
        json.dump(global_data, file, indent=4)

    return "The path to infrastructure_networks has been saved in Global_data.json"
