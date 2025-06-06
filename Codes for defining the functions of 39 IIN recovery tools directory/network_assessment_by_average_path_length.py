import json
import networkx as nx

def network_assessment_by_average_path_length(global_json_path: str):
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

    # Construct directed graph to model dependencies
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node['Code'], **node)
    for edge in edges:
        G.add_edge(edge['Start'], edge['End'], **edge)

    total_nodes = G.number_of_nodes()
    if total_nodes == 0:
        return "Error: The network is empty."

    # Calculate the average path length in the largest weakly connected component in the original network
    largest_wcc_before = max(nx.weakly_connected_components(G), key=len)
    subgraph_before = G.subgraph(largest_wcc_before).to_undirected()
    avg_path_length_before = nx.average_shortest_path_length(subgraph_before) if nx.is_connected(subgraph_before) else 0

    # Create a new graph without the failed nodes
    G_after_failure = G.copy()
    G_after_failure.remove_nodes_from(failed_nodes)

    # Calculate the average path length after cascading failures
    if G_after_failure.number_of_nodes() > 0:
        largest_wcc_after = max(nx.weakly_connected_components(G_after_failure), key=len)
        subgraph_after = G_after_failure.subgraph(largest_wcc_after).to_undirected()
        avg_path_length_after = nx.average_shortest_path_length(subgraph_after) if nx.is_connected(subgraph_after) else float('inf')
    else:
        avg_path_length_after = float('inf')

    # Calculate network resilience
    network_resilience = avg_path_length_before / avg_path_length_after if avg_path_length_after > 0 else 0

    # Prepare the result to save
    result = {
        'initial_attack_nodes': cascading_failure_data.get('initial_attack_nodes', []),  # List of initial attack nodes
        'all_failed_nodes': failed_nodes,  # Nodes failed due to cascading failure
        'number_of_failed_nodes': len(failed_nodes),  # Total number of failed nodes
        'remaining_nodes': remaining_nodes,  # Nodes remaining after cascading failure
        'number_of_remaining_nodes': len(remaining_nodes),  # Total number of remaining nodes
        'avg_path_length_before': avg_path_length_before,  # Average path length before failure
        'avg_path_length_after': avg_path_length_after,    # Average path length after failure
        'network_resilience': network_resilience,          # Network resilience ratio
    }

    output_json_path = 'network_assessment_by_average_path_length.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    print(f"Network resilience assessment results saved to {output_json_path}")

    # Update the Global_Data.json file with the path
    file_paths['network_assessment_by_average_path_length'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Global_Data.json updated with network resilience result path.")

