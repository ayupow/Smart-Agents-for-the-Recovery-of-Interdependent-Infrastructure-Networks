import json
import os

def resource_allocation_considering_carbon_emissions(global_json_path):
    global_json_path = global_json_path.strip().replace('\n', '')

    # Load global data
    with open(global_json_path, 'r') as f:
        global_data = json.load(f)

    # Load paths from global data
    network_path = global_data["interdependent_infrastructure_networks_with_different_resource_demand"]
    resource_providers_information_path = global_data["resource_provider_distance"]
    cascading_failure_path = global_data["cascading_failure_by_random_attacks"]

# Load detailed data
    with open(network_path, 'r') as f:
            network_data = json.load(f)

    with open(resource_providers_information_path, 'r') as f:
            providers_data = json.load(f)

    with open(cascading_failure_path, 'r') as f:
            cascading_data = json.load(f)

        # Extract failed nodes
    failed_nodes = cascading_data["all_failed_nodes"]
    node_demand_info = {}

    # 这里改为访问 network_data["nodes"]
    for node in network_data["nodes"]:
        if node["Code"] in failed_nodes:
            node_demand_info[node["Code"]] = {
                "resource_demand_type_1": node.get("resource_demand_type_1", 0),
                "resource_demand_type_2": node.get("resource_demand_type_2", 0),
                "resource_demand_type_3": node.get("resource_demand_type_3", 0),
            }

        # Build supply map
    supply_map = {}
    for provider_name, provider_info in providers_data.items():
        for rtype in provider_info["resource_available_type"]:
            supply_map.setdefault(rtype, []).append((provider_name, provider_info["distance_to_nodes"]))

    allocation_result = {}
    total_emission = 0.0
    em_factor = 0.02

    for node_code, demands in node_demand_info.items():
        allocation_result[node_code] = {}
        for i in range(1, 4):
            demand_type = f"resource_demand_type_{i}"
            demand_qty = demands[demand_type]
            if demand_qty <= 0:
                continue
            rtype = f"type_{i}"
            if rtype not in supply_map:
                 continue

                # Find nearest supplier(s)
            candidates = supply_map[rtype]
            sorted_candidates = sorted(candidates, key=lambda x: x[1].get(node_code, float('inf')))
            assigned = 0
            for provider, dist_dict in sorted_candidates:
                distance = dist_dict.get(node_code, float('inf'))
                if distance == float('inf'):
                    continue
                allocation_result[node_code].setdefault(provider, {})
                allocation_result[node_code][provider][rtype] = demand_qty
                total_emission += distance * demand_qty * em_factor
                break  # since resource is infinite, take from the nearest only

    output = {
        "resource_allocation": allocation_result,
        "total_carbon_emissions": total_emission
    }

    with open("resource_allocation_considering_carbon_emissions.json", "w") as f:
        json.dump(output, f, indent=4)

    print("Resource allocation completed. Output saved to 'resource_allocation_considering_carbon_emissions.json'.")

resource_allocation_considering_carbon_emissions("Global_Data.json")