import json
import networkx as nx
import random

def resource_allocation_considering_population(global_json_path):
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    # Load paths from global data
    network_path = global_data["interdependent_infrastructure_networks_with_different_resource_demand"]
    resource_constraints_path = global_data["resource_constraints_per_day"]
    cascading_failure_path = global_data["cascading_failure_information"]
    population_data_path = global_data["population_data"]

    # Load data from files
    with open(network_path, 'r') as f:
        network_data = json.load(f)
    with open(resource_constraints_path, 'r') as f:
        resource_constraints = json.load(f)["resource_constraints"]
    with open(cascading_failure_path, 'r') as f:
        failed_nodes = json.load(f)["failed_nodes"]
    with open(population_data_path, 'r') as f:
        population_data = json.load(f)

    # Extract dynamic resource types
    resource_types = resource_constraints['repair_teams'].keys()

    # Helper function to calculate affected population
    def calculate_population_affected(recovered_nodes):
        affected_population = 0
        affected_areas = set()
        for node in recovered_nodes:
            for n in network_data["nodes"]:
                if n["Code"] == node and n.get("Service Area"):
                    areas = n["Service Area"].split(',')
                    affected_areas.update(areas)
        for area in affected_areas:
            for data in population_data:
                if data["Id"] == area:
                    affected_population += data["Population"]
        return affected_population, affected_areas

    population_size = 50
    generations = 100
    mutation_rate = 0.1

    def fitness(order):
        available_resources = {rtype: resource_constraints['repair_teams'][rtype]['resource_per_day'] for rtype in resource_types}
        cumulative_population_restored = 0

        for node in order:
            node_data = next((n for n in network_data["nodes"] if n["Code"] == node), None)
            if node_data and all(node_data.get(rtype, 0) <= available_resources[rtype] for rtype in resource_types):
                for rtype in resource_types:
                    available_resources[rtype] -= node_data.get(rtype, 0)
                pop_restored, _ = calculate_population_affected([node])
                cumulative_population_restored += pop_restored
        return -cumulative_population_restored

    def mutate(order):
        if random.random() < mutation_rate:
            idx1, idx2 = random.sample(range(len(order)), 2)
            order[idx1], order[idx2] = order[idx2], order[idx1]
        return order

    def crossover(parent1, parent2):
        idx = random.randint(0, len(parent1) - 1)
        child = parent1[:idx] + [n for n in parent2 if n not in parent1[:idx]]
        return child

    population = [random.sample(failed_nodes, len(failed_nodes)) for _ in range(population_size)]

    for _ in range(generations):
        population = sorted(population, key=lambda x: fitness(x))
        next_generation = population[:10]
        while len(next_generation) < population_size:
            parents = random.sample(population[:20], 2)
            child = crossover(parents[0], parents[1])
            child = mutate(child)
            next_generation.append(child)
        population = next_generation

    best_order = population[0]
    cumulative_population_restored = 0
    restored_areas_set = set()
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
            population_restored_today, restored_areas = calculate_population_affected(nodes_recovered_today)
            cumulative_population_restored += population_restored_today
            restored_areas_set.update(restored_areas)
            daily_recovery_order.append({
                "day": day,
                "recovered_nodes": nodes_recovered_today,
                "restored_areas": list(restored_areas_set),
                "cumulative_population_restored": cumulative_population_restored,
                "resource_allocation": resource_allocation_today
            })

        day += 1

    output_json_path = 'resource_allocation_considering_population.json'
    with open(output_json_path, 'w') as f:
        json.dump(daily_recovery_order, f, indent=4)

    global_data["resource_allocation_considering_population"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"

# Example usage
global_json_path = 'Global_Data.json'
print(resource_allocation_considering_population(global_json_path))
