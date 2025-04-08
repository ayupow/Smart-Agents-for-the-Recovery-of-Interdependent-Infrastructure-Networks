import json

def post_disaster_network_temporary_recovery_evaluated_by_population(global_json_path: str):
    # Load the global data file to get the network file path and failure data file path
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
        network_file = file_paths.get('interdependent_infrastructure_networks_with_different_resource_demand_population')
        failure_data_file = file_paths.get('cascading_failure_identification_under_big_nodes_attacks')  # Failure data file

    if not network_file or not failure_data_file:
        print("Network file or failure data file not found in Global_Data.json.")
        return

    # Load network data
    with open(network_file, 'r') as file:
        network_data = json.load(file)

    if not isinstance(network_data, dict):
        print("Error: Network data format is incorrect.")
        return

    # Get total resources and total demands from the file
    total_resources = network_data.get('total_resources')
    total_demands_node = network_data.get('total_demands', {}).get('node', {})  # Read only node section of total_demands

    # Ensure total_resources and total_demands_node are loaded properly
    if not total_resources or not total_demands_node:
        print("Error: 'total_resources' or 'total_demands' (node) not found in the network data.")
        return

    # Load population data
    with open('population_data.json', 'r') as file:
        population_data = json.load(file)

    # Load failure data (failed nodes)
    with open(failure_data_file, 'r') as file:
        failure_data = json.load(file)

    failed_nodes = failure_data.get('all_failed_nodes', [])

    if not failed_nodes:
        print("Error: No failed nodes found in the failure data.")
        return

    # Step 1: Resource demands and backup strategy for nodes
    resource_demands = {}
    for node in network_data['nodes']:
        if 'resource_demand_type_1' in node:  # Standardize node resource demands
            resource_demands[node['Code']] = {
                'resource_type_1': node.get('resource_demand_type_1', 0),
                'resource_type_2': node.get('resource_demand_type_2', 0),
                'resource_type_3': node.get('resource_demand_type_3', 0),
            }

    # Step 2: Backup selected nodes to minimize failure and improve network performance
    backup_nodes = []
    current_total_demands = {
        'resource_type_1': total_demands_node.get('resource_type_1', 0),
        'resource_type_2': total_demands_node.get('resource_type_2', 0),
        'resource_type_3': total_demands_node.get('resource_type_3', 0),
    }

    # Calculate the total demand of all failed nodes
    for node in failed_nodes:
        node_data = next(n for n in network_data['nodes'] if n['Code'] == node)

        if 'Service Area' in node_data and node_data['Service Area']:
            service_area = node_data['Service Area'].split(',')

            # Get the resource demands of the node
            demand = resource_demands.get(node, {'resource_type_1': 0, 'resource_type_2': 0, 'resource_type_3': 0})

            # Calculate the new total demand with the backup node
            new_total_demands = {
                'resource_type_1': current_total_demands['resource_type_1'] + demand['resource_type_1'],
                'resource_type_2': current_total_demands['resource_type_2'] + demand['resource_type_2'],
                'resource_type_3': current_total_demands['resource_type_3'] + demand['resource_type_3'],
            }

            # Check if the new total demand exceeds the total resources
            if new_total_demands['resource_type_1'] <= total_resources['resource_type_1'] and \
                    new_total_demands['resource_type_2'] <= total_resources['resource_type_2'] and \
                    new_total_demands['resource_type_3'] <= total_resources['resource_type_3']:
                # If the resources allow, add the node to the backup list
                backup_nodes.append(node_data)
                # Update the current total demands
                current_total_demands = new_total_demands
            else:
                print(f"Node {node} exceeds resource limits, skipping backup.")

    # Step 3: Recalculate the affected areas and population with the backup nodes
    backup_areas = set()
    for node in backup_nodes:
        if 'Service Area' in node:
            backup_areas.update(node['Service Area'].split(','))

    # Determine the new failed areas after backing up the nodes
    failed_areas = set()
    for node in failed_nodes:
        node_data = next(n for n in network_data['nodes'] if n['Code'] == node)
        if 'Service Area' in node_data and node_data['Service Area']:
            failed_areas.update(node_data['Service Area'].split(','))

    new_failed_areas = failed_areas - backup_areas
    new_affected_population = sum([area['Population'] for area in population_data if area['Id'] in new_failed_areas])

    # Output the results
    result = {
        "attacked_node": failed_nodes[0],  # The first node is considered the attacked node
        "failed_nodes": failed_nodes,
        "failed_areas": list(failed_areas),
        "affected_population": sum([area['Population'] for area in population_data if area['Id'] in failed_areas]),
        "backup_nodes": [node['Code'] for node in backup_nodes],
        "new_failed_areas": list(new_failed_areas),
        "new_affected_population": new_affected_population
    }

    # Save the result to a JSON file
    output_json_path = 'post_disaster_network_temporary_recovery_evaluated_by_population.json'
    with open(output_json_path, 'w') as outfile:
        json.dump(result, outfile, indent=4)

    # Update Global_Data.json
    with open(global_json_path, 'r') as file:
        file_paths = json.load(file)
    file_paths['post_disaster_network_temporary_recovery_evaluated_by_population'] = output_json_path
    with open(global_json_path, 'w') as file:
        json.dump(file_paths, file, indent=4)

    print(f"Post disaster network temporary recovery results saved to {output_json_path}")
    print(f"Global_Data.json updated with the temporary recovery node result path.")

post_disaster_network_temporary_recovery_evaluated_by_population("Global_Data.json")