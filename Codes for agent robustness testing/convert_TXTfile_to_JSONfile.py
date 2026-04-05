import json
import pandas as pd
from shapely.geometry import Point


def convert_TXTfile_to_JSONfile(json_input_path: str) -> str:
    # 清理路径字符串
    json_input_path = json_input_path.strip().replace('"', '')

    # 1. 读取 Global_Data.json 获取基础配置路径
    with open(json_input_path, 'r') as file:
        data = json.load(file)

    # 2. 读取次级 JSON 获取具体的 TXT 文件路径
    infrastructure_information_path = data['infrastructure_information']
    with open(infrastructure_information_path, 'r') as file:
        infra_data = json.load(file)

    # 假设次级 JSON 中的键名可能从 'network_csv_files' 变更为 'network_txt_files'
    # 这里做个兼容处理
    network_files = infra_data.get('network_txt_files', infra_data.get('network_csv_files'))

    all_network_data = {'nodes': [], 'edges': []}

    for network in network_files:
        points_file = network['points']
        lines_file = network['lines']

        # 3. 读取节点 TXT (sep=None 表示自动检测分隔符，如空格、制表符或逗号)
        points_df = pd.read_csv(points_file, sep=None, engine='python')

        # 将节点属性转换为字典列表
        # 假设 TXT 里的列名保持不变：Code, Facility, SA, location, Demands, X, Y, IT
        nodes_list = points_df.apply(
            lambda row: {
                'Code': str(row['Code']),
                'Facility': row['Facility'],
                'Service Area': row['SA'],
                'Location': row['location'],
                'Demands': row['Demands'],
                'Coordinates': [float(row['X']), float(row['Y'])],
                'Infrastructure Type': row['IT']
            }, axis=1).tolist()

        # 4. 读取边 TXT
        lines_df = pd.read_csv(lines_file, sep=None, engine='python')

        # 假设边 TXT 列名：Code, Start_node, End_node, IT
        edges_list = lines_df.apply(
            lambda row: {
                'Code': str(row['Code']),
                'Start': str(row['Start_node']),
                'End': str(row['End_node']),
                'Infrastructure Type': row['IT']
            }, axis=1).tolist()

        all_network_data['nodes'].extend(nodes_list)
        all_network_data['edges'].extend(edges_list)

    # 5. 保存生成的网络数据为 JSON
    output_json_path = 'infrastructure_networks.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(all_network_data, outfile, indent=4)

    # 6. 更新 Global_Data.json 记录新生成的网络文件路径
    data['infrastructure_networks'] = output_json_path
    with open(json_input_path, 'w') as file:
        json.dump(data, file, indent=4)

    return "The path to infrastructure_networks has been saved in Global_data.json"