import networkx as nx
import json

def recovery_strategy_of_degree_centrality(global_json_path):
    """
    Generate an interdependent infrastructure recovery strategy based on degree centrality.
    The strategy focuses on restoring failed nodes based on the provided failure information.

    Input:
        global_json_path: The path to the global data file containing input and output file paths.

    Output:
        A JSON file containing the prioritized nodes and edges for recovery, and global_data is updated with the output file path.
    """

    # Read global data file
    with open(global_json_path, 'r') as f:
        file_paths = json.load(f)

    # Read network topology file
    with open(file_paths['interdependent_infrastructure_networks'], 'r') as f:
        network_topology = json.load(f)

    # Read degree centrality file
    with open(file_paths['facility_importance_using_degree_centrality'], 'r') as f:
        centrality_data = json.load(f)

    # Read failure nodes file
    with open(file_paths['cascading_failure_information'], 'r') as f:
        failure_data = json.load(f)

    # Construct graph
    G = nx.Graph()

    for edge in network_topology['edges']:
        G.add_edge(edge['Start'], edge['End'], infrastructure_type=edge['Infrastructure Type'])

    # Assign centrality values to nodes
    for node in centrality_data['nodes']:
        G.nodes[node['Code']]['degree_centrality'] = node['degree']

    # Select only failed nodes for recovery
    failed_nodes = failure_data['failed_nodes']

    # Sort failed nodes by degree centrality
    sorted_failed_nodes = sorted(
        [node for node in G.nodes(data=True) if node[0] in failed_nodes],
        key=lambda x: x[1]['degree_centrality'], reverse=True
    )

    # Sort edges related to failed nodes
    sorted_failed_edges = sorted(
        [(u, v) for u, v in G.edges() if u in failed_nodes or v in failed_nodes],
        key=lambda x: (G.nodes[x[0]]['degree_centrality'] + G.nodes[x[1]]['degree_centrality']),
        reverse=True
    )

    # Generate recovery order
    recovery_order = {
        "recovery_order": {
            "nodes": [node[0] for node in sorted_failed_nodes],
            "edges": [{"Start": edge[0], "End": edge[1]} for edge in sorted_failed_edges]
        }
    }

    # Output file path
    output_json_path = 'recovery_strategy_of_degree_centrality.json'

    # Save recovery order to output file
    with open(output_json_path, 'w') as f:
        json.dump(recovery_order, f, indent=4)

    # Update global data file path
    file_paths['recovery_strategy_of_degree_centrality'] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)

    return "The restoration strategy for failed nodes has been generated and saved to the specified JSON file."