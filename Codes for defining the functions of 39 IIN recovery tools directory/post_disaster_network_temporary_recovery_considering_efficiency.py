import json
import networkx as nx
from itertools import combinations

def calculate_global_efficiency(graph):
    """
    计算网络的全局效率。
    """
    total_efficiency = 0
    nodes = list(graph.nodes())
    n = len(nodes)

    if n < 2:
        return 0  # 如果节点数小于2，效率为0

    for i in range(n):
        for j in range(i + 1, n):  # 避免重复计算
            try:
                shortest_path_length = nx.shortest_path_length(graph, source=nodes[i], target=nodes[j])
                efficiency = 1 / shortest_path_length
            except nx.NetworkXNoPath:
                efficiency = 0  # 如果节点之间没有路径，效率为0
            total_efficiency += efficiency

    return 2 * total_efficiency / (n * (n - 1))  # 归一化公式

def post_disaster_network_temporary_recovery_evaluated_by_efficiency(global_json_path: str):
    # 加载全局数据文件
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
        network_file = file_paths.get('interdependent_infrastructure_networks_with_different_resource_demand')
        failure_data_file = file_paths.get('cascading_failure_identification_by_big_nodes_attacks')

    if not network_file or not failure_data_file:
        print("Error: Network file or failure data file not found in Global_Data.json.")
        return

    # 加载网络数据
    with open(network_file, 'r') as file:
        network_data = json.load(file)

    if not isinstance(network_data, dict):
        print("Error: Network data format is incorrect.")
        return

    # 加载故障数据
    with open(failure_data_file, 'r') as file:
        failure_data = json.load(file)

    failed_nodes = failure_data.get('failed_nodes', [])
    if not failed_nodes:
        print("Error: No failed nodes found in the failure data.")
        return

    # 构建原始网络图（不包含故障节点的恢复）
    graph = nx.DiGraph()
    for edge in network_data.get('edges', []):
        graph.add_edge(edge['Start'], edge['End'])

    # 计算恢复之前的全局效率
    initial_efficiency = calculate_global_efficiency(graph)
    print(f"Initial global efficiency: {initial_efficiency}")

    # 获取基础设施类型
    node_types = {node['Code']: node['Infrastructure Type'] for node in network_data['nodes']}

    # 临时设施数量设置：例如，每种设施都有固定数量可用
    temp_facilities = {
        "generator": 3,   # 临时发电机数量
        "water": 1,       # 临时水设施数量
        "gas": 0          # 临时供气设施数量
    }

    # 筛选出与临时设施类型匹配的故障节点
    # 对于每个设施类型，只挑选那些节点，其 Infrastructure Type 与设施类型相同
    failed_nodes_by_type = {
        "generator": [node for node in failed_nodes if node_types.get(node) == "power"],  # 假设 generator 用于 power 节点
        "water": [node for node in failed_nodes if node_types.get(node) == "water"],
        "gas": [node for node in failed_nodes if node_types.get(node) == "gas"]
    }

    # 简单地贪心选择——对于每种类型，挑选数量不超过临时设施数量的节点
    best_allocation = []
    for facility_type, available_count in temp_facilities.items():
        candidates = failed_nodes_by_type.get(facility_type, [])
        # 若候选节点超过可用数量，任选前 available_count 个（或根据其他准则排序后选取）
        allocation = candidates[:available_count]
        best_allocation.extend(allocation)

    # 恢复这些节点：即将它们重新加入网络中
    recovered_graph = graph.copy()
    for node in best_allocation:
        recovered_graph.add_node(node)
        # 为该节点重新添加所有相关边
        for edge in network_data.get('edges', []):
            if edge['Start'] == node or edge['End'] == node:
                recovered_graph.add_edge(edge['Start'], edge['End'])

    # 计算恢复之后的全局效率
    recovered_efficiency = calculate_global_efficiency(recovered_graph)
    print(f"Recovered global efficiency: {recovered_efficiency}")

    # 输出结果
    result = {
        "failed_nodes": failed_nodes,
        "initial_efficiency": initial_efficiency,
        "best_allocation": best_allocation,
        "recovered_efficiency": recovered_efficiency
    }

    # 保存结果到 JSON 文件
    output_json_path = 'post_disaster_network_temporary_recovery_evaluated_by_efficiency.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    # 更新 Global_Data.json
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
    file_paths['post_disaster_network_temporary_recovery_evaluated_by_efficiency'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Post-disaster network temporary recovery results saved to {output_json_path}")
    print(f"Global_Data.json updated with the temporary recovery result path.")

