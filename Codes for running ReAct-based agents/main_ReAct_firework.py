import pandas as pd
from langchain.agents import Tool, initialize_agent, AgentType

from langchain_fireworks import ChatFireworks
import os
import io
import sys
from langchain.prompts import PromptTemplate
from convert_shpfile_to_network import convert_shpfile_to_network
from generate_interdependent_infrastructure_networks_using_service_areas import generate_interdependent_infrastructure_networks_using_service_areas
from measure_facility_importance_using_degree_centrality import measure_facility_importance_using_degree_centrality
from measure_facility_importance_using_betweenness_centrality import measure_facility_importance_using_betweenness_centrality
from measure_facility_importance_using_closeness_centrality import measure_facility_importance_using_closeness_centrality
from measure_facility_importance_using_kshell import measure_facility_importance_using_kshell
from measure_facility_importance_using_pagerank import measure_facility_importance_using_pagerank
from measure_facility_importance_using_katz_centrality import measure_facility_importance_using_katz_centrality
from recovery_strategy_of_degree_centrality import recovery_strategy_of_degree_centrality
from recovery_strategy_of_kshell import recovery_strategy_of_kshell
from recovery_strategy_of_pagerank import recovery_strategy_of_pagerank
from recovery_strategy_of_betweenness_centrality import recovery_strategy_of_betweenness_centrality
from recovery_strategy_of_closeness_centrality import recovery_strategy_of_closeness_centrality
from recovery_strategy_of_GSCC_by_GA import recovery_strategy_of_GSCC_by_GA
from recovery_strategy_of_GSCC_by_SA import recovery_strategy_of_GSCC_by_SA
from recovery_strategy_of_katz_centrality import recovery_strategy_of_katz_centrality
from recovery_order_of_population_by_GA import recovery_order_of_population_by_GA
from recovery_order_of_mixed_integer_linear_programming_time import recovery_order_of_mixed_integer_linear_programming_time
from recovery_strategy_of_population_by_SA import recovery_strategy_of_population_by_SA
from cascading_failure_identification_by_big_nodes_attacks import cascading_failure_identification_by_big_nodes_attacks
from network_assessment_by_connectivily import network_assessment_by_connectivily
from network_assessment_by_average_path_length import network_assessment_by_average_path_length
from network_assessment_by_diameter import network_assessment_by_diameter
from network_assessment_by_global_network_efficiency import \
    network_assessment_by_global_network_efficiency
from network_assessment_of_betweenness_centrality import \
    network_assessment_of_betweenness_centrality
from network_assessment_by_node_reachability import network_assessment_by_node_reachability
from network_assessment_of_katz_centrality import \
    network_assessment_of_katz_centrality
from network_assessment_of_closeness_centrality import \
    network_assessment_of_closeness_centrality
from network_assessment_of_degree_centrality import \
    network_assessment_of_degree_centrality
from network_assessment_of_kshell import network_assessment_of_kshell
from network_assessment_of_pagerank import network_assessment_of_pagerank
from post_disaster_network_temporary_recovery_evaluated_by_population import post_disaster_network_temporary_recovery_evaluated_by_population
from post_disaster_network_temporary_recovery_evaluated_by_efficiency import post_disaster_network_temporary_recovery_evaluated_by_efficiency
from post_disaster_network_temporary_recovery_evaluated_by_connectivity import post_disaster_network_temporary_recovery_evaluated_by_connectivity
from resource_allocation_by_population import resource_allocation_by_population
from resource_allocation_by_time import resource_allocation_by_time
from resource_allocation_by_cost import resource_allocation_by_cost
from resource_allocation_by_clustering_coefficient import resource_allocation_by_clustering_coefficient

os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"

import warnings

# 忽略弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

os.environ["FIREWORKS_API_KEY"] = " " #fill in  your API key of firework AI
llm_1 = ChatFireworks(
    model="accounts/fireworks/models/gemma2-9b-it",
    temperature=0,
    # max_tokens=4096,
)

# accounts/fireworks/models/gemma2-9b-it
llm_2 = ChatFireworks(
model="accounts/fireworks/models/llama-v3p1-405b-instruct",
    temperature=0,
    # max_tokens=4096,
)
# accounts/fireworks/models/llama-v3p1-405b-instruct
llm_3 = ChatFireworks(
model="accounts/fireworks/models/qwen2p5-72b-instruct",
    temperature=0,
    # max_tokens=4096,
)

# accounts/fireworks/models/gemma2-9b-it
llm_4 = ChatFireworks(
model="accounts/fireworks/models/deepseek-v3",
    temperature=0,
    # max_tokens=4096,
)
# accounts/fireworks/models/llama-v3p1-405b-instruct
llm_5 = ChatFireworks(
model="accounts/fireworks/models/mixtral-8x22b-instruct",
    temperature=0,
    # max_tokens=4096,
)

