import json
import networkx as nx


def recovery_order_of_population(global_json_path):
    # Clean path
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    # Load paths from global data
    network_path = global_data["interdependent_infrastructure_networks_with_different_resource_demand"]
    cascading_failure_path = global_data["cascading_failure_identification_by_big_nodes_attacks"]
    population_data_path = global_data["population_data"]

    # Load data from files
    with open(network_path, 'r') as f:
        network_data = json.load(f)
    with open(cascading_failure_path, 'r') as f:
        failed_nodes = json.load(f)["failed_nodes"]
    with open(population_data_path, 'r') as f:
        population_data = json.load(f)

    # Create directed graph from network data
    G = nx.DiGraph()
    for edge in network_data["edges"]:
        G.add_edge(edge["Start"], edge["End"])

    # Helper function to calculate the total population affected by failures
    def calculate_population_affected(recovered_nodes):
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
        return affected_population, affected_areas

    # Recovery process: maximize cumulative served population, one node per day
    daily_recovery_order = []
    cumulative_population_restored = 0
    restored_areas_set = set()
    day = 1

    while failed_nodes:
        best_node = None
        best_population_gain = 0
        best_areas = set()

        # Select the node that maximizes cumulative served population
        for node in failed_nodes:
            population_gain, affected_areas = calculate_population_affected([node])
            if population_gain > best_population_gain:
                best_population_gain = population_gain
                best_node = node
                best_areas = affected_areas

        if best_node:
            failed_nodes.remove(best_node)
            cumulative_population_restored += best_population_gain
            restored_areas_set.update(best_areas)

            daily_recovery_order.append({
                "day": day,
                "recovered_node": best_node,
                "restored_areas": list(restored_areas_set),
                "cumulative_population_restored": cumulative_population_restored
            })

            print(f"Day {day} - Recovered node: {best_node}")
            print(f"Cumulative population restored: {cumulative_population_restored}")
        else:
            print("No node can be recovered.")
            break

        day += 1

    # Define output path and save result
    output_json_path = 'recovery_strategy_of_population_by_GA.json'
    with open(output_json_path, 'w') as f:
        json.dump(daily_recovery_order, f, indent=4)

    # Update global data output path
    global_data["recovery_strategy_of_population_by_GA"] = output_json_path
    with open(global_json_path, 'w') as f:
        json.dump(global_data, f, indent=4)

    return "The path to recovery order result has been saved in global_data.json"


# Usage example
global_json_path = 'Global_Data.json'
recovery_order_of_population(global_json_path)
