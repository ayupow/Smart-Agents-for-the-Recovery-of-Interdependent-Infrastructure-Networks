import json
import networkx as nx

def measure_facility_importance_using_pagerank(global_json_path):
    global_json_path = global_json_path.strip().replace('"', '')

    # 读取 Global_Data.json 文件以获取 present_network 的路径
    with open(global_json_path, 'r') as f:
        file_paths = json.load(f)

    # 获取 present_network 文件的路径
    network_path = file_paths.get('interdependent_infrastructure_networks_with_cascading_failures')

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

    # 计算每个节点的 PageRank
    pagerank_values = nx.pagerank(G_present)

    # 将 PageRank 信息添加到节点数据中
    for node in present_network_data['nodes']:
        node['pagerank'] = pagerank_values.get(node['Code'], 0)

    # 保存新的网络数据到 network_with_pagerank.json 文件
    output_json_path = 'facility_importance_using_pagerank.json'
    with open(output_json_path, 'w') as f:
        json.dump(present_network_data, f, indent=4)

    # print(f"Network with PageRank saved to {output_json_path}")

    # 更新 Global_Data.json 文件，保存新的 network_with_pagerank.json 文件路径
    #output_json_path = file_paths['network_with_pagerank']
    #with open(global_json_path, 'w') as f:
      #  json.dump(file_paths, f, indent=4)

    print(f"Global_Data.json updated with facility_importance_using_pagerank path.")
    file_paths['facility_importance_using_pagerank'] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)


    return "The path to network_with_pagerank has been saved in Global_data.json"