# accounts/fireworks/models/qwen2p5-72b-instruct
# 创建工具实例
convert_shpfile_to_network_tool = Tool.from_function(
    name="convert_shpfile_to_network",
    func=convert_shpfile_to_network,
    description="This tool is to convert shapefile into networks and save the networks. It reads the shpfile information from Global_Data.jso as input and output the network information, as well as observing network information in Global_Data.json. If this function is run, you could observe the network information path in Global_Data.json "
)

generate_interdependent_infrastrcuture_networks_using_service_areas_tool = Tool.from_function(
    name="generate_interdependent_infrastructure_networks_using_service_areas",
    func=generate_interdependent_infrastructure_networks_using_service_areas,
    description="This tool is to generate interdependent infrastructure networks using_service_areas. It reads the network information from Global_Data.json as input and output the interdependent infrastructure network, as well as save interdependent infrastructure networ in Global_Data.json. If this function is run, you could observe the interdependent network information path in Global_Data.json"
)
measure_facility_importance_using_degree_centrality_tool = Tool.from_function(
    name="measure_facility_importance_using_degree_centrality",
    func=measure_facility_importance_using_degree_centrality,
    description="This tool is to measure facility importance using degree centrality. It reads the interdependent infrastructure network from Global_Data.json as input and output facility importance using degree centrality, as well as save the degree-centrality-based facility importance in Global_Data.json. If this function is run, you could observe the facility degree centrality information path in Global_Data.json"
)
measure_facility_importance_using_pagerank_tool = Tool.from_function(
    name="measure_facility_importance_using_pagerank",
    func=measure_facility_importance_using_pagerank,
    description="This tool is to measure facility importance using pagerank. It reads the interdependent infrastructure network from Global_Data.json as input and output facility importance using pagerank, as well as save the pagerank-based facility importance in Global_Data.json. If this function is run, you could observe the facility pagerank information path in Global_Data.json"
)
measure_facility_importance_using_kshell_tool = Tool.from_function(
    name="measure_facility_importance_using_kshell",
    func=measure_facility_importance_using_kshell,
    description="This tool is to measure facility importance using kshell. It reads the interdependent infrastructure network from Global_Data.json as input and output facility importance using kshell, as well as save the kshell-based facility importance in Global_Data.json. If this function is run, you could observe the facility kshell information path in Global_Data.json"
)
measure_facility_importance_using_betweenness_centrality_tool = Tool.from_function(
    name="measure_facility_importance_using_betweenness_centrality",
    func=measure_facility_importance_using_betweenness_centrality,
    description="This tool is to measure facility importance using betweenness centrality. It reads the interdependent infrastructure network from Global_Data.json as input and output facility importance using betweenness centrality, as well as save the betweenness centrality-based facility importance in Global_Data.json. If this function is run, you could observe the facility betweenness centrality information path in Global_Data.json"
)
measure_facility_importance_using_closeness_centrality_tool = Tool.from_function(
    name="measure_facility_importance_using_closeness_centrality",
    func=measure_facility_importance_using_closeness_centrality,
    description="This tool is to measure facility importance using closeness centrality. It reads the interdependent infrastructure network from Global_Data.json as input and output facility importance using closeness centrality, as well as save the closeness centrality-based facility importance in Global_Data.json. If this function is run, you could observe the facility closeness centrality information path in Global_Data.json"
)

measure_facility_importance_using_katz_centrality_tool = Tool.from_function(
    name="measure_facility_importance_using_katz_centrality",
    func=measure_facility_importance_using_katz_centrality,
    description="This tool is to measure facility importance using katz centrality. It reads the interdependent infrastructure network from Global_Data.json as input and output facility importance using katz centrality, as well as save the katz centrality-based facility importance in Global_Data.json. If this function is run, you could observe the facility closeness centrality information path in Global_Data.json"
)

cascading_failure_identification_by_big_nodes_attacks_tool = Tool.from_function(
    name="cascading_failure_identification_by_big_nodes_attacks",
    func=cascading_failure_identification_by_big_nodes_attacks,
    description="This tool is to simulate cascading failures in interdependent directed networks under big nods-targeted attacks."
                "It reads the facilities importance from Global_Data.json as input. "
                "It outputs the affected facilities due to cascading failures and the interdependent infrastructure networks with cascading failures. "
                "If this function is run, you could observe the pathes of affected facilities due to cascading failures and the interdependent infrastructure networks with cascading failures in Global_Data.json"
)

recovery_strategy_of_betweenness_centrality_tool = Tool.from_function(
    name="recovery_strategy_of_betweenness_centrality",
    func=recovery_strategy_of_betweenness_centrality,
    description="This tool generates a recovery strategy for interdependent infrastructure networks based on betweenness centrality. It reads the global data file to access the necessary input files, including the network topology, facility importance based on betweenness centrality, and failure information. The function prioritizes the restoration of failed nodes and their associated edges based on their betweenness centrality values. The recovery plan is outputted to recovery_strategy_of_betweenness_centrality.json, and the path to this output file is updated in the global data file. If the function is run, the restoration strategy for failed nodes will be generated and saved as specified.")

recovery_strategy_of_degree_centrality_tool = Tool.from_function(
    name="recovery_strategy_of_degree_centrality",
    func=recovery_strategy_of_degree_centrality,
    description="This tool generates a recovery strategy for interdependent infrastructure networks based on degree centrality. It reads the global data file to access the necessary input files, including the network topology, facility importance based on degree centrality, and failure information. The function prioritizes the restoration of failed nodes and their associated edges based on their degree centrality values. The recovery plan is outputted to recovery_strategy_of_degree_centrality.json, and the path to this output file is updated in the global data file. If the function is run, the restoration strategy for failed nodes will be generated and saved as specified.")

recovery_strategy_of_kshell_tool = Tool.from_function(
    name="recovery_strategy_of_kshell",
    func=recovery_strategy_of_kshell,
    description="This tool generates a recovery strategy for interdependent infrastructure networks based on kshell. It reads the global data file to access the necessary input files, including the network topology, facility importance based on kshell, and failure information. The function prioritizes the restoration of failed nodes and their associated edges based on their kshell values. The recovery plan is outputted to recovery_strategy_of_kshell.json, and the path to this output file is updated in the global data file. If the function is run, the restoration strategy for failed nodes will be generated and saved as specified.")

recovery_strategy_of_closeness_centrality_tool = Tool.from_function(
    name="recovery_strategy_of_closeness_centrality",
    func=recovery_strategy_of_closeness_centrality,
    description="This tool generates a recovery strategy for interdependent infrastructure networks based on closeness_centrality. It reads the global data file to access the necessary input files, including the network topology, facility importance based on closeness_centrality, and failure information. The function prioritizes the restoration of failed nodes and their associated edges based on their closeness_centrality values. The recovery plan is outputted to recovery_strategy_of_closeness_centrality.json, and the path to this output file is updated in the global data file. If the function is run, the restoration strategy for failed nodes will be generated and saved as specified.")

recovery_strategy_of_pagerank_tool = Tool.from_function(
    name="recovery_strategy_of_pagerank",
    func=recovery_strategy_of_pagerank,
    description="This tool generates a recovery strategy for interdependent infrastructure networks based on closeness_centrality. It reads the global data file to access the necessary input files, including the network topology, facility importance based on pagerank, and failure information. The function prioritizes the restoration of failed nodes and their associated edges based on their pagerank values. The recovery plan is outputted to recovery_strategy_of_pagerank.json, and the path to this output file is updated in the global data file. If the function is run, the restoration strategy for failed nodes will be generated and saved as specified.")
recovery_strategy_of_katz_centrality_tool = Tool.from_function(
    name="recovery_strategy_of_katz_centrality",
    func=recovery_strategy_of_katz_centrality,
    description="This tool generates a recovery strategy for interdependent infrastructure networks based on katz_centrality. It reads the global data file to access the necessary input files, including the network topology, facility importance based on katz, and failure information. The function prioritizes the restoration of failed nodes and their associated edges based on their katz values. The recovery plan is outputted to recovery_strategy_of_katz.json, and the path to this output file is updated in the global data file. If the function is run, the restoration strategy for failed nodes will be generated and saved as specified.")

recovery_order_of_population_by_GA_tool = Tool.from_function(
    name="recovery_order_of_population_by_GA",
    func=recovery_order_of_population_by_GA,
    description="This tool generates a recovery strategy for infrastructure networks using a Genetic Algorithm based on the populations. It reads the network information from interdependent_infrastructure_networks. json and the population data from population_data. json as referenced in Global_Data. json, along with the list of failed nodes from cascading_failure_identification_under_big_nodes_attacks. json as input. It outputs the recovery strategy to recovery_strategy_of_population_by_GA. json and saved in Global_Data.json. If this function is running, you can observe the recovery strategy file path in Global_Data.json.")

recovery_strategy_of_GSCC_by_GA = Tool.from_function(
    name="recovery_strategy_of_GSCC_by_GA",
    func=recovery_strategy_of_GSCC_by_GA,
    description="This tool generates a recovery strategy for infrastructure networks using a Genetic Algorithm based on the size of the GSCC. It reads the network information from interdependent_infrastructure_networks.json referenced in Global_Data.json and the failed nodes list from cascading_failure_identification_under_big_nodes_attacks.json as input. It outputs the recovery strategy in recovery_strategy_of_GSCC_by_GA.json and saved in Global_Data.json. If this function is running, you can observe the recovery strategy file path in Global_Data.json.")

recovery_strategy_of_population_by_SA_tool = Tool.from_function(
    name="recovery_strategy_of_population_by_SA",
    func=recovery_strategy_of_population_by_SA,
    description="This tool generates a recovery strategy for infrastructure networks using a Simulated Annealing based on the populations. It reads the network information from interdependent_infrastructure_networks. json and the population data from population_data. json as referenced in Global_Data. json, along with the list of failed nodes from cascading_failure_identification_under_big_nodes_attacks.json.  It outpouts the recovery strategy is outputted to recovery_strategy_of_population_by_SA. json and saved in Global_Data.json.  If this function is running, you can observe the recovery strategy file path in Global_Data.json.")
recovery_strategy_of_GSCC_by_SA = Tool.from_function(
    name="recovery_strategy_of_GSCC_by_SA",
    func=recovery_strategy_of_GSCC_by_SA,
    description="This tool generates a recovery strategy for infrastructure networks using Simulated Annealing based on the size of the GSCC. It reads the network information from interdependent_infrastructure_networks.json referenced in Global_Data.json and the failed nodes list from cascading_failure_identification_under_big_nodes_attacks.json as input. It outputs the recovery strategy in recovery_strategy_of_GSCC_by_SA.json and saved in Global_Data.json. If this function is running, you can observe the recovery strategy file path in Global_Data.json.")

recovery_order_of_mixed_integer_linear_programming_time_tool = Tool.from_function(
    name="recovery_order_of_mixed_integer_linear_programming_time",
    func=recovery_order_of_mixed_integer_linear_programming_time,
    description="This tool utilizes a Mixed-Integer Linear Programming (MILP) algorithm to compute the total recovery time of failed nodes in IIN for minimizing the total recovery time,. It reads the network, failure, and resource constraint data from `Global_Data.json`. The recovery plan is created by evaluating solutions based on their feasibility under resource constraints.The tool simulates recovery day by day, reintroducing nodes into the graph and recalculating the average clustering coefficient after each recovery step. It outputs detailed daily recovery data, including recovered nodes, restored areas, and clustering coefficient values, to `recovery_order_of_mixed_integer_linear_programming_time.json`. The path to the output is updated in `Global_Data.json`.Running this function provides insight into recovery strategies, balancing resource allocation and network resilience."
)

network_assessment_by_node_reachability_tool = Tool.from_function(
    name="network_assessment_by_node_reachability",
    func=network_assessment_by_node_reachability,
    description="This tool is to evaluate the interdependent directed networks by_node_reachability under ramdom attacks."
                "It reads the interdependent infrastructure network and the failed nodes list from cascading_failure_identification_under_big_nodes_attacks.json from Global_Data.json as input. "
                "It outputs the ratio of the proportion of pairs that can reach each other before and after ramdom attacks"
                "If this function is run, you could observe the path of network_resilience_assessment_by_reachability in Global_Data.json"
)
network_assessment_by_connectivily_tool = Tool.from_function(
    name="network_assessment_by_connectivily",
    func=network_assessment_by_connectivily,
    description="This tool is to evaluate network connectivily in interdependent directed networks under ramdom attacks."
                "It reads the interdependent infrastructure network and the failed nodes list from cascading_failure_identification_under_big_nodes_attacks.json from Global_Data.json as input. "
                "It outputs the the ratio of the proportion of nodes in the largest connected subgraph after removing certain nodes or connections to the proportion of nodes in the largest connected subgraph of the original network.. "
                "If this function is run, you could observe the path of network_resilience_assessment_by_connectivity in Global_Data.json"
)

network_assessment_by_average_path_length_tool = Tool.from_function(
    name="network_assessment_by_average_path_length",
    func=network_assessment_by_average_path_length,
    description="This tool is to evaluate the interdependent directed networks by_average_path_length under ramdom attacks."
                "It reads the interdependent infrastructure network and the failed nodes list from cascading_failure_identification_under_big_nodes_attacks.json from Global_Data.json as input. "
                "It outputs the average path length of the interdependent infrastructure network before and after ramdom attacks"
                "If this function is run, you could observe the path of network_resilience_assessment_by_ave_path_length in Global_Data.json"
)


network_assessment_by_diameter_tool = Tool.from_function(
    name="network_assessment_by_diameter",
    func=network_assessment_by_diameter,
    description="This tool is to evaluate the interdependent directed networks by_node_reachability under ramdom attacks."
                "It reads the interdependent infrastructure network and the failed nodes list from cascading_failure_identification_under_big_nodes_attacks.json from Global_Data.json as input. "
                "It outputs the ratio of the diameter of the largest weakly connected component before and after ramdom attacks"
                "If this function is run, you could observe the path of network_resilience_assessment_by_diameter in Global_Data.json"
)

network_assessment_by_global_network_efficiency_tool = Tool.from_function(
    name="network_assessment_by_global_network_efficiency",
    func=network_assessment_by_global_network_efficiency,
    description="This tool is to evaluate global_network_efficiency of interdependent directed networks under random attacks."
                "It reads the interdependent infrastructure network and the failed nodes list from cascading_failure_identification_under_big_nodes_attacks.json from Global_Data.json as input. "
                "It outputs the global_network_efficiency under random attacks. "
                "If this function is run, you could observe the path of network_resilience_assessment_by_global_network_efficiency in Global_Data.json"
)

network_assessment_of_betweenness_centrality_tool = Tool.from_function(
    name="network_assessment_of_betweenness_centrality",
    func=network_assessment_of_betweenness_centrality,
    description="This tool assesses network recovery resilience by determining the optimal order to restore failed nodes based on their betweenness centrality and evaluating the impact on the restored population. It reads the network information from interdependent_infrastructure_networks. json and the population data from population_data. json as referenced in Global_Data. json, along with the list of failed nodes from cascading_failure_identification_under_big_nodes_attacks.json as input. It outpouts the recovery strategy and evaluation results are saved to network_recovery_resilience_assessment_of_betweenness_centrality. json and Global_Data. json is updated with the path to this file. If this function is running, you can observe the recovery strategy file path in Global_Data. json and view the generated recovery population curve plot.")

network_assessment_of_closeness_centrality_tool = Tool.from_function(
    name="network_assessment_of_closeness_centrality",
    func=network_assessment_of_closeness_centrality,
    description="This tool assesses network recovery resilience by determining the optimal order to restore failed nodes based on their closeness centrality and evaluating the impact on the restored population. It reads the network information from interdependent_infrastructure_networks. json and the population data from population_data. json as referenced in Global_Data. json, along with the list of failed nodes from cascading_failure_identification_under_big_nodes_attacks.json as input. It outpouts the recovery strategy and evaluation results are saved to network_recovery_resilience_assessment_of_closeness_centrality. json and Global_Data. json is updated with the path to this file. If this function is running, you can observe the recovery strategy file path in Global_Data. json and view the generated recovery population curve plot.")

network_assessment_of_degree_centrality_tool = Tool.from_function(
    name="network_assessment_of_degree_centrality",
    func=network_assessment_of_degree_centrality,
    description="This tool assesses network recovery resilience by determining the optimal order to restore failed nodes based on their degree centrality and evaluating the impact on the restored population. It reads the network information from interdependent_infrastructure_networks. json and the population data from population_data. json as referenced in Global_Data. json, along with the list of failed nodes from cascading_failure_identification_under_big_nodes_attacks.json as input. It outpouts the recovery strategy and evaluation results are saved to network_recovery_resilience_assessment_of_degree_centrality. json and Global_Data. json is updated with the path to this file. If this function is running, you can observe the recovery strategy file path in Global_Data. json and view the generated recovery population curve plot.")

network_assessment_of_katz_centrality_tool = Tool.from_function(
    name="network_assessment_of_katz_centrality",
    func=network_assessment_of_katz_centrality,
    description="This tool assesses network recovery resilience by determining the optimal order to restore failed nodes based on their katz centrality and evaluating the impact on the restored population. It reads the network information from interdependent_infrastructure_networks. json and the population data from population_data. json as referenced in Global_Data. json, along with the list of failed nodes from cascading_failure_identification_under_big_nodes_attacks.json as input. It outpouts the recovery strategy and evaluation results are saved to network_recovery_resilience_assessment_of_katz_centrality. json and Global_Data. json is updated with the path to this file. If this function is running, you can observe the recovery strategy file path in Global_Data. json and view the generated recovery population curve plot.")

network_assessment_of_pagerank_tool = Tool.from_function(
    name="network_assessment_of_pageranky",
    func=network_assessment_of_pagerank,
    description="This tool assesses network recovery resilience by determining the optimal order to restore failed nodes based on their PageRank centrality and evaluating the impact on the restored population. It reads the network information from interdependent_infrastructure_networks. json and the population data from population_data. json as referenced in Global_Data. json, along with the list of failed nodes from cascading_failure_identification_under_big_nodes_attacks.json as input. It outpouts the recovery strategy and evaluation results are saved to network_recovery_resilience_assessment_of_PageRank_centrality. json and Global_Data. json is updated with the path to this file. If this function is running, you can observe the recovery strategy file path in Global_Data. json and view the generated recovery population curve plot.")

network_assessment_of_kshell_tool = Tool.from_function(
    name="network_assessment_of_kshell",
    func=network_assessment_of_kshell,
    description="This tool assesses network recovery resilience by determining the optimal order to restore failed nodes based on their kshell centrality and evaluating the impact on the restored population. It reads the network information from interdependent_infrastructure_networks. json and the population data from population_data. json as referenced in Global_Data. json, along with the list of failed nodes from cascading_failure_identification_under_big_nodes_attacks.json as input. It outpouts the recovery strategy and evaluation results are saved to network_recovery_resilience_assessment_of_kshell_centrality. json and Global_Data. json is updated with the path to this file. If this function is running, you can observe the recovery strategy file path in Global_Data. json and view the generated recovery population curve plot.")

post_disaster_network_temporary_recovery_evaluated_by_population_tool = Tool.from_function(
    name="post_disaster_network_temporary_recovery_evaluated_by_population",
    func=post_disaster_network_temporary_recovery_evaluated_by_population,
    description="This tool simulates post-disaster network optimization by generating temporary nodes to restore service to affected areas after a cascading failure. It reads data from `Global_Data.json`, identifies failed nodes and edges based on an attack scenario, and simulates the removal of these elements from the network.The tool analyzes the service areas impacted by the failure and estimates the affected population. It then generates temporary nodes to existing nodes, ensuring that resource constraints are met. The new nodes and edges are designed to help restore services and mitigate the impact of the failure on served population.The results, including failed nodes, backup nodes, restored areas, and updated population impacts, are saved to `Post_disaster_network_temporary_recovery_evaluated_by_population.json`, and the output path is updated in `Global_Data.json`."
)

post_disaster_network_temporary_recovery_evaluated_by_efficiency_tool = Tool.from_function(
    name="post_disaster_network_temporary_recovery_evaluated_by_efficiency",
    func=post_disaster_network_temporary_recovery_evaluated_by_efficiency,
    description="This tool simulates post-disaster network optimization by generating temporary nodes to restore service to affected areas after a cascading failure. It reads data from `Global_Data.json`, identifies failed nodes and edges based on an attack scenario, and simulates the removal of these elements from the network.The tool analyzes the service areas impacted by the failure and estimates the global network efficiency. It then generates temporary nodes to existing nodes, ensuring that resource constraints are met. The new nodes and edges are designed to help restore services and mitigate the impact of the failure on network efficiency.The results, including failed nodes, backup nodes, restored areas, and updated network efficiency, are saved to `Post_disaster_network_temporary_recovery_evaluated_by_efficiency.json`, and the output path is updated in `Global_Data.json`."
)

post_disaster_network_temporary_recovery_evaluated_by_connectivity_tool = Tool.from_function(
    name="post_disaster_network_temporary_recovery_evaluated_by_connectivity",
    func=post_disaster_network_temporary_recovery_evaluated_by_connectivity,
    description="This tool simulates post-disaster network optimization by generating temporary nodes to restore service to affected areas after a cascading failure. It reads data from `Global_Data.json`, identifies failed nodes and edges based on an attack scenario, and simulates the removal of these elements from the network.The tool analyzes the service areas impacted by the failure and estimates the network connectivity. It then generates temporary nodes to existing nodes, ensuring that resource constraints are met. The new nodes and edges are designed to help restore services and mitigate the impact of the failure on network connectivity.The results, including failed nodes, backup nodes, restored areas, and updated network connectivity, are saved to `Post_disaster_network_temporary_recovery_evaluated_by_connectivity.json`, and the output path is updated in `Global_Data.json`."
)

resource_allocation_by_population_tool = Tool.from_function(
   name="resource_allocation_by_population",
    func=resource_allocation_by_population,
    description="This tool calculates the daily resource allocation for each node to maximize the served population. It reads data from Global_Data.json, including interdependent_infrastructure_networks_with_different_resource_demand, cascading_failure_identification_under_random_attacks.json, and resource_constraints_per_day. The tool outputs resource_allocation_by_population.json and stores it in Global_Data.json.If the tool runs successfully, you will observe that resource_allocation_by_population.json has been generated and stored in Global_Data.json.")

resource_allocation_by_time_tool = Tool.from_function(
   name="resource_allocation_by_time",
    func=resource_allocation_by_time,
    description="This tool calculates the daily resource allocation for each node to minimize the time. It reads data from Global_Data.json, including interdependent_infrastructure_networks_with_different_resource_demand, cascading_failure_identification_under_random_attacks.json, and resource_constraints_per_day. The tool outputs resource_allocation_by_time.json and stores it in Global_Data.json.If the tool runs successfully, you will observe that resource_allocation_by_time.json has been generated and stored in Global_Data.json.")

resource_allocation_by_cost_tool = Tool.from_function(
   name="resource_allocation_by_cost",
    func=resource_allocation_by_cost,
    description="This tool calculates the daily resource allocation for each node to minimize the cost. It reads data from Global_Data.json, including interdependent_infrastructure_networks_with_different_resource_demand, cascading_failure_identification_under_random_attacks.json, and resource_constraints_per_day. The tool outputs resource_allocation_by_cost.json and stores it in Global_Data.json.If the tool runs successfully, you will observe that resource_allocation_by_cost.json has been generated and stored in Global_Data.json.")

resource_allocation_by_clustering_coefficient_tool = Tool.from_function(
   name="resource_allocation_by_clustering_coefficient",
    func=resource_allocation_by_clustering_coefficient,
    description="This tool calculates the daily resource allocation for each node based on their clustering coefficient. It reads data from Global_Data.json, including interdependent_infrastructure_networks_with_different_resource_demand, cascading_failure_identification_under_random_attacks.json, and resource_constraints_per_day. The tool outputs resource_allocation_bclustering_coefficient.json and stores it in Global_Data.json.If the tool runs successfully, you will observe that resource_allocation_by_clustering_coefficient.json has been generated and stored in Global_Data.json.")

tools = [convert_shpfile_to_network_tool,
         generate_interdependent_infrastrcuture_networks_using_service_areas_tool,
         cascading_failure_identification_by_big_nodes_attacks_tool,
         measure_facility_importance_using_degree_centrality_tool,
         measure_facility_importance_using_pagerank_tool,
         measure_facility_importance_using_kshell_tool,
         measure_facility_importance_using_betweenness_centrality_tool,
         measure_facility_importance_using_closeness_centrality_tool,
         measure_facility_importance_using_katz_centrality_tool,
         recovery_strategy_of_betweenness_centrality_tool,
         recovery_strategy_of_degree_centrality_tool,
         recovery_strategy_of_closeness_centrality_tool,
         recovery_strategy_of_kshell_tool,
         recovery_strategy_of_pagerank_tool,
         recovery_strategy_of_katz_centrality_tool,
         recovery_order_of_population_by_GA_tool,
        recovery_order_of_mixed_integer_linear_programming_time_tool,
         resource_allocation_by_population_tool,
         resource_allocation_by_time_tool,
         resource_allocation_by_cost_tool,
         resource_allocation_by_clustering_coefficient_tool,
         recovery_strategy_of_population_by_SA_tool,
         recovery_strategy_of_GSCC_by_SA,
         recovery_strategy_of_GSCC_by_GA,
         network_assessment_by_connectivily_tool,
         network_assessment_by_average_path_length_tool,
         network_assessment_by_node_reachability_tool,
         network_assessment_by_diameter_tool,
         network_assessment_by_global_network_efficiency_tool,
         network_assessment_of_betweenness_centrality_tool,
         network_assessment_of_kshell_tool,
         network_assessment_of_pagerank_tool,
         network_assessment_of_katz_centrality_tool,
         network_assessment_of_degree_centrality_tool,
         network_assessment_of_closeness_centrality_tool,
         post_disaster_network_temporary_recovery_evaluated_by_efficiency_tool,
         post_disaster_network_temporary_recovery_evaluated_by_connectivity_tool,
         post_disaster_network_temporary_recovery_evaluated_by_population_tool
         ]

prompt_template = PromptTemplate(
    input_variables=["tools", "tool_names", "input", "agent_scratchpad"],
    template="""
You are an expert in interdependent infrastructure networks, and your task is to solve the problem step by step using the provided tools.
__________________________________________________________________
To solve a task, please use the following format:
Complete format:
Thought: (reflect on your progress and decide what to do next (based on observation if exist), do not skip)
Action: (the action name, should be one of [{tool_names}]. Decide the action based on previous Thought and Observation)
Action Input: (name of a .json file, decide the input based on previous Thought and Observation)
Observation: (the result of the action)
(this process can repeat, and you can only process one task at a time)

OR
Thought: (review original question and check my total process) 
Final Answer: (output the final answer to the original input question based on observation)
__________________________________________________________________

Answer the question below using the following tools: {tools} 
Use the tools provided, and use the most specific tool available for each action. Your final answer should contain all information necessary to answer the question and subquestions.
Question: {input}
__________________________________________________________________
REMEMBER:
1. You can only respond with a single complete "Thought, Action, Action Input, Observation" format OR a single "Final Answer" format.
2. Don't create files that don't exist yourself.

Begin!
Thought: {agent_scratchpad}"""
)

# Initialize agents for each LLM
agent_1 = initialize_agent(
    tools=tools,
    llm=llm_1,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt_template
)

agent_2 = initialize_agent(
    tools=tools,
    llm=llm_2,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt_template
)

agent_3 = initialize_agent(
    tools=tools,
    llm=llm_3,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt_template
)
agent_4 = initialize_agent(
    tools=tools,
    llm=llm_4,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt_template
)

agent_5 = initialize_agent(
    tools=tools,
    llm=llm_5,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt_template
)



def capture_agent_output(agent, query):
    # 重定向stdout以捕获打印输出
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        # 运行代理
        agent(query)
    except Exception as e:
        captured_output.write(f"Error: {e}")

    # 重置stdout
    sys.stdout = sys.__stdout__
    return captured_output.getvalue()


# 读取查询文件 (查询列)
input_file = 'questions_version_R2_minus_version_R1.xlsx'  # 更新为实际文件路径

df = pd.read_excel(input_file)

# 初始化一个新的DataFrame存储结果
responses_logs = pd.DataFrame(columns=["questions",
                                       "Agent_1_Response", "Agent_1_Logs",
                                       "Agent_2_Response", "Agent_2_Logs",
                                       "Agent_3_Response", "Agent_3_Logs",
                                       "Agent_4_Response", "Agent_4_Logs",
                                       "Agent_5_Response", "Agent_5_Logs"
                                       ])

# 输出文件路径
output_file = 'One_agent_result_fireworks_R2_minus_R1.xlsx'

# 逐个处理每个查询
for index, query in enumerate(df['questions']):
    print(f"Processing question {index + 1}: {query}")

    # 为每个代理创建空响应和日志变量
    response_1 = None
    response_2 = None
    response_3 = None
    logs_1 = ""
    logs_2 = ""
    logs_3 = ""

    # 运行Agent 1并捕获其输出
    try:
        print(f"Running Agent 1 for query: {query}")
        logs_1 = capture_agent_output(agent_1, query)
        response_1 = "Finished"
    except Exception as e:
        response_1 = f"Failed: {e}"

    # 运行Agent 2并捕获其输出
    try:
        print(f"Running Agent 2 for query: {query}")
        logs_2 = capture_agent_output(agent_2, query)
        response_2 = "Finished"
    except Exception as e:
        response_2 = f"Failed: {e}"

    # 运行Agent 3并捕获其输出
    try:
        print(f"Running Agent 3 for query: {query}")
        logs_3 = capture_agent_output(agent_3, query)
        response_3 = "Finished"
    except Exception as e:
        response_3 = f"Failed: {e}"

    try:
        print(f"Running Agent 4 for query: {query}")
        logs_4 = capture_agent_output(agent_4, query)
        response_4 = "Finished"
    except Exception as e:
        response_4 = f"Failed: {e}"

    try:
        print(f"Running Agent 5 for query: {query}")
        logs_5 = capture_agent_output(agent_5, query)
        response_5 = "Finished"
    except Exception as e:
        response_5 = f"Failed: {e}"

    # 将结果和日志写入到DataFrame
    responses_logs.at[index, 'query'] = query
    responses_logs.at[index, 'Agent_1_Response'] = response_1
    responses_logs.at[index, 'Agent_2_Response'] = response_2
    responses_logs.at[index, 'Agent_3_Response'] = response_3
    responses_logs.at[index, 'Agent_4_Response'] = response_4
    responses_logs.at[index, 'Agent_5_Response'] = response_5

    responses_logs.at[index, 'Agent_1_Logs'] = logs_1
    responses_logs.at[index, 'Agent_2_Logs'] = logs_2
    responses_logs.at[index, 'Agent_3_Logs'] = logs_3
    responses_logs.at[index, 'Agent_4_Logs'] = logs_4
    responses_logs.at[index, 'Agent_5_Logs'] = logs_5

    # 打印日志以进行验证
    print(f"Agent 1 Logs:\n{logs_1}")
    print(f"Agent 2 Logs:\n{logs_2}")
    print(f"Agent 3 Logs:\n{logs_3}")
    print(f"Agent 4 Logs:\n{logs_4}")
    print(f"Agent 5 Logs:\n{logs_5}")

    # 立即将结果写入Excel文件
    with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
        responses_logs.to_excel(writer, index=False)
    print(f"Logs written to {output_file} after processing query {index + 1}")

print("All queries processed and logs have been written.")
# 用
