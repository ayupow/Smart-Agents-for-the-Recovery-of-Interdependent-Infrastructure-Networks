import json
import networkx as nx

def network_assessment_by_node_reachability(global_json_path: str):
    # Load global data file to get the network file path and cascading failure data
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
        network_file = file_paths.get('interdependent_infrastructure_networks')  # Get network file path
        cascading_failure_file = file_paths.get('cascading_failure_identification_by_big_nodes_attacks')  # Get cascading failure file path

    if not network_file or not cascading_failure_file:
        print("Error: Network file or cascading failure file not found in Global_Data.json.")
        return

    # Load network data
    with open(network_file, 'r') as file:
        network_data = json.load(file)

    if not isinstance(network_data, dict):
        print("Error: The network data is not in the correct format.")
        return

    nodes = network_data.get('nodes', [])
    edges = network_data.get('edges', [])

    if not nodes or not edges:
        return "Error: Network data is incomplete."

    # Load cascading failure data
    with open(cascading_failure_file, 'r') as file:
        cascading_failure_data = json.load(file)

    if not isinstance(cascading_failure_data, dict):
        print("Error: The cascading failure data is not in the correct format.")
        return

    failed_nodes = cascading_failure_data.get('failed_nodes', [])
    remaining_nodes = cascading_failure_data.get('remaining_nodes', [])

    if not failed_nodes or not remaining_nodes:
        return "Error: Cascading failure data is incomplete."

    # Construct an undirected graph for reachability analysis
    G = nx.Graph()
    for node in nodes:
        G.add_node(node['Code'], **node)
    for edge in edges:
        G.add_edge(edge['Start'], edge['End'], **edge)

    total_nodes = G.number_of_nodes()
    if total_nodes == 0:
        return "Error: The network is empty."

    # Compute node reachability before failures
    def node_reachability(graph):
        reachability = 0
        for component in nx.connected_components(graph):
            size = len(component)
            reachability += size ** 2  # Sum of squared component sizes
        return reachability / (total_nodes ** 2)

    reachability_before = node_reachability(G)

    # Create a new graph without the failed nodes
    G_after_failure = G.copy()
    G_after_failure.remove_nodes_from(failed_nodes)

    # Compute node reachability after cascading failures
    reachability_after = node_reachability(G_after_failure) if G_after_failure.number_of_nodes() > 0 else 0

    # Calculate network resilience based on node reachability
    network_resilience = reachability_before / reachability_after if reachability_after > 0 else 0

    # Prepare the result to save
    result = {
        'initial_attack_nodes': cascading_failure_data.get('initial_attack_nodes', []),  # List of initial attack nodes
        'all_failed_nodes': failed_nodes,  # Nodes failed due to cascading failure
        'number_of_failed_nodes': len(failed_nodes),  # Total number of failed nodes
        'remaining_nodes': remaining_nodes,  # Nodes remaining after cascading failure
        'number_of_remaining_nodes': len(remaining_nodes),  # Total number of remaining nodes
        'node_reachability_before': reachability_before,  # Node reachability before failure
        'node_reachability_after': reachability_after,    # Node reachability after failure
        'network_resilience': network_resilience,  # Resilience ratio based on node reachability
    }

    output_json_path = 'network_assessment_by_node_reachability.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    print(f"Network resilience assessment results saved to {output_json_path}")

    # Update the Global_Data.json file with the path
    file_paths['network_assessment_by_node_reachability'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Global_Data.json updated with network resilience result path.")

