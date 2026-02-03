import json
import networkx as nx


def calculate_connectivity(graph):
    """
    计算网络的连通性（最大连通子图的大小）。
    """
    if not graph.nodes():
        return 0  # 如果图中没有节点，连通性为0

    largest_cc = max(nx.weakly_connected_components(graph), key=len)
    return len(largest_cc)


def post_disaster_network_temporary_recovery_evaluated_by_connectivity(global_json_path: str):
    # 加载全局数据文件
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
        network_file = file_paths.get('interdependent_infrastructure_networks_with_different_resource_demand')
        failure_data_file = file_paths.get('cascading_failure_identification_under_big_nodes_attacks')  # 故障数据文件

    if not network_file or not failure_data_file:
        print("Network file or failure data file not found in Global_Data.json.")
        return

    # 加载网络数据
    with open(network_file, 'r') as file:
        network_data = json.load(file)

    if not isinstance(network_data, dict):
        print("Error: Network data format is incorrect.")
        return

    # 获取总资源和总需求
    total_resources = network_data.get('total_resources')
    total_demands_node = network_data.get('total_demands', {}).get('node', {})  # 仅读取节点的需求部分

    if not total_resources or not total_demands_node:
        print("Error: 'total_resources' or 'total_demands' (node) not found in the network data.")
        return

    # 加载故障数据（故障节点）
    with open(failure_data_file, 'r') as file:
        failure_data = json.load(file)

    failed_nodes = failure_data.get('all_failed_nodes', [])

    if not failed_nodes:
        print("Error: No failed nodes found in the failure data.")
        return

    # 构建网络图
    graph = nx.DiGraph()
    for edge in network_data['edges']:
        graph.add_edge(edge['Start'], edge['End'])

    # 计算初始连通性
    initial_connectivity = calculate_connectivity(graph)

    # Step 1: 资源需求和备份策略
    resource_demands = {}
    for node in network_data['nodes']:
        if 'resource_demand_type_1' in node:  # 标准化节点资源需求
            resource_demands[node['Code']] = {
                'resource_type_1': node.get('resource_demand_type_1', 0),
                'resource_type_2': node.get('resource_demand_type_2', 0),
                'resource_type_3': node.get('resource_demand_type_3', 0),
            }

    # Step 2: 备份节点以最大化恢复后的网络连通性
    backup_nodes = []
    current_total_demands = {
        'resource_type_1': total_demands_node.get('resource_type_1', 0),
        'resource_type_2': total_demands_node.get('resource_type_2', 0),
        'resource_type_3': total_demands_node.get('resource_type_3', 0),
    }

    # 备份节点并计算恢复后的网络连通性
    recovered_connectivity = initial_connectivity
    for node in failed_nodes:
        node_data = next(n for n in network_data['nodes'] if n['Code'] == node)

        # 获取节点的资源需求
        demand = resource_demands.get(node, {'resource_type_1': 0, 'resource_type_2': 0, 'resource_type_3': 0})

        # 计算备份后的总需求
        new_total_demands = {
            'resource_type_1': current_total_demands['resource_type_1'] + demand['resource_type_1'],
            'resource_type_2': current_total_demands['resource_type_2'] + demand['resource_type_2'],
            'resource_type_3': current_total_demands['resource_type_3'] + demand['resource_type_3'],
        }

        # 检查资源是否足够
        if new_total_demands['resource_type_1'] <= total_resources['resource_type_1'] and \
                new_total_demands['resource_type_2'] <= total_resources['resource_type_2'] and \
                new_total_demands['resource_type_3'] <= total_resources['resource_type_3']:
            # 如果资源足够，备份该节点
            backup_nodes.append(node_data)
            current_total_demands = new_total_demands

            # 恢复该节点并重新计算网络连通性
            graph.add_edges_from([(edge['Start'], edge['End']) for edge in network_data['edges'] if
                                  edge['Start'] == node or edge['End'] == node])
            recovered_connectivity = calculate_connectivity(graph)
        else:
            print(f"Node {node} exceeds resource limits, skipping backup.")

    # 输出结果
    result = {
        "attacked_node": failed_nodes[0],  # 第一个节点被视为被攻击节点
        "failed_nodes": failed_nodes,
        "initial_connectivity": initial_connectivity,
        "backup_nodes": [node['Code'] for node in backup_nodes],
        "recovered_connectivity": recovered_connectivity
    }

    # 保存结果到 JSON 文件
    output_json_path = 'post_disaster_network_temporary_recovery_evaluated_by_connectivity.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    # 更新 Global_Data.json
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
    file_paths['post_disaster_network_temporary_recovery_evaluated_by_connectivity'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Post disaster network temporary recovery results saved to {output_json_path}")
    print(f"Global_Data.json updated with the temporary recovery node result path.")


