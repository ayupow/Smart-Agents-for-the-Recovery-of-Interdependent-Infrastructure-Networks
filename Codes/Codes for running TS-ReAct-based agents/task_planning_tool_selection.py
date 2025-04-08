import os
import pandas as pd
from docx import Document as DocxDocument
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain_fireworks import ChatFireworks
from langchain.prompts import PromptTemplate
import getpass
from langchain_together import ChatTogether

# Set up environment variables
os.environ["http_proxy"] = "http://localhost:7890"
os.environ["https_proxy"] = "http://localhost:7890"
os.environ["OPENAI_API_KEY"] = "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"
os.environ["TOGETHER_API_KEY"] = "0190b5cb32a8aaeb0cf6d27421315fbbfe6fafd90a46866d18400fb217090364"
os.environ["FIREWORKS_API_KEY"] = "fw_3ZMHggoiEU71VjRVJargnpYB"

# Define candidate tool names
candidate_tool_names = ["""
    convert_shpfile_to_network_tool,
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
    recovery_strategy_of_population_by_SA_tool,
    recovery_strategy_of_GSCC_by_SA,
    recovery_strategy_of_GSCC_by_GA,
    recovery_order_of_population_and_minimum_cost_by_GA_tool,
    recovery_order_of_population_and_minimum_cost_by_SA_tool,
    recovery_order_of_population_and_minimum_cost_and_time_by_GA_tool
    recovery_order_of_population_and_minimum_cost_and_time_by_SA_tool
    recovery_order_of_mixed_integer_linear_programming_time_tool
    network_resilience_evaluation_by_connectivily_tool,
    network_resilience_evaluation_by_average_path_length_tool,
    network_resilience_evaluation_by_node_reachability_tool,
    network_resilience_evaluation_by_diameter_tool,
    network_resilience_assessment_by_global_network_efficiency_tool,
    network_recovery_resilience_assessment_of_betweenness_centrality_tool,
    network_recovery_resilience_assessment_of_kshell_tool,
    network_recovery_resilience_assessment_of_pagerank_tool,
    network_recovery_resilience_assessment_of_katz_centrality_tool,
    network_recovery_resilience_assessment_of_degree_centrality_tool,
    network_recovery_resilience_assessment_of_closeness_centrality_tool,
    post_disaster_network_temporary_recovery_evaluated_by_efficiency_tool,
    post_disaster_network_temporary_recovery_evaluated_by_connectivity_tool,
    post_disaster_network_temporary_recovery_evaluated_by_population_tool
    """
]

# Define the LLM model
llm = ChatOpenAI(
    openai_api_key=os.environ["OPENAI_API_KEY"],
    temperature=0,
    model_name='gpt-4o')

# llm = ChatTogether(model="meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",temperature=0,max_tokens=None,timeout=None,)
# llm = ChatFireworks(
#     model="accounts/fireworks/models/deepseek-v3",
#     temperature=0,
#     max_tokens=None,
# )

# Prompt for task planning: Ensure each step uses one of the candidate tools
task_planning_prompt = PromptTemplate(
    input_variables=["context", "question", "tool_list"],
    template="""Based on the following context and the question, plan the task in detailed steps. Each step must involve using one tool sourced from [candidate_tool_names].

    Context:
    {context}

    Question: {question}

    Candidate Tools:
    {tool_list}

    Task Plan:
    (1) First, convert shapefile into networks.
    (2) Second, generate_interdependent_infrastructure_networks using_service_areas.
    (3) Third, measure_facility_importance_using_degree_centrality
    ...
    """
)

# Prompt for identifying relevant tools: Format output as requested
tools_prompt = PromptTemplate(
    input_variables=["context", "question", "tool_list"],
    template="""
    
    Given the following context, the question, and the list of candidate tools, identify the tools that are likely to be used.

    Context:
    {context}

    Question:
    {question}

    Candidate Tools:
    {tool_list}

    Relevant Tools (you can only output the exact names, the whole name of each tool, and nothing but the name, separated by commas between two tool names):
    One example output for you: 
    
    convert_shpfile_to_network_tool, 
    generate_interdependent_infrastrcuture_networks_using_service_areas_tool, 
    measure_facility_importance_using_pagerank_tool, 
    cascading_failure_identification_by_big_nodes_attacks_tool, 
    post_disaster_network_optimization_by_backup_nodes_tool
    
    
    """
)

# Task Planning & Tool Selection Tool
def task_planning_tool_selection(input_excel):
    input_excel='question_with_retrieved_chunks.xlsx'
    """
    This tool performs task planning and tool selection for each question based on the RAG results.

    :param input_excel: Path to the Excel file containing questions and retrieved chunks.
    :return: DataFrame with task plans, relevant tools, and retrieved chunks.
    """
    # Load the input Excel file (questions and retrieved chunks)
    input_df = pd.read_excel(input_excel)

    # Prepare the output DataFrame
    output_df = pd.DataFrame(columns=["questions", "task_plan", "relevant_tools", "retrieved_chunks"])

    # Process each question in the input DataFrame
    for index, row in input_df.iterrows():
        user_question = row["question"]
        context = row["retrieved_chunk_1"] + "\n\n" + row["retrieved_chunk_2"] + "\n\n" + row["retrieved_chunk_3"]

        # **First LLM Call: Task Planning**
        task_plan_prompt = task_planning_prompt.format(
            context=context,
            question=user_question,
            tool_list=", ".join([f'"{tool}"' for tool in candidate_tool_names])  # Include tools with quotes
        )

        # Generate the task plan using the LLM
        task_plan = llm.invoke(task_plan_prompt).content.strip()

        # **Second LLM Call: Tool Selection**
        tools_prompt_formatted = tools_prompt.format(
            context=context,
            question=user_question,
            tool_list=", ".join([f'"{tool}"' for tool in candidate_tool_names])  # Include tools with quotes
        )

        # Select relevant tools based on the task plan
        relevant_tools = llm.invoke(tools_prompt_formatted).content.strip()

        # Add results to the output dataframe
        output_df = output_df.append({
            "questions": user_question,
            "task_plan": task_plan,
            "relevant_tools": relevant_tools,
            "retrieved_chunks": context
        }, ignore_index=True)

    # Save the output to an Excel file
    output_file_path = "Task_Plan_gpt-4o_question4UI.xlsx"
    output_df.to_excel(output_file_path, index=False)

    print(f"Task planning and tool selection results saved to {output_file_path}")
    return output_file_path

