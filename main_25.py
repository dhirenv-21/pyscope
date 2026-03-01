import sys
import os
import tracemalloc

instruction_count = 0
step = 0

def trace_lines(frame, event, arg):
    global instruction_count, step

    if event == "line":
        if frame.f_code.co_filename.endswith("user_program.py"):
            step += 1
            instruction_count += 1
            print(f"Step {step} → Line {frame.f_lineno}")

    return trace_lines


print("===== PROGRAM EXECUTION START =====\n")

# Get correct path
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "user_program.py")

with open(file_path, "r") as f:
    code = f.read()

# Start memory tracking
tracemalloc.start()

# Start tracing
sys.settrace(trace_lines)

exec(compile(code, file_path, 'exec'))

# Stop tracing
sys.settrace(None)

# Memory usage
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print("\n===== PROGRAM EXECUTION END =====")
print("Total Steps:", instruction_count)
print("Peak Memory Usage (bytes):", peak)