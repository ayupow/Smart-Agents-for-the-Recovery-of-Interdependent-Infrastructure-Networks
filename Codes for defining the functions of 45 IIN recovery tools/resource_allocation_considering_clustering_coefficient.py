import json
import networkx as nx
import random

def resource_allocation_considering_clustering_coefficient(global_json_path):
    global_json_path = global_json_path.strip().replace('\n', '')

    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    network_path = global_data["interdependent_infrastructure_networks_with_different_resource_demand"]
    cascading_failure_path = global_data["cascading_failure_information"]
    resource_constraints_path = global_data["resource_constraints_per_day"]

    with open(network_path, 'r') as f:
        network_data = json.load(f)
    with open(cascading_failure_path, 'r') as f:
        cascading_failure_data = json.load(f)
    with open(resource_constraints_path, 'r') as f:
        resource_constraints = json.load(f)["resource_constraints"]

    G = nx.DiGraph()
    for edge in network_data['edges']:
        G.add_edge(edge['Start'], edge['End'])

    failed_nodes = cascading_failure_data['failed_nodes']
    resource_types = resource_constraints['repair_teams'].keys()

    G.remove_nodes_from(failed_nodes)

    node_progress = {}
    recovery_data = []
    day = 1

    while failed_nodes or node_progress:
        available_resources = {rtype: resource_constraints['repair_teams'][rtype]['resource_per_day'] for rtype in resource_types}
        resources_used_today = []
        recovered_nodes_today = []
        restored_areas_today = set()

        for node in failed_nodes[:]:
            node_data = next((n for n in network_data['nodes'] if n['Code'] == node), None)
            if not node_data:
                continue

            remaining_resources = node_progress.get(node, {rtype: node_data.get(rtype, 0) for rtype in resource_types})
            allocation = {}
            allocated_any = False

            for rtype in resource_types:
                allocated = min(remaining_resources[rtype], available_resources[rtype])
                if allocated > 0:
                    allocated_any = True
                available_resources[rtype] -= allocated
                allocation[rtype] = allocated
                remaining_resources[rtype] -= allocated

            if allocated_any:
                resources_used_today.append({"node": node, "resources_used": allocation})

            if all(v == 0 for v in remaining_resources.values()):
                recovered_nodes_today.append(node)
                failed_nodes.remove(node)
                node_progress.pop(node, None)

                if node_data.get("Service Area"):
                    areas = node_data["Service Area"].split(',')
                    restored_areas_today.update(areas)
            else:
                node_progress[node] = remaining_resources

        if resources_used_today:
            for node in recovered_nodes_today:
                G.add_node(node)
                for edge in network_data['edges']:
                    if edge['Start'] == node or edge['End'] == node:
                        G.add_edge(edge['Start'], edge['End'])

            clustering_coefficient = nx.average_clustering(G.to_undirected())

            recovery_data.append({
                "day": day,
                "recovered_nodes": recovered_nodes_today,
                "restored_areas": list(restored_areas_today),
                "clustering_coefficient": clustering_coefficient,
                "resource_allocation": resources_used_today
            })

        day += 1

    output_json_path = 'resource_allocation_considering_clustering_coefficient.json'
    with open(output_json_path, 'w') as f:
        json.dump(recovery_data, f, indent=4)

    global_data["resource_allocation_considering_clustering_coefficient"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The recovery data and clustering coefficient values have been saved in global_data.json"


# Example usage
global_json_path = 'Global_Data.json'
print(resource_allocation_considering_clustering_coefficient(global_json_path))