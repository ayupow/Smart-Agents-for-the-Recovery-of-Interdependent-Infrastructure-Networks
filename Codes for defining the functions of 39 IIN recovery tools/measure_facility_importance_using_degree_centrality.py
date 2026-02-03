import json


def measure_facility_importance_using_degree_centrality(main_json_path):
    """
    Process interdependent_infrastructure_networks_with_resource_demand and facility_importance_using_degree_centrality,
    allocate resources based on node importance (degree) and resource demand, and save the results to a new JSON file.
    """
    main_json_path = main_json_path.strip().replace('"', '')

    output_json_path = 'macility_importance_using_degree.json'

    # Read Global_Data.json file, which contains two important paths
    with open(main_json_path, 'r') as f:
        file_paths = json.load(f)

    # Read interdependent_infrastructure_networks_with_resource_demand file
    with open(file_paths['interdependent_infrastructure_networks_with_resource_demand'], 'r') as f:
        network_data = json.load(f)

    # Read facility_importance_using_degree_centrality.json file
    with open(file_paths['facility_importance_using_degree_centrality'], 'r') as f:
        degree_data = json.load(f)

    nodes = network_data['nodes']
    total_resources = network_data['total_resources']

    # Extract node infrastructure types and degrees from the degree data
    node_infrastructure_type = {node['Code']: node['Infrastructure Type'] for node in nodes}
    node_degrees = {facility['Code']: facility['degree'] for facility in degree_data['nodes']}

    # Calculate the total degree
    total_degree = sum(node_degrees.values())

    # Calculate resource allocation based on degree and demand
    best_solution = {}

    for node in nodes:
        code = node['Code']
        infra_type = node_infrastructure_type[code]

        # Initialize the best solution for this node
        best_solution[code] = {}

        # Check for resource demands dynamically
        demands = [key for key in node.keys() if key.startswith('node_resource_demand')]

        # Determine the degree ratio
        degree_ratio = node_degrees.get(code, 0) / total_degree if total_degree > 0 else 0

        # Allocate resources for each existing demand type
        for demand_key in demands:
            # Get the demand amount
            demand_amount = node[demand_key]

            # Allocate resource based on degree and available total resources
            if infra_type in total_resources:
                allocated_resource = degree_ratio * total_resources[infra_type]
                allocated_resource = min(allocated_resource, demand_amount)  # Ensure allocation does not exceed demand
                # Save allocated resources
                best_solution[code][demand_key] = allocated_resource

    # Write the best solution to a new JSON file
    output_data = {
        "best_solution": best_solution
    }

    with open(output_json_path, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)



    # Update Global_Data.json file to include the new path
    file_paths['facility_importance_using_degree'] = output_json_path
    with open(main_json_path, 'w') as f:
        json.dump(file_paths, f, indent=4)

    return "The facility_importance_using_degree has been saved in Global_Data.json"


