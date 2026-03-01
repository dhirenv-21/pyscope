import sys
import os
import tracemalloc

instruction_count = 0
step = 0
call_depth = 0

def trace_lines(frame, event, arg):
    global instruction_count, step, call_depth

    filename = frame.f_code.co_filename

    # Only trace user_program.py
    if not filename.endswith("user_program.py"):
        return trace_lines

    if event == "call":
        call_depth += 1
        print("   " * call_depth + f"Function Call → {frame.f_code.co_name}")

    elif event == "return":
        print("   " * call_depth + f"Function Return → {frame.f_code.co_name}")
        call_depth -= 1

    elif event == "line":
        step += 1
        instruction_count += 1

        # Filter only user variables (simple types)
        user_vars = {
            k: v for k, v in frame.f_locals.items()
            if isinstance(v, (int, float, str, bool))
        }

        print(f"Step {step} → Line {frame.f_lineno}")
        print("   Variables:", user_vars)
        print("-" * 45)

    return trace_lines


print("===== PROGRAM EXECUTION START =====\n")

# Correct file path
current_dir = os.path.dirname(__file__)
file_path = os.path.join(current_dir, "user_program.py")

with open(file_path, "r") as f:
    code = f.read()

# Start memory tracking
tracemalloc.start()

# Start tracing
sys.settrace(trace_lines)

# Execute user program
exec(compile(code, file_path, 'exec'))

# Stop tracing
sys.settrace(None)

# Get memory usage
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print("\n===== PROGRAM EXECUTION END =====")
print("Total CPU Steps:", instruction_count)
print("Peak Memory Usage (bytes):", peak)