

## ⚠️ Important Notice ⚠️
## __As the paper is under review, all contents in this repository are currently not permitted for reuse by anyone until this announcement is removed. Thank you for your understanding! 🙏__

## 0. Videos of agents operation

### 0.1 Operation of the developed prototype

↓↓↓ A snippet of using the **developed prototype** to run the TS-ReAct-based agents driven by GPT-4o

https://github.com/user-attachments/assets/a79ed28e-a42a-4bc7-8c49-fa07a2e0df50

↓↓↓ A snippet of **updating the tool kit in the prototype**

https://github.com/user-attachments/assets/310db01b-bbd3-462c-945c-60fbf6867e14

The full video to showcase the prototype and tool kit updating can be found in: https://github.com/ayupow/Smart-Agents-for-the-Recovery-of-Interdependent-Infrastructure-Networks/blob/dc852aa1b25333338bf60541742478caf6d58be8/Videos/Operation%20of%20the%20TS-ReAct%20agent%20prototype.mp4

### 0.2 Operation of agents based on ReAct pattern

↓↓↓ A snippet of running the **ReAct-based agents driven by GPT-4o, GPT-4, and GPT-3.5 Turbo**.

https://github.com/user-attachments/assets/9cf85f36-af04-480f-bbde-e37f10f18738

The full video can be found here (https://github.com/ayupow/Smart-Agents-for-the-Recovery-of-Interdependent-Infrastructure-Networks/blob/dc852aa1b25333338bf60541742478caf6d58be8/Videos/Operations%20of%20agents%20based%20on%20ReAct%20pattern/ReAct-based%20agents%20driven%20by%20GPT-4o%2C%20GPT-4%2C%20and%20GPT-3.5%20Turbo.mp4)
 
↓↓↓ A snippet of running the **ReAct-based agents driven by Qwen2.5, Deepseek-V3, Gemma-2, Llama-3.1, and Mixtral MoE**.

https://github.com/user-attachments/assets/3f849a87-8716-4c5d-b26d-61c32f97b54e

The full video can be found here (https://github.com/ayupow/Smart-Agents-for-the-Recovery-of-Interdependent-Infrastructure-Networks/blob/dc852aa1b25333338bf60541742478caf6d58be8/Videos/Operations%20of%20agents%20based%20on%20ReAct%20pattern/ReAct-based%20agents%20driven%20by%20Qwen2.5%2C%20Deepseek-V3%2C%20Gemma-2%2C%20Llama-3.1%2C%20and%20Mixtral%20MoE.mp4)

### 0.3 Operation of agents based on TS-ReAct pattern

↓↓↓ A snippet of running the **TS agent based on TS-ReAct pattern**. 

https://github.com/user-attachments/assets/710dad92-1f76-4e51-84bd-471268bc73bb

The full video can be found here (https://github.com/ayupow/Smart-Agents-for-the-Recovery-of-Interdependent-Infrastructure-Networks/blob/dc852aa1b25333338bf60541742478caf6d58be8/Videos/Operations%20of%20agents%20based%20on%20TS-ReAct%20pattern/TS-ReAct-based-ReAct-agent.mp4)

↓↓↓ A snippet of running the **ReAct agent based on TS-ReAct pattern**. 

https://github.com/user-attachments/assets/2ba0f564-1b8a-412e-92bf-dd5e7bb09ad6

The full video can be found here (https://github.com/ayupow/Smart-Agents-for-the-Recovery-of-Interdependent-Infrastructure-Networks/blob/dc852aa1b25333338bf60541742478caf6d58be8/Videos/Operations%20of%20agents%20based%20on%20TS-ReAct%20pattern/TS-ReAct-based-TS-agent.mp4)

## 1. Introduction
### 1.1 Objective 
This repository aims at providing the codes and data regarding the paper entitled “……” for the public, and it is developed by XXX University in China, XXX university in US, and XXX university of HongKong in HK SAR.
### 1.2 Acknowledgements
We greatly appreciate the selfless spirits of these voluntary contributors of a series of open python libraries, including LangChain-Agent (https://github.com/LangChain-OpenTutorial/LangChain-OpenTutorial/tree/main/15-Agent), LangChain-RAG (https://github.com/LangChain-OpenTutorial/LangChain-OpenTutorial/tree/main/12-RAG), MTEB leaderboard (https://huggingface.co/spaces/mteb/leaderboard), some base works in general purpose LLM development (https://huggingface.co/google/gemma-2-27b-it, https://huggingface.co/spaces/llamameta/llama3.1-405B, https://huggingface.co/Qwen, and so on). Our work stands on the shoulders of these giants.
### 1.3 Copyright
As for anything regarding the copyright, please refer to the MIT License or contact the authors.

## 2. Summary of supplemental materials
This table below shows all supplemental materials. All sheets in Tables S1-S4 are arranged in the order shown in this table.

<img width="1245" height="747" alt="image" src="https://github.com/user-attachments/assets/1fd0c74b-13fc-439d-806d-181dec9ae466" />

## 3 Reuse ths repository
### 3.1 Import defined IIN recovery tools
Prior to executing the agents, please move the code files for defining the functions of the 39 IIN recovery tools—originally located in the directory **{Codes for defining the functions of 45 IIN recovery tools}**—into the target directory **{Codes for running ReAct-based agents}** or **{Codes for running TS-ReAct-based agents}**, depending on the specific agent to be used.

↓↓↓ All codes for defining the tool functions could be found below.

![Image](https://github.com/user-attachments/assets/f5edf27c-d541-4571-9ec4-349a43f1a188)

Subsequently, please import the functions into your scripts as demonstrated in the following image.

![Image](https://github.com/user-attachments/assets/2bb562ec-6377-41da-8393-3a57a2ca6481)

### 3.2 Reuse of the codes to operate the agents based on ReAct pattern
↓↓↓ Codes for running the agents based on ReAct pattern driven by 8 LLMs.

![Image](https://github.com/user-attachments/assets/049ba853-593b-4cab-a5e7-6d1a8d35a923)

### 3.3 Reuse of the codes to operate the agents based on TS-ReAct pattern
↓↓↓ Codes for running the agents based on TS-ReAct pattern driven by 8 LLMs.

![Image](https://github.com/user-attachments/assets/5f0b06e6-a6a8-49fb-a0b5-260131b7f628)

### 3.4 Reuse of the codes to operate the prototype and update the tool kit
↓↓↓ Codes for running the prototype of TS-ReAct-based agents and updating the tool kit.

![Image](https://github.com/user-attachments/assets/763d8d30-7d3b-4324-87eb-05f7c917babe)





