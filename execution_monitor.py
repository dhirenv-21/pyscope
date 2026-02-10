import sys
import tracemalloc

# -------- CPU TRACKING --------
instruction_count = 0
step = 0   # ✅ THIS LINE MUST EXIST



def trace_lines(frame, event, arg):
    global instruction_count, step

    if event == "line":
        step += 1
        instruction_count += 1
        print(f"Step {step} → Executing source line {frame.f_lineno}")

    return trace_lines



# -------- MEMORY TRACKING --------
tracemalloc.start()

# -------- LOAD & RUN REAL PYTHON CODE --------
sys.settrace(trace_lines)

with open("user_program.py") as f:
    code = f.read()
    exec(code)

sys.settrace(None)

# -------- MEMORY RESULTS --------
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print("\n===== EXECUTION SUMMARY =====")
print("Total Lines Executed (CPU Work):", instruction_count)
print("Peak Memory Usage (bytes):", peak)
