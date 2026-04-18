import sys
import os
import tracemalloc
import psutil
import time
import matplotlib.pyplot as plt
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

try:
    import wmi
    _wmi_obj = wmi.WMI(namespace="root\\cimv2")
    WMI_AVAILABLE = True
except Exception:
    WMI_AVAILABLE = False

def get_gpu_usage():
    """Returns GPU usage % using GPUtil (NVIDIA) or WMI (AMD/Intel)."""
    if GPU_AVAILABLE:
        gpus = GPUtil.getGPUs()
        if gpus:
            return gpus[0].load * 100
    if WMI_AVAILABLE:
        try:
            items = _wmi_obj.query(
                "SELECT Name, UtilizationPercentage FROM Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine"
            )
            if items:
                vals = [int(i.UtilizationPercentage) for i in items
                        if i.UtilizationPercentage is not None]
                return sum(vals) / len(vals) if vals else 0.0
        except Exception:
            pass
    return 0.0

instruction_count = 0
step = 0
call_depth = 0

process = psutil.Process(os.getpid())

time_points = []
memory_points = []
cpu_points = []
gpu_points = []

start_time = None

def trace_lines(frame, event, arg):
    global instruction_count, step, call_depth

    filename = frame.f_code.co_filename
    if not filename.endswith("user_program.py"):
        return trace_lines

    current_time = time.time() - start_time
    current_memory = process.memory_info().rss
    current_cpu = psutil.cpu_percent(interval=None)

    # GPU usage
    current_gpu = get_gpu_usage()

    time_points.append(current_time)
    memory_points.append(current_memory)
    cpu_points.append(current_cpu)
    gpu_points.append(current_gpu)

    if event == "call":
        call_depth += 1
        print("   " * call_depth + f"Function Call → {frame.f_code.co_name}")

    elif event == "return":
        print("   " * call_depth + f"Function Return → {frame.f_code.co_name}")
        call_depth -= 1

    elif event == "line":
        step += 1
        instruction_count += 1

        user_vars = {
            k: v for k, v in frame.f_locals.items()
            if isinstance(v, (int, float, str, bool))
        }

        print(f"Step {step} → Line {frame.f_lineno}")
        print("   Variables:", user_vars)
        print("-" * 50)

    return trace_lines


print("===== PROGRAM EXECUTION START =====\n")

current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "user_program.py")

with open(file_path, "r") as f:
    code = f.read()

tracemalloc.start()
start_time = time.time()

sys.settrace(trace_lines)
exec(compile(code, file_path, 'exec'))
sys.settrace(None)

end_time = time.time()

current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

execution_time = end_time - start_time

cpu_usage = psutil.cpu_percent(interval=0.1)
ram_usage = psutil.virtual_memory().percent
process_memory = process.memory_info().rss

# Final GPU snapshot
gpu_usage = get_gpu_usage()
gpu_memory_used = 0
gpu_memory_total = 0
gpu_name = "Unknown GPU"

if GPU_AVAILABLE:
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu_memory_used = gpus[0].memoryUsed
        gpu_memory_total = gpus[0].memoryTotal
        gpu_name = gpus[0].name

if gpu_name == "Unknown GPU" and WMI_AVAILABLE:
    try:
        video_cards = _wmi_obj.query("SELECT Name FROM Win32_VideoController")
        if video_cards:
            gpu_name = video_cards[0].Name
    except Exception:
        pass

print("\n===== PROGRAM EXECUTION END =====")
print("Total CPU Steps:", instruction_count)
print("Peak Memory Usage (bytes):", peak)
print("Process Memory Usage (bytes):", process_memory)
print("CPU Usage (%):", cpu_usage)
print("RAM Usage (%):", ram_usage)
print("Execution Time (seconds):", execution_time)
print(f"GPU Name: {gpu_name}")
print(f"GPU Usage (%): {gpu_usage:.1f}")
print(f"GPU Memory Used (MB): {gpu_memory_used}")
print(f"GPU Memory Total (MB): {gpu_memory_total}")

plt.figure(figsize=(12, 10))

# 1. Memory Graph
plt.subplot(4, 1, 1)
plt.plot(time_points, memory_points, color='steelblue')
plt.title("Memory Usage Over Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Memory (bytes)")

# 2. CPU Graph
plt.subplot(4, 1, 2)
plt.plot(time_points, cpu_points, color='darkorange')
plt.title("CPU Usage Over Time")
plt.xlabel("Time (seconds)")
plt.ylabel("CPU (%)")

# 3. GPU Graph
plt.subplot(4, 1, 3)
plt.plot(time_points, gpu_points, color='mediumseagreen')
plt.title(f"GPU Usage Over Time ({gpu_name})")
plt.xlabel("Time (seconds)")
plt.ylabel("GPU (%)")

# 4. Steps Graph
plt.subplot(4, 1, 4)
plt.plot(time_points, range(len(time_points)), color='mediumpurple')
plt.title("Execution Steps Over Time")
plt.xlabel("Time (seconds)")
plt.ylabel("Step Count")

plt.tight_layout()
plt.show()