from langchain.agents import Tool, initialize_agent, AgentType
from langchain_openai import ChatOpenAI
import os
from langchain.prompts import PromptTemplate
from tool_graph_to_chunks import tool_graph_to_chunks
from RAG import RAG
from task_planning_tool_selection import task_planning_tool_selection

# 设置OpenAI API密钥
# os.environ["http_proxy"] = "http://localhost:7890"
# os.environ["https_proxy"] = "http://localhost:7890"

import warnings

# 忽略弃用警告
warnings.filterwarnings("ignore", category=DeprecationWarning)

os.environ["OPENAI_API_KEY"] = "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"

# os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "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")
# llm = ChatOpenAI(
#     openai_api_key=os.environ["OPENAI_API_KEY"],
#     temperature=float(os.environ.get("TEMPERATURE", 0)),  # 读取温度
#     model_name=os.environ.get("MODEL_NAME", "gpt-4o")  # 读取 LLM 选择
# )

llm = ChatOpenAI(
    openai_api_key=os.environ["OPENAI_API_KEY"],
    temperature=0,
    model_name='gpt-4o'
)

# 创建工具实例
tool_graph_to_chunks_tool = Tool.from_function(
    name="tool_graph_to_chunks",
    func=tool_graph_to_chunks,
    description="This tool is used to converting tool graph to knowledge chunks, it read the tool_relationship_json as input and output the tool_chunks.docx. If it runs, you can see a generated file named tool_chunks.docx")
RAG_tool = Tool.from_function(
    name="RAG",
    func=RAG,
    description="This tool is used to retrieving knowledge chunks to each question, it read the tool_description04_docx as input and output the question_with_retrieved_chunks_xlsx. If it runs, you can see a generated file named question_with_retrieved_chunks.xlsx")
task_planning_tool_selection_tool = Tool.from_function(
    name="task_planning_tool_selection",
    func=task_planning_tool_selection,
    description="This tool is used to planning and selection, it read the question_with_retrieved_chunks_xlsx as input and output the Doubel_agent_three_matched_LLMs_Plan_GPT4o_versionR1_minus_original.xlsx. If it runs, you can see a generated output file")

tools = [tool_graph_to_chunks_tool,
         RAG_tool,
         task_planning_tool_selection_tool
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
    3. Before all actions begin, you need to first plan the overall execution steps to complete the task. A suggested overall execution step for solving the tasks is:
    (1) Firstly, tool_graph_to_chunks using tool_graph_to_chunks_tool,
    (2) Secondly, RAG using RAG_tool,
    (3) Finnaly, task_planning_tool_selection using task_planning_tool_selection_tool

    Begin!
    Thought: {agent_scratchpad}"""
    )

# 初始化代理
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    prompt=prompt_template
)

# 使用代理运行任务
response = agent("Please read the questions and output the results using provided three tools")
# Query examples in each category:

# measure facility: Please use the shpfile information in Global_Data.json and finally output the facility_importance_using_pagerank
# Designing the recovery strategy: Please use the shpfile information in Global_Data.json and finally output the best recovery sequence, including which ones to repair every day and the clustering coefficient of network as the program evaluation indicators.
# Assessing IIN resilience:Please use the shpfile information in Global_Data.json and finally output the global network efficiency evaluation under ramdom attacks
# post-disaster optimization: Please use the shpfile information in Global_Data.json and finally output a file showing the network performance changes after backing up new nodes after inputing file of attacking top 5 pagerank nodes.

print(response)
