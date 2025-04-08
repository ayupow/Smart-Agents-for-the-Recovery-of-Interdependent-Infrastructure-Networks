import json
import random

def resource_allocation_by_time(global_json_path):
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    # Load paths from global data
    network_path = global_data["interdependent_infrastructure_networks_with_different_resource_demand"]
    resource_constraints_path = global_data["resource_constraints_per_day"]
    cascading_failure_path = global_data["cascading_failure_information"]

    # Load data from files
    with open(network_path, 'r') as f:
        network_data = json.load(f)
    with open(resource_constraints_path, 'r') as f:
        resource_constraints = json.load(f)["resource_constraints"]
    with open(cascading_failure_path, 'r') as f:
        failed_nodes = json.load(f)["failed_nodes"]

    # Extract resource types
    resource_types = resource_constraints['repair_teams'].keys()

    # Helper function to calculate recovery time per node
    def calculate_recovery_time(node_data):
        recovery_time = 0
        for rtype in resource_types:
            demand = node_data.get(rtype, 0)
            available_per_day = resource_constraints['repair_teams'][rtype]['resource_per_day']
            if available_per_day > 0:
                recovery_time = max(recovery_time, (demand / available_per_day))
        return recovery_time

    # Helper function to calculate total recovery time for all nodes in order
    def fitness(order):
        total_recovery_time = 0
        for node in order:
            node_data = next((n for n in network_data["nodes"] if n["Code"] == node), None)
            if node_data:
                total_recovery_time += calculate_recovery_time(node_data)
        return total_recovery_time

    population_size = 50
    generations = 100
    mutation_rate = 0.1

    def mutate(order):
        if random.random() < mutation_rate:
            idx1, idx2 = random.sample(range(len(order)), 2)
            order[idx1], order[idx2] = order[idx2], order[idx1]
        return order

    def crossover(parent1, parent2):
        idx = random.randint(0, len(parent1) - 1)
        child = parent1[:idx] + [n for n in parent2 if n not in parent1[:idx]]
        return child

    # Initialize population (each individual is a random order of failed nodes)
    population = [random.sample(failed_nodes, len(failed_nodes)) for _ in range(population_size)]

    # Run the genetic algorithm
    for _ in range(generations):
        population = sorted(population, key=lambda x: fitness(x))
        next_generation = population[:10]
        while len(next_generation) < population_size:
            parents = random.sample(population[:20], 2)
            child = crossover(parents[0], parents[1])
            child = mutate(child)
            next_generation.append(child)
        population = next_generation

    # Get the best order (node recovery sequence)
    best_order = population[0]

    # Simulate recovery based on the best order
    daily_recovery_order = []
    day = 1
    node_progress = {}

    while best_order or node_progress:
        available_resources = {rtype: resource_constraints['repair_teams'][rtype]['resource_per_day'] for rtype in resource_types}
        nodes_recovered_today = []
        resource_allocation_today = []

        for node in best_order[:]:
            node_data = next((n for n in network_data["nodes"] if n["Code"] == node), None)
            if not node_data:
                continue

            remaining_resources = node_progress.get(node, {rtype: node_data.get(rtype, 0) for rtype in resource_types})
            allocation = {}
            for rtype in resource_types:
                allocated = min(remaining_resources[rtype], available_resources[rtype])
                available_resources[rtype] -= allocated
                allocation[rtype] = allocated
                remaining_resources[rtype] -= allocated

            resource_allocation_today.append({"node": node, "resources_used": allocation})

            if all(v == 0 for v in remaining_resources.values()):
                nodes_recovered_today.append(node)
                best_order.remove(node)
                node_progress.pop(node, None)
            else:
                node_progress[node] = remaining_resources

        if resource_allocation_today:
            daily_recovery_order.append({
                "day": day,
                "recovered_nodes": nodes_recovered_today,
                "resource_allocation": resource_allocation_today
            })

        day += 1

    output_json_path = 'resource_allocation_by_time.json'
    with open(output_json_path, 'w') as f:
        json.dump(daily_recovery_order, f, indent=4)

    global_data["resource_allocation_by_time"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"

