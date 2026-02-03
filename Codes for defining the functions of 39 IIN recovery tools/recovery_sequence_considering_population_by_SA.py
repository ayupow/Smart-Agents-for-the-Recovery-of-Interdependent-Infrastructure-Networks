import json
import random
import math

def recovery_strategy_of_population_by_SA(global_json_path):
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    network_path = global_data["interdependent_infrastructure_networks"]
    population_data_path = global_data["population_data"]
    failure_nodes_json_path = global_data["cascading_failure_information"]

    with open(network_path, 'r') as f:
        network_data = json.load(f)
    with open(population_data_path, 'r') as f:
        population_data = json.load(f)

    # Load the failed nodes data
    with open(failure_nodes_json_path, 'r') as f:
        failure_data = json.load(f)

    failed_nodes = failure_data.get("all_failed_nodes", [])

    def calculate_population_affected(recovered_nodes, network_data, population_data):
        affected_population = 0
        affected_areas = set()

        for node in recovered_nodes:
            for n in network_data["nodes"]:
                if n["Code"] == node and n["Service Area"]:
                    areas = n["Service Area"].split(',')
                    for area in areas:
                        affected_areas.add(area)

        for area in affected_areas:
            for data in population_data:
                if data["Id"] == area:
                    affected_population += data["Population"]

        return affected_population

    def initial_solution(nodes):
        solution = nodes[:]
        random.shuffle(solution)
        return solution

    def generate_neighbor(solution):
        if len(solution) < 2:
            # Return the solution as-is if we can't sample 2 elements
            return solution

        neighbor = solution[:]
        i, j = random.sample(range(len(neighbor)), 2)
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        return neighbor

    def fitness(individual, network_data, population_data):
        restored_areas = set()
        total_fitness = 0
        weight = len(individual)

        for node in individual:
            for n in network_data["nodes"]:
                if n["Code"] == node and n["Service Area"]:
                    areas = n["Service Area"].split(',')
                    for area in areas:
                        restored_areas.add(area)
            current_population = sum(
                data["Population"] for data in population_data if data["Id"] in restored_areas
            )
            total_fitness += current_population * weight
            weight -= 1

        return total_fitness

    def acceptance_probability(current_fitness, neighbor_fitness, temperature):
        if neighbor_fitness > current_fitness:
            return 1.0
        else:
            return math.exp((neighbor_fitness - current_fitness) / temperature)

    # Initialize solution with only failed nodes
    current_solution = initial_solution(failed_nodes)
    current_fitness = fitness(current_solution, network_data, population_data)
    best_solution = current_solution[:]
    best_fitness = current_fitness

    temperature = 1000
    cooling_rate = 0.995
    temperature_min = 1e-3
    max_iterations = 100000
    iteration = 0

    while temperature > temperature_min and iteration < max_iterations:
        neighbor_solution = generate_neighbor(current_solution)
        neighbor_fitness = fitness(neighbor_solution, network_data, population_data)

        ap = acceptance_probability(current_fitness, neighbor_fitness, temperature)

        if random.random() < ap:
            current_solution = neighbor_solution
            current_fitness = neighbor_fitness

            if current_fitness > best_fitness:
                best_solution = current_solution[:]
                best_fitness = current_fitness

        temperature *= cooling_rate
        iteration += 1

    # Calculate the final affected population
    final_population_affected = calculate_population_affected(best_solution, network_data, population_data)

    # Build recovery order and cumulative population
    recovery_order = []
    affected_areas_set = set()

    for idx, node in enumerate(best_solution):
        for n in network_data["nodes"]:
            if n["Code"] == node and n["Service Area"]:
                areas = n["Service Area"].split(',')
                for area in areas:
                    affected_areas_set.add(area)
        affected_population = calculate_population_affected(best_solution[:idx + 1], network_data, population_data)
        recovery_order.append({
            "node": node,
            "restored_areas": list(affected_areas_set),
            "cumulative_population_restored": affected_population
        })

    output_json_path = 'recovery_strategy_of_population_by_SA.json'
    with open(output_json_path, 'w') as f:
        json.dump(recovery_order, f, indent=4)

    global_data["recovery_strategy_of_population_by_SA"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"

recovery_strategy_of_population_by_SA("Global_Data.json")