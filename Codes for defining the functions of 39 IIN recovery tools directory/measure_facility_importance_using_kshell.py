import json
import networkx as nx

def measure_facility_importance_using_kshell(global_json_path):
    """
    读取 Global_Data.json 中的 present_network，计算每个节点的 k-shell 值，将其写入新的 JSON 文件 network_with_kshell.json，
    并将文件路径保存回 Global_Data.json。

    :param global_json_path: Global_Data.json 文件路径。
    """
    # 读取 Global_Data.json 文件以获取 present_network 的路径
    with open(global_json_path, 'r') as f:
        file_paths = json.load(f)

    # 获取 present_network 文件的路径
    network_path = file_paths.get('interdependent_infrastructure_networks')

    if not network_path:
        print("present_network path not found in Global_Data.json.")
        return

    # 读取 present_network.json 文件
    with open(network_path, 'r') as f:
        present_network_data = json.load(f)

    # 创建有向图
    G_present = nx.DiGraph()

    # 添加节点，并将 Coordinates 作为 pos 属性
    for node in present_network_data['nodes']:
        G_present.add_node(node['Code'], layer=node['Infrastructure Type'], pos=(node['Coordinates'][0], node['Coordinates'][1]))

    # 添加边
    for edge in present_network_data['edges']:
        G_present.add_edge(edge['Start'], edge['End'])

    # 转换为无向图，以便计算 k-shell 值
    G_undirected = G_present.to_undirected()

    # 计算每个节点的 k-shell 值
    kshell_values = nx.core_number(G_undirected)

    # 将 k-shell 值信息添加到节点数据中
    for node in present_network_data['nodes']:
        node['kshell'] = kshell_values.get(node['Code'], 0)

    # 保存新的网络数据到 network_with_kshell.json 文件
    output_json_path = 'facility_importance_using_kshell.json'
    with open(output_json_path, 'w') as f:
        json.dump(present_network_data, f, indent=4)

    print(f"Network with k-shell values saved to {output_json_path}")

    # 更新 Global_Data.json 文件，保存新的 network_with_kshell.json 文件路径
    file_paths['facility_importance_using_kshell'] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)

    print(f"Global_Data.json updated with network_with_kshell path.")

