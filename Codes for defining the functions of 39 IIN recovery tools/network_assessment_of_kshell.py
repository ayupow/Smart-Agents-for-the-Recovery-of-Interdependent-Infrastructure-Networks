import json
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def calculate_population_restored(recovery_order, network_data, population_data):
    """
    Calculate cumulative population restored after each recovery step.

    :param recovery_order: List of nodes in the order of recovery
    :param network_data: Network data containing nodes and their service areas
    :param population_data: Population data with population counts for each area
    :return: List of cumulative population restored after each step
    """
    restored_areas = set()
    cumulative_population = []

    for node in recovery_order:
        # Get the service areas of the current node
        for n in network_data["nodes"]:
            if n["Code"] == node and n.get("Service Area"):
                areas = n["Service Area"].split(',')
                for area in areas:
                    restored_areas.add(area)
        # Calculate cumulative population after restoring this node
        current_population = sum(
            data["Population"] for data in population_data if data["Id"] in restored_areas
        )
        cumulative_population.append(current_population)

    return cumulative_population


def calculate_recovery_area(steps, populations):
    """
    Calculate the area under the recovery population curve using the trapezoidal rule and plot the curve.

    :param steps: List of recovery steps (integers)
    :param populations: List of cumulative populations at each step
    :return: Area under the recovery curve
    """
    # Calculate the area using trapezoidal rule
    area = np.trapezoid(populations, steps)

    # Plot the recovery population curve
    plt.figure(figsize=(10, 6))
    plt.plot(steps, populations, label="Cumulative Population Restored", marker='o')
    plt.fill_between(steps, populations, color="skyblue", alpha=0.4)
    plt.xlabel('Recovery Step (Node Recovery Order)')
    plt.ylabel('Cumulative Population Restored')
    plt.title('Recovery Population Curve')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    return area


def network_assessment_of_kshell(global_json_path):
    """
    Determine recovery order based on k-shell centrality and evaluate using population data.

    :param global_json_path: Path to the global data JSON file
    :return: Area under the recovery population curve as the evaluation metric
    """
    # Load global data file to get network and population data paths
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
        network_file = file_paths.get('interdependent_infrastructure_networks')
        population_file = file_paths.get('population_data')
        failure_file_path = file_paths.get('cascading_failure_information')

    if not network_file:
        print("No network file found in Global_Data.json.")
        return

    if not population_file:
        print("No population data file found in Global_Data.json.")
        return

    # Load network data
    with open(network_file, 'r') as file:
        network_data = json.load(file)

    # Load population data
    with open(population_file, 'r') as file:
        population_data = json.load(file)

    nodes = network_data.get('nodes', [])
    edges = network_data.get('edges', [])

    if not nodes or not edges:
        print("Error: Network data is incomplete.")
        return

    # Load failure data
    with open(failure_file_path, 'r') as file:
        failure_data = json.load(file)
        failed_nodes = failure_data.get("all_failed_nodes", [])

    if not failed_nodes:
        print("Error: No failed nodes found in the failure identification file.")
        return

    # Construct directed graph
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node['Code'], **node)
    for edge in edges:
        G.add_edge(edge['Start'], edge['End'], **edge)

    # Calculate K-Shell Centrality for each node
    kshell_centrality = nx.core_number(G)

    # Filter the k-shell centrality for only the failed nodes
    failed_nodes_kshell = {node: kshell_centrality[node] for node in failed_nodes if node in kshell_centrality}

    # Sort failed nodes by K-Shell Centrality (highest first)
    sorted_failed_nodes_by_kshell = sorted(failed_nodes_kshell, key=failed_nodes_kshell.get, reverse=True)

    recovery_order = sorted_failed_nodes_by_kshell  # Recovery order based solely on k-shell centrality

    # Calculate cumulative population restored after each recovery step
    cumulative_population = calculate_population_restored(recovery_order, network_data, population_data)

    # Calculate the area under the recovery curve
    steps = list(range(1, len(recovery_order) + 1))
    recovery_area = calculate_recovery_area(steps, cumulative_population)

    # Save recovery order and evaluation results to a JSON file
    result = {
        'recovery_order': recovery_order,  # Recovery order based on k-shell centrality
        'number_of_nodes': len(recovery_order),
        'cumulative_population_restored': cumulative_population,
        'overall_network_recovery_evaluation': recovery_area  # Area under the recovery curve
    }

    output_json_path = 'network_assessment_of_kshell.json'

    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    # Update the Global_Data.json file with the recovery strategy result path
    file_paths['network_assessment_of_kshell'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Global_Data.json updated with recovery strategy result path.")

    return recovery_area