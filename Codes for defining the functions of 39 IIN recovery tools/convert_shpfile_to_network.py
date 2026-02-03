import json
import geopandas as gpd

def convert_shpfile_to_network(json_input_path: str)-> str:
    # 读取输入的JSON文件
    json_input_path = json_input_path.strip().replace('"', '')

    with open(json_input_path, 'r') as file:
        data = json.load(file)

    infrastructure_information = data['infrastructure_information']
    with open(infrastructure_information, 'r') as file:
        data = json.load(file)

    network_files = data['network_shapefiles']
    all_network_data = {'nodes': [], 'edges': []}

    for network in network_files:
        points_file = network['points']
        lines_file = network['lines']


        # 读取点和线的shapefile
        points_gdf = gpd.read_file(points_file)
        lines_gdf = gpd.read_file(lines_file)

        # 添加点的坐标信息
        points_gdf['coordinates'] = points_gdf.geometry.apply(lambda x: [x.x, x.y])

        # 构建点属性字典，并添加基础设施类型
        points_gdf['node_properties'] = points_gdf.apply(
            lambda row: {'Code': row['Code'], 'Facility': row['Facility'],
                         'Service Area': row['SA'], 'Location': row['location'],'Demands': row['Demands'],
                         'Coordinates': [row.geometry.x, row.geometry.y],
                         'Infrastructure Type': row['IT']}, axis=1)

        # 为线构建属性字典
        lines_gdf['edge_properties'] = lines_gdf.apply(
            lambda row: {'Code': row['Code'], 'Start': row['Start_node'], 'End': row['End_node'],
                         'Infrastructure Type': row['IT']}, axis=1)

        # 合并所有网络的点和边
        all_network_data['nodes'].extend(points_gdf['node_properties'].tolist())
        all_network_data['edges'].extend(lines_gdf['edge_properties'].tolist())

    # 将合并后的网络数据保存到JSON文件
    output_json_path = 'infrastructure_networks.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(all_network_data, outfile, indent=4)

    with open(json_input_path, 'r') as file:
        global_data = json.load(file)
    global_data['infrastructure_networks'] = output_json_path

    with open(json_input_path, 'w') as file:
        json.dump(global_data, file, indent=4)
    return "The path to infrastructure_networks has been saved in Global_data.json"

# 调用函数
# convert_shpfile_to_network('Global_Data.json')
