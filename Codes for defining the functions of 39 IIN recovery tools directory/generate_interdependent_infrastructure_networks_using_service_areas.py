import json

def generate_interdependent_infrastructure_networks_using_service_areas(input_file):
    input_file = input_file.strip().replace('"', '')

    def find_nearest_service(nodes, target_location, service_type):
        """ Finds the nearest service node that covers the specified location. """
        for node in nodes:
            if node['Infrastructure Type'] == service_type and node.get('Service Area'):
                if target_location in node['Service Area'].split(','):
                    return node['Code']
        return None

    def add_service_edges(nodes, edges, service_type):
        """ Adds edges based on the service type needed. """
        for node in nodes:
            demands = node.get('Demands')
            if demands:  # Check if 'Demands' is not None or empty
                demands = demands.split(', ')
                # print(demands)
                if service_type in demands:
                    target_location = node['Location']
                    service_node_code = find_nearest_service(nodes, target_location, service_type.lower())
                    if service_node_code:
                        edges.append({
                            "Code": f"{service_node_code}_{node['Code']}",
                            "Start": service_node_code,
                            "End": node['Code'],
                            "Infrastructure Type": service_type.lower()
                        })
                    # print(service_node_code)

    """ Processes the network to add new service links based on demands and saves the modified JSON data. """
    with open(input_file, 'r') as file:
        data = json.load(file)
    infrastructure_networks = data['infrastructure_networks']
    with open(infrastructure_networks, 'r') as file:
        json_data = json.load(file)

    nodes = json_data['nodes']
    edges = json_data['edges']

    # Add service edges for Electricity, Gas, and Water
    add_service_edges(nodes, edges, 'power')
    add_service_edges(nodes, edges, 'gas')
    add_service_edges(nodes, edges, 'water')

    # Save the modified network to a new file
    json_data['edges'] = edges
    with open('interdependent_infrastructure_networks.json', 'w') as outfile:
        json.dump(json_data, outfile, indent=4)

    # Update the Global_Data.json to store the path to the new file
    data['interdependent_infrastructure_networks'] = 'interdependent_infrastructure_networks.json'
    with open(input_file, 'w') as outfile:
        json.dump(data, outfile, indent=4)
    return "The path to interdependent infrastructure networks has been saved in Global_data.json"


# Example usage:
# modified_network = generate_interdependent_infrastructure_networks_using_service_areas('Global_Data.json')
# print("The modified network has been saved to 'interdependent_infrastructure_networks.json'.")
