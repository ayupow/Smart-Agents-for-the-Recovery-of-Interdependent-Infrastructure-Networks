import json
import random

def resource_allocation_considering_time(global_json_path):
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

    # Extract dynamic resource types
    resource_types = resource_constraints['repair_teams'].keys()

    population_size = 50
    generations = 100
    mutation_rate = 0.1

    def fitness(order):
        available_resources = {rtype: resource_constraints['repair_teams'][rtype]['resource_per_day'] for rtype in resource_types}
        node_progress = {}
        node_recovery_day = {}
        day = 1
        remaining_order = order[:]

        while remaining_order or node_progress:
            available_resources_today = available_resources.copy()
            for node in remaining_order[:]:
                node_data = next((n for n in network_data["nodes"] if n["Code"] == node), None)
                if not node_data:
                    continue
                remaining_resources = node_progress.get(node, {rtype: node_data.get(rtype, 0) for rtype in resource_types})
                allocation = {}
                for rtype in resource_types:
                    allocated = min(remaining_resources[rtype], available_resources_today[rtype])
                    allocation[rtype] = allocated
                    available_resources_today[rtype] -= allocated
                    remaining_resources[rtype] -= allocated
                if all(v == 0 for v in remaining_resources.values()):
                    node_recovery_day[node] = day
                    remaining_order.remove(node)
                    node_progress.pop(node, None)
                else:
                    node_progress[node] = remaining_resources
            day += 1

        return sum(node_recovery_day.values())  # Total cumulative recovery time

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

    # Actual resource allocation simulation with best order
    node_progress = {}
    node_recovery_day = {}
    day = 1
    daily_recovery_order = []

    remaining_order = best_order[:]

    while remaining_order or node_progress:
        available_resources = {rtype: resource_constraints['repair_teams'][rtype]['resource_per_day'] for rtype in resource_types}
        resource_allocation_today = []
        recovered_today = []

        for node in remaining_order[:]:
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
                node_recovery_day[node] = day
                recovered_today.append(node)
                remaining_order.remove(node)
                node_progress.pop(node, None)
            else:
                node_progress[node] = remaining_resources

        daily_recovery_order.append({
            "day": day,
            "recovered_nodes": recovered_today,
            "resource_allocation": resource_allocation_today
        })

        day += 1

    total_cumulative_recovery_time = sum(node_recovery_day.values())

    output = {
        "daily_recovery_order": daily_recovery_order,
        "node_recovery_day": node_recovery_day,
        "total_cumulative_recovery_time": total_cumulative_recovery_time
    }

    output_json_path = 'resource_allocation_considering_time.json'
    with open(output_json_path, 'w') as f:
        json.dump(output, f, indent=4)

    global_data["resource_allocation_considering_time"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery time optimization result has been saved in global_data.json"



# Example usage
global_json_path = 'Global_Data.json'
print(resource_allocation_considering_time(global_json_path))
