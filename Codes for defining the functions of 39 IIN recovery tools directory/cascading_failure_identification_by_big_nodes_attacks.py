import json
import networkx as nx

def cascading_failure_identification_by_big_nodes_attacks(global_json_path: str):
    # Load global data file to get the facility importance (PageRank) file path
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
        pagerank_file = file_paths.get('facility_importance_using_pagerank')  # Get PageRank file path

    if not pagerank_file:
        print("No PageRank file found in Global_Data.json.")
        return

    # Load PageRank and network data from the specified file
    with open(pagerank_file, 'r') as file:
        network_data = json.load(file)

    nodes = network_data.get('nodes', [])
    edges = network_data.get('edges', [])

    if not nodes or not edges:
        return "Error: Network data is incomplete."

    # Construct directed graph
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node['Code'], **node)
    for edge in edges:
        G.add_edge(edge['Start'], edge['End'], **edge)

    # Select top 5 nodes based on PageRank
    pagerank_scores = {node['Code']: node['pagerank'] for node in nodes}
    top_5_nodes = sorted(pagerank_scores, key=pagerank_scores.get, reverse=True)[:5]
    initially_failed_nodes = set(top_5_nodes)

    # Initialize sets for cascading failure
    all_failed_nodes = set(initially_failed_nodes)
    newly_failed_nodes = set(initially_failed_nodes)

    # Cascading failure process
    while newly_failed_nodes:
        temp_new_failures = set()
        for node in newly_failed_nodes:
            # Check all outgoing connections of the failed node
            dependents = list(G.successors(node))
            for dependent in dependents:
                if dependent not in all_failed_nodes:
                    temp_new_failures.add(dependent)
        newly_failed_nodes = temp_new_failures
        all_failed_nodes.update(newly_failed_nodes)

    # Final remaining nodes after all cascades
    remaining_nodes = [node for node in G.nodes if node not in all_failed_nodes]

    # Save results
    result = {
        'initial_attack_nodes': top_5_nodes,  # Top 5 PageRank nodes as initial attack nodes
        'failed_nodes': list(all_failed_nodes),  # Nodes failed due to cascading failure
        'remaining_nodes': remaining_nodes,
        'number_of_remaining_nodes': len(remaining_nodes),
        'number_of_failed_nodes': len(all_failed_nodes),
    }

    output_json_path = 'cascading_failure_identification_by_big_nodes_attacks.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    print(f"Cascading failure analysis results saved to {output_json_path}")

    # Update the Global_Data.json file with the path
    file_paths['cascading_failure_identification_by_big_nodes_attacks'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Global_Data.json updated with cascading failure result path.")

# Usage example
global_json_path = 'Global_Data.json'
cascading_failure_identification_by_big_nodes_attacks(global_json_path)
