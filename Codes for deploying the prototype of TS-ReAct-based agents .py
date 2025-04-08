import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import subprocess

def select_file(entry):
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def run_script(command, text_output):
    text_output.insert(tk.END, "\n[INFO] Script running...\n")
    root.update()

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)

    for line in iter(process.stdout.readline, ''):
        text_output.insert(tk.END, line)
        text_output.see(tk.END)
        root.update()

    process.stdout.close()
    process.wait()

    text_output.insert(tk.END, "\n[INFO] Execution completed!\n")
    text_output.see(tk.END)
    root.update()

def clear_console(text_output):
    text_output.delete(1.0, tk.END)

def resize_logo(image_path, width):
    image = Image.open(image_path)
    aspect_ratio = image.height / image.width
    new_height = int(width * aspect_ratio)
    image = image.resize((width, new_height), Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(image)

def toggle_api_visibility():
    if entry_api_plan.cget('show') == '*':
        entry_api_plan.config(show='')
        toggle_button.config(text="Hide Key")
    else:
        entry_api_plan.config(show='*')
        toggle_button.config(text="Show Key")

def open_update_tool():
    update_window = tk.Toplevel(root)
    update_window.title("Tool Updating Interface")
    update_window.geometry("500x1000")

    # Tool Path Uploading Section
    tool_path_frame = tk.LabelFrame(update_window, text="Tool Path Uploading", font=("Arial", 14, "bold"), fg="blue", bd=2, relief="solid")
    tool_path_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(tool_path_frame, text="Please fill in the path of tool's function (.py):", font=("Arial", 12)).pack(pady=5)
    entry_tool_path = tk.Entry(tool_path_frame, width=80)
    entry_tool_path.pack(pady=5)

    def browse_py_file():
        file_path = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file_path:
            entry_tool_path.delete(0, tk.END)
            entry_tool_path.insert(0, file_path)

    tk.Button(tool_path_frame, text="Browse", command=browse_py_file, font=("Arial", 12), bg="#DEDEDE", fg="black").pack(pady=5)

    tk.Label(tool_path_frame, text="Please fill in the name of tool's function:", font=("Arial", 12)).pack(pady=5)
    entry_tool_function = tk.Entry(tool_path_frame, width=80)
    entry_tool_function.pack(pady=5)

    # Tool Description Filling Section
    tool_desc_frame = tk.LabelFrame(update_window, text="Tool Description Filling", font=("Arial", 14, "bold"), fg="blue", bd=2, relief="solid")
    tool_desc_frame.pack(fill=tk.X, padx=10, pady=10)

    def create_labeled_entry(parent, label_text):
        tk.Label(parent, text=label_text, font=("Arial", 12)).pack(pady=5)
        entry = tk.Entry(parent, width=80)
        entry.pack(pady=5)
        return entry

    entry_purpose = create_labeled_entry(tool_desc_frame, "Purpose of the tool:")
    entry_input = create_labeled_entry(tool_desc_frame, "Input of the tool:")
    entry_output = create_labeled_entry(tool_desc_frame, "Output of the tool:")
    entry_outcome = create_labeled_entry(tool_desc_frame, "Effect of using the tool:")

    # Tool Graph Updating Section
    tool_graph_frame = tk.LabelFrame(update_window, text="Tool Graph Updating", font=("Arial", 14, "bold"), fg="blue", bd=2, relief="solid")
    tool_graph_frame.pack(fill=tk.X, padx=10, pady=10)

    tk.Label(tool_graph_frame, text="Please upload the updated tool graph (.json):", font=("Arial", 12)).pack(pady=5)
    entry_tool_graph = tk.Entry(tool_graph_frame, width=80)
    entry_tool_graph.pack(pady=5)

    def browse_json_file():
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            entry_tool_graph.delete(0, tk.END)
            entry_tool_graph.insert(0, file_path)

    tk.Button(tool_graph_frame, text="Browse", command=browse_json_file, font=("Arial", 12), bg="#DEDEDE", fg="black").pack(pady=5)

    # Update Tool Function
    def update_tool():
        tool_path = entry_tool_path.get()
        tool_function = entry_tool_function.get()
        purpose = entry_purpose.get()
        tool_input = entry_input.get()
        tool_output = entry_output.get()
        outcome = entry_outcome.get()
        tool_graph = entry_tool_graph.get()

        import_statement = f"from {tool_function} import {tool_function}\n"
        tool_definition = (
            f"{tool_function}_tool = Tool.from_function(\n"
            f'    name="{tool_function}",\n'
            f'    func={tool_function},\n'
            f'    description="{purpose} {tool_input} {tool_output} {outcome}"\n'
            ")\n"
        )

        try:
            with open("main-ReAct-Agent.py", "r") as f:
                lines = f.readlines()
            lines.insert(319, import_statement + tool_definition)
            with open("main-ReAct-Agent.py", "w") as f:
                f.writelines(lines)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update main-ReAct-Agent.py: {e}")
            return

        try:
            with open("C:\\Users\\86131\\Desktop\\shelby_new_Hongyu\\tool_graph_to_chunks.py", "r") as f:
                lines = f.readlines()
            with open("C:\\Users\\86131\\Desktop\\shelby_new_Hongyu\\tool_graph_to_chunks.py", "w") as f:
                for line in lines:
                    if line.strip() == "input_json_file = ' '  # Input JSON file with tool relationships":
                        f.write(f"input_json_file = '{tool_graph}'  # Input JSON file with tool relationships\n")
                    else:
                        f.write(line)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update tool_graph_to_chunks.py: {e}")
            return

        messagebox.showinfo("Update Successful", "The tool has been updated successfully!")

    # Update Tool Button (Align with LabelFrames)
    update_button = tk.Button(update_window, text="Add this tool to the tookit", command=update_tool,
                              font=("Arial", 12, "bold"), bg="#0000FF", fg="white")
    update_button.pack(fill=tk.X, padx=10, pady=30)  # fill=tk.X


# Create main window
root = tk.Tk()
root.title("Python Script Runner")
root.geometry("850x800")
root.configure(bg="#f0f0f0")

# Load and resize logo
try:
    logo = resize_logo("IINlogo.png", 850)
    logo_label = tk.Label(root, image=logo, bg="#f0f0f0")
    logo_label.pack(pady=10)
except Exception as e:
    print("Error loading image:", e)

# Create two frames to split UI
right_frame = tk.Frame(root, width=400, bg="#f0f0f0")
right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
left_frame = tk.Frame(root, width=400, bg="#f0f0f0")
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

### Right Frame: Executive Agent ###
tk.Label(right_frame, text="Reasoning and Action (ReAct) Agent", font=("Arial", 18, "bold"), fg="#A02B93", bg="#f0f0f0").pack()

# Set Parameters Section
set_params_exec_frame = tk.LabelFrame(right_frame, text="Set Parameters", font=("Arial", 12, "bold"), bg="#f0f0f0", bd=2, relief="solid")
set_params_exec_frame.pack(fill=tk.X, pady=10)

# LLM model selection
llm_var_exec = tk.StringVar()
tk.Label(set_params_exec_frame, text="Please select the based LLM:", font=("Arial", 12), bg="#f0f0f0").pack(anchor="w")
llm_dropdown_exec = ttk.Combobox(set_params_exec_frame, textvariable=llm_var_exec, values=["gpt-4", "gpt-4o", "gpt-3.5 Turbo"], state="readonly", font=("Arial", 10))
llm_dropdown_exec.pack(fill=tk.X, pady=5)
llm_dropdown_exec.current(0)

# Temperature
tk.Label(set_params_exec_frame, text="Please set temperature of based LLM (0-1):", font=("Arial", 12), bg="#f0f0f0").pack(anchor="w")
entry_temp_exec = tk.Entry(set_params_exec_frame, width=50, font=("Arial", 10))
entry_temp_exec.pack(fill=tk.X, pady=5)
# Running Process Section
running_exec_frame = tk.LabelFrame(
    right_frame, text="Running Process of The ReAct Agent",
    font=("Arial", 12, "bold"), bg="#f0f0f0", bd=2, relief="solid"
)
running_exec_frame.pack(fill=tk.BOTH, expand=True, pady=20)

# Run button
tk.Button(
    running_exec_frame, text="Run ReAct Agent",
    command=lambda: run_script(
        ["python", "C:\\Users\\86131\\Desktop\\shelby_new_Hongyu\\main-ReAct-Agent.py"],
        text_output_exec
    ),
    font=("Arial", 12, "bold"), bg="#A02B93", fg="white"
).pack(fill=tk.X, pady=5)

# Console output
text_output_exec = tk.Text(running_exec_frame, width=60, height=19, font=("Arial", 10))
text_output_exec.pack(fill=tk.BOTH, pady=5)

tk.Button(
    running_exec_frame, text="Clear Output",
    command=lambda: clear_console(text_output_exec),
    font=("Arial", 12), bg="#DEDEDE", fg="black"
).pack(fill=tk.X, pady=5)

# Tool Updating
tool_updating_button = tk.Button(
    right_frame, text="Update IIN Recovery Toolkit (optional)",
    command=open_update_tool,
    font=("Arial", 14, "bold"), bg="#0000FF", fg="white"
)
tool_updating_button.pack(fill=tk.X, pady=10, anchor="s")



### Left Frame: Planning Agent ###
tk.Label(left_frame, text="Tool Selection (TS) Agent", font=("Arial", 18, "bold"), fg="#47D45A", bg="#f0f0f0").pack()

# Task Input Section
task_input_frame = tk.LabelFrame(left_frame, text="Task Input", font=("Arial", 12, "bold"), bg="#f0f0f0", bd=2, relief="solid")
task_input_frame.pack(fill=tk.X, pady=10)

tk.Label(task_input_frame, text="Please fill in the task for agents to response:", font=("Arial", 12), bg="#f0f0f0").pack(anchor="w")
entry_task_input = tk.Text(task_input_frame, width=50, height=5, font=("Arial", 10))
entry_task_input.pack(fill=tk.X, pady=5)

# Set Parameters Section
set_params_frame = tk.LabelFrame(left_frame, text="Set Parameters", font=("Arial", 12, "bold"), bg="#f0f0f0", bd=2, relief="solid")
set_params_frame.pack(fill=tk.X, pady=10)

tk.Label(set_params_frame, text="Please select the based LLM:", font=("Arial", 12), bg="#f0f0f0").pack(anchor="w")
llm_var_plan = tk.StringVar()
llm_dropdown_plan = ttk.Combobox(set_params_frame, textvariable=llm_var_plan, values=["gpt-4", "gpt-4o", "gpt-3.5 Turbo"], state="readonly", font=("Arial", 10))
llm_dropdown_plan.pack(fill=tk.X, pady=5)
llm_dropdown_plan.current(0)

tk.Label(set_params_frame, text="Please fill in your OpenAI API key:", font=("Arial", 12), bg="#f0f0f0").pack(anchor="w")
api_frame = tk.Frame(set_params_frame, bg="#f0f0f0")
api_frame.pack(fill=tk.X, pady=5)
entry_api_plan = tk.Entry(api_frame, width=40, show="*", font=("Arial", 10))
entry_api_plan.pack(side=tk.LEFT, padx=5)
toggle_button = tk.Button(api_frame, text="Show key", command=toggle_api_visibility, font=("Arial", 12), bg="#DEDEDE", fg="black")
toggle_button.pack(side=tk.RIGHT)

tk.Label(set_params_frame, text="Please set temperature of based LLM (0-1):", font=("Arial", 12), bg="#f0f0f0").pack(anchor="w")
entry_temp_plan = tk.Entry(set_params_frame, width=50, font=("Arial", 10))
entry_temp_plan.pack(fill=tk.X, pady=5)


# Running Process Section
running_process_frame = tk.LabelFrame(left_frame, text="Running Process of The TS Agent", font=("Arial", 12, "bold"), bg="#f0f0f0", bd=2, relief="solid")
running_process_frame.pack(fill=tk.BOTH, expand=True, pady=10)

# Run TS Agent Button
tk.Button(running_process_frame, text="Run TS Agent", command=lambda: run_script(["python", "C:\\Users\\86131\\Desktop\\shelby_new_Hongyu\\main-TS-Agent.py"], text_output_plan), font=("Arial", 12, "bold"), bg="#47D45A", fg="white").pack(fill=tk.X, pady=5)

# Console Output
text_output_plan = tk.Text(running_process_frame, width=60, height=10, font=("Arial", 10))
text_output_plan.pack(fill=tk.BOTH, expand=True, pady=5)

# Clear Output Button
tk.Button(running_process_frame, text="Clear Output", command=lambda: clear_console(text_output_plan), font=("Arial", 12), bg="#DEDEDE", fg="black").pack(fill=tk.X, pady=5)




# Run GUI
root.mainloop()