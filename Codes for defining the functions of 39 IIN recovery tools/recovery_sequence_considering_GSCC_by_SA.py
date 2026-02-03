import json
import random
import networkx as nx
import math
import copy


def fitness(individual, network_data, edges):
    """
    Calculate the fitness of an individual, which is the sum of GSCC sizes after each node recovery step.
    :param individual: An individual representing the order of node recovery
    :param network_data: Network data containing node information
    :param edges: List of edges in the network
    :return: Fitness value (sum of GSCC sizes)
    """
    G = nx.DiGraph()  # Assuming a directed graph; use nx.Graph() for undirected
    total_gscc_size = 0

    # Create a mapping from node to its outgoing edges
    node_to_out_edges = {}
    for edge in edges:
        start = edge["Start"]
        end = edge["End"]
        if start not in node_to_out_edges:
            node_to_out_edges[start] = []
        node_to_out_edges[start].append(end)

    for node in individual:
        G.add_node(node)
        # Add current node's outgoing edges if the target node has been recovered
        for target in node_to_out_edges.get(node, []):
            if target in G.nodes:
                G.add_edge(node, target)
        # Add edges from other recovered nodes to the current node if they point to it
        for source, targets in node_to_out_edges.items():
            if node in targets and source in G.nodes:
                G.add_edge(source, node)

        # Compute the GSCC
        if len(G) > 0:
            try:
                gscc = max(nx.strongly_connected_components(G), key=len)
                gscc_size = len(gscc)
            except ValueError:
                gscc_size = 0
        else:
            gscc_size = 0
        total_gscc_size += gscc_size

    return total_gscc_size


def generate_neighbor(solution):
    """
    Generate a neighbor solution by swapping two random nodes in the recovery order.
    :param solution: Current solution (node recovery order)
    :return: Neighbor solution
    """
    neighbor = solution.copy()
    idx1, idx2 = random.sample(range(len(neighbor)), 2)
    neighbor[idx1], neighbor[idx2] = neighbor[idx2], neighbor[idx1]
    return neighbor


def acceptance_probability(current_fitness, neighbor_fitness, temperature):
    """
    Calculate the acceptance probability for the neighbor solution.
    :param current_fitness: Fitness of the current solution
    :param neighbor_fitness: Fitness of the neighbor solution
    :param temperature: Current temperature
    :return: Acceptance probability
    """
    if neighbor_fitness > current_fitness:
        return 1.0
    else:
        return math.exp((neighbor_fitness - current_fitness) / temperature)


def recovery_strategy_of_GSCC_by_SA(global_json_path, initial_temperature=1000, cooling_rate=0.995,
                                   stopping_temperature=1e-3, max_iterations=100000):
    """
    Solve the node recovery order using Simulated Annealing based on GSCC for a subset of failed nodes.
    :param global_json_path: Path to the global data JSON file
    :param failure_data_path: Path to the cascading failure identification JSON file
    :param initial_temperature: Starting temperature for SA
    :param cooling_rate: Rate at which the temperature decreases
    :param stopping_temperature: Temperature at which the algorithm stops
    :param max_iterations: Maximum number of iterations
    :return: Path to the recovery strategy result
    """
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    network_path = global_data["interdependent_infrastructure_networks"]
    failure_data_path = global_data["cascading_failure_information"]
    # Load network data
    with open(network_path, 'r') as f:
        network_data = json.load(f)

    # Load failure data
    with open(failure_data_path, 'r') as f:
        failure_data = json.load(f)

    # Get the failed nodes from the failure data
    failed_nodes = failure_data["failed_nodes"]

    # Filter out the failed nodes from the network
    nodes = [node["Code"] for node in network_data["nodes"]]
    failed_nodes = [node for node in nodes if node in failed_nodes]

    edges = network_data.get("edges", [])

    # Initialize current solution with a random permutation of failed nodes
    current_solution = failed_nodes[:]
    random.shuffle(current_solution)
    current_fitness = fitness(current_solution, network_data, edges)

    best_solution = current_solution.copy()
    best_fitness = current_fitness

    temperature = initial_temperature
    iteration = 0

    print("Starting Simulated Annealing optimization...")
    while temperature > stopping_temperature and iteration < max_iterations:
        # Generate a neighbor solution
        neighbor_solution = generate_neighbor(current_solution)
        neighbor_fitness = fitness(neighbor_solution, network_data, edges)

        # Decide whether to accept the neighbor solution
        ap = acceptance_probability(current_fitness, neighbor_fitness, temperature)
        if ap > random.random():
            current_solution = neighbor_solution
            current_fitness = neighbor_fitness

            # Update best solution found
            if current_fitness > best_fitness:
                best_solution = current_solution.copy()
                best_fitness = current_fitness

        # Cool down the temperature
        temperature *= cooling_rate
        iteration += 1

        # Optionally, print progress every certain number of iterations
        if iteration % 1000 == 0:
            print(f"Iteration {iteration}: Best Fitness = {best_fitness}, Temperature = {temperature:.4f}")

    print("Simulated Annealing optimization completed.")
    print(f"Total iterations: {iteration}")
    print(f"Best Fitness: {best_fitness}")

    # Generate recovery order details
    G = nx.DiGraph()
    recovery_order = []
    # Create a mapping from node to its outgoing edges
    node_to_out_edges = {}
    for edge in edges:
        start = edge["Start"]
        end = edge["End"]
        if start not in node_to_out_edges:
            node_to_out_edges[start] = []
        node_to_out_edges[start].append(end)

    gscc_size = 0
    for idx, node in enumerate(best_solution):
        G.add_node(node)
        # Add current node's outgoing edges if the target node has been recovered
        for target in node_to_out_edges.get(node, []):
            if target in G.nodes:
                G.add_edge(node, target)
        # Add edges from other recovered nodes to the current node if they point to it
        for source, targets in node_to_out_edges.items():
            if node in targets and source in G.nodes:
                G.add_edge(source, node)
        # Compute the GSCC
        if len(G) > 0:
            try:
                gscc = max(nx.strongly_connected_components(G), key=len)
                gscc_size = len(gscc)
            except ValueError:
                gscc_size = 0
        else:
            gscc_size = 0
        recovery_order.append({
            "step": idx + 1,
            "node": node,
            "current_GSCC_size": gscc_size
        })

    output_json_path = 'recovery_strategy_of_GSCC_by_SA.json'
    with open(output_json_path, 'w') as f:
        json.dump(recovery_order, f, indent=4)

    # Update global data
    global_data["recovery_strategy_of_GSCC_by_SA"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"

