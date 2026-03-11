import sys # trace program execution line-by-line.
import os # handle file paths and locate
import tracemalloc # Tracks how much memory the program uses.
import psutil # To measure system metrics
import time # to measure execution time
import matplotlib.pyplot as plt # to plot graphs

instruction_count = 0  
step = 0 
call_depth = 0 # to track nested function calls

process = psutil.Process(os.getpid()) # to get the process id

# Lists to store graph data
time_points = []
memory_points = []
cpu_points = []
step_points = []

def trace_lines(frame, event, arg): # to trace programe execution line by line
    global instruction_count, step, call_depth #modify global variables

    filename = frame.f_code.co_filename

    if not filename.endswith("user_program.py"):
        return trace_lines

    if event == "call": # to track function calls
        call_depth += 1
        print("   " * call_depth + f"Function Call → {frame.f_code.co_name}")

    elif event == "return": 
        print("   " * call_depth + f"Function Return → {frame.f_code.co_name}")
        call_depth -= 1

    elif event == "line": 
        step += 1
        instruction_count += 1
#Show only simple variables
        user_vars = { 
            k: v for k, v in frame.f_locals.items() 
            if isinstance(v, (int, float, str, bool))  
        } 

        print(f"Step {step} → Line {frame.f_lineno}")
        print("   Variables:", user_vars)
        print("-" * 45)

        # Collect data for graphs
        current_time = time.time() - start_time
        current_memory = process.memory_info().rss
        current_cpu = psutil.cpu_percent(interval=None)

        time_points.append(current_time)
        memory_points.append(current_memory)
        cpu_points.append(current_cpu)
        step_points.append(step)

    return trace_lines


print("===== PROGRAM EXECUTION START =====\n")

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "user_program.py") 

with open(file_path, "r") as f:
    code = f.read()

# Start measurements
tracemalloc.start() 
start_time = time.time() 
sys.settrace(trace_lines)

exec(compile(code, file_path, 'exec')) 

sys.settrace(None)
end_time = time.time()

# Memory usage
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

# Real system metrics
cpu_usage = psutil.cpu_percent(interval=0.1)
ram_usage = psutil.virtual_memory().percent
process_memory = process.memory_info().rss

execution_time = end_time - start_time

print("\n===== PROGRAM EXECUTION END =====")
print("Total CPU Steps:", instruction_count)
print("Peak Memory Usage (bytes):", peak)
print("Process Memory Usage (bytes):", process_memory)
print("CPU Usage (%):", cpu_usage)
print("RAM Usage (%):", ram_usage)
print("Execution Time (seconds):", execution_time)

# -----------------------
# GRAPHS
# -----------------------

plt.figure(figsize=(10, 8))

# Memory graph
plt.subplot(3,1,1)
plt.plot(time_points, memory_points)
plt.title("Memory Usage Over Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Memory (bytes)")

# CPU graph
plt.subplot(3,1,2)
plt.plot(time_points, cpu_points)
plt.title("CPU Usage Over Time")
plt.xlabel("Time (seconds)")
plt.ylabel("CPU (%)")

# Step graph
plt.subplot(3,1,3)
plt.plot(time_points, step_points)
plt.title("Execution Steps Over Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Step Count")

plt.tight_layout()
plt.show()