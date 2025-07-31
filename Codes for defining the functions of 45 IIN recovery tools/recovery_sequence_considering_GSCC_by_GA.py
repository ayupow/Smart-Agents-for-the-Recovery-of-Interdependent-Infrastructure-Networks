import json
import random
import networkx as nx


def initialize_population(nodes, population_size):
    """
    Initialize the population with random permutations of nodes.
    :param nodes: List of all nodes
    :param population_size: Size of the population
    :return: List of initialized individuals
    """
    population = []
    for _ in range(population_size):
        individual = nodes[:]
        random.shuffle(individual)
        population.append(individual)
    return population


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


def selection(population, fitness_scores):
    """
    Perform selection using roulette wheel method based on fitness scores.
    :param population: The current population
    :param fitness_scores: Fitness scores for each individual
    :return: Selected individuals for the next generation
    """
    total_fitness = sum(fitness_scores)
    if total_fitness == 0:
        # If all fitness scores are zero, select randomly
        selected = random.sample(population, len(population) // 2)
    else:
        selection_probs = [score / total_fitness for score in fitness_scores]
        selected_indices = random.choices(range(len(population)), selection_probs, k=len(population) // 2)
        selected = [population[i] for i in selected_indices]
    return selected


def crossover(parent1, parent2):
    """
    Perform Order Crossover (OX) to generate two child individuals, maintaining permutation validity.
    :param parent1: The first parent individual
    :param parent2: The second parent individual
    :return: Two child individuals
    """
    size = len(parent1)
    child1 = [None] * size
    child2 = [None] * size

    # Randomly choose two crossover points
    cxpoint1 = random.randint(0, size - 1)
    cxpoint2 = random.randint(0, size - 1)

    start, end = min(cxpoint1, cxpoint2), max(cxpoint1, cxpoint2)

    # Copy the slice from the first parent to the first child
    child1[start:end] = parent1[start:end]
    # Fill the remaining positions with genes from the second parent
    fill_pos = end
    for gene in parent2[end:] + parent2[:end]:
        if gene not in child1:
            if fill_pos >= size:
                fill_pos = 0
            child1[fill_pos] = gene
            fill_pos += 1

    # Repeat the process for the second child
    child2[start:end] = parent2[start:end]
    fill_pos = end
    for gene in parent1[end:] + parent1[:end]:
        if gene not in child2:
            if fill_pos >= size:
                fill_pos = 0
            child2[fill_pos] = gene
            fill_pos += 1

    return child1, child2


def mutation(individual, mutation_rate=0.02):
    """
    Perform mutation by swapping two nodes in the individual with a certain probability.
    :param individual: The individual to mutate
    :param mutation_rate: Probability of mutation
    :return: Mutated individual
    """
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            j = random.randint(0, len(individual) - 1)
            individual[i], individual[j] = individual[j], individual[i]
    return individual


def recovery_strategy_of_GSCC_by_GA(global_json_path, population_size=50, generations=100, crossover_rate=0.8,
                                    mutation_rate=0.02):
    """
    Solve the node recovery order using Genetic Algorithm based on GSCC.
    :param global_json_path: Path to the global data JSON file
    :param population_size: Size of the population
    :param generations: Number of generations to run the algorithm
    :param crossover_rate: Probability of performing crossover
    :param mutation_rate: Probability of mutation
    :return: Path to the recovery strategy result
    """

    global_json_path = global_json_path.strip().replace('\n', '')

    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    network_path = global_data["interdependent_infrastructure_networks"]

    with open(network_path, 'r') as f:
        network_data = json.load(f)

    # Read the failed nodes from the external file
    failure_file_path = 'cascading_failure_identification_under_big_nodes_attacks.json'
    with open(failure_file_path, 'r') as f:
        failure_data = json.load(f)

    failed_nodes = failure_data.get("all_failed_nodes", [])

    nodes = failed_nodes  # Use only the failed nodes for recovery
    edges = network_data.get("edges", [])
    population = initialize_population(nodes, population_size)

    best_individual = None
    best_fitness = -1

    for generation in range(generations):
        # Calculate fitness scores
        fitness_scores = [fitness(individual, network_data, edges) for individual in population]

        # Track the best individual in the current generation
        max_fitness = max(fitness_scores)
        if max_fitness > best_fitness:
            best_fitness = max_fitness
            best_individual = population[fitness_scores.index(max_fitness)]

        print(f"Generation {generation + 1}: Best Fitness = {max_fitness}")

        # Selection
        selected_population = selection(population, fitness_scores)

        # Crossover
        offspring = []
        while len(offspring) < population_size - len(selected_population):
            parent1, parent2 = random.sample(selected_population, 2)
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
                offspring.extend([child1, child2])
            else:
                offspring.extend([parent1[:], parent2[:]])
        # If offspring exceed the required size, trim the list
        offspring = offspring[:population_size - len(selected_population)]

        # Mutation
        offspring = [mutation(individual, mutation_rate) for individual in offspring]

        # Create new population
        population = selected_population + offspring

    # After all generations, evaluate the best individual
    final_best_fitness = fitness(best_individual, network_data, edges)

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
    for idx, node in enumerate(best_individual):
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

    output_json_path = 'recovery_strategy_of_GSCC_by_GA.json'
    with open(output_json_path, 'w') as f:
        json.dump(recovery_order, f, indent=4)

    # Update global data
    global_data["recovery_strategy_of_GSCC_by_GA"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"


