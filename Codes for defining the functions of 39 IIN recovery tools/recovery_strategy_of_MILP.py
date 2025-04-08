import json
from pulp import LpMinimize, LpProblem, LpVariable, lpSum, LpAffineExpression


def recovery_strategy_of_MILP(main_json_path):
    """
    处理 cascading_failure_information.json 中的失效节点，确定恢复顺序并计算恢复时间。
    节点依赖其前一个节点的恢复：只有前一个节点恢复后，当前节点才可以恢复。
    将恢复顺序和对应的恢复时间保存到新的 JSON 文件，并将该文件地址写回到 Global_Data.json 中。
    """
    main_json_path = main_json_path.strip().replace('"', '')

    output_json_path = 'recovery_strategy_of_MILP.json'

    # 读取包含各个文件路径的 Global_Data.json 文件
    with open(main_json_path, 'r') as f:
        file_paths = json.load(f)

    # 根据路径读取 interdependent_infrastructure_networks_with_resource_demand
    with open(file_paths['interdependent_infrastructure_networks_with_resource_demand'], 'r') as f:
        network_data = json.load(f)

    nodes = network_data['nodes']
    edges = network_data['edges']  # 获取边列表（起点和终点的关系）

    # 提取节点的恢复速度
    node_recovery_speed = {node['Code']: node['recovery_speed'] for node in nodes}

    # 读取 cascading_failure_information.json，获取失效节点列表
    with open(file_paths['cascading_failure_information'], 'r') as f:
        cascading_failure_data = json.load(f)
    failed_nodes = cascading_failure_data['failed_nodes']

    # 创建一个映射，获取每个节点的前驱节点（起点节点）
    preceding_node_map = {edge['End']: edge['Start'] for edge in edges}

    # 初始化 MILP 模型，目标为最小化恢复时间
    model = LpProblem(name="restoration_sequence_min_recovery_time_failed_nodes", sense=LpMinimize)

    # 创建辅助变量：每个节点的恢复顺序，整数变量（越小表示越先恢复）
    restoration_order = {node: LpVariable(name=f"restoration_order_{node}", lowBound=1, cat='Integer') for node in
                         failed_nodes}

    # 目标函数：最小化恢复时间，恢复时间与恢复顺序和恢复速度成正比
    model += lpSum(restoration_order[node] * (1 / node_recovery_speed[node]) for node in restoration_order)

    # 添加依赖约束：一个节点的恢复必须依赖于其前一个节点的恢复
    for node in failed_nodes:
        if node in preceding_node_map:  # 只有在有前驱节点的情况下才添加约束
            preceding_node = preceding_node_map[node]
            if preceding_node in failed_nodes:  # 确保前驱节点也是失效节点
                # 约束：前驱节点的恢复顺序必须早于当前节点
                model += restoration_order[node] >= restoration_order[preceding_node] + 1, \
                    f"dependency_constraint_{node}_{preceding_node}"

    # 解决 MILP 模型
    model.solve()

    # 获取最优恢复顺序
    restoration_sequence = {node: restoration_order[node].value() for node in restoration_order}

    # 计算每个节点的恢复时间: 恢复时间 = 恢复顺序 / 恢复速度
    recovery_times = {node: restoration_sequence[node] / node_recovery_speed[node] for node in restoration_sequence}

    # 计算总恢复时间：所有节点的恢复时间之和
    total_recovery_time = sum(recovery_times[node] for node in recovery_times)

    # 根据恢复顺序对节点排序，并关联恢复时间
    sorted_restoration_sequence = sorted(restoration_sequence.items(), key=lambda x: x[1])
    sorted_recovery_times = {node: recovery_times[node] for node, _ in sorted_restoration_sequence}

    # 输出数据
    output_data = {
        "restoration_sequence": sorted_restoration_sequence,
        "recovery_times": sorted_recovery_times,
        "total_recovery_time": total_recovery_time
    }

    # 将最优恢复顺序和恢复时间写入新的 JSON 文件
    with open(output_json_path, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)

    print(f"Optimized restoration sequence, recovery times, and total recovery time written to {output_json_path}")

    # 更新 Global_Data.json 文件，写入新的路径
    file_paths['recovery_strategy_of_MILP'] = output_json_path
    with open(main_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)

    print(f"Updated Global_Data.json with the new file path: {output_json_path}")

    return json.dumps({"status": "success", "output_path": output_json_path})


# 使用示例
main_json_path = 'Global_Data.json'
recovery_strategy_of_MILP(main_json_path)
