"""
PyScope — Execution Engine
===========================
Handles code execution with step-level tracing, resource profiling,
variable tracking, call stack construction, and safety features.
"""

import sys
import os
import io
import time
import threading
import subprocess
import tracemalloc
import traceback

import psutil
import matplotlib
matplotlib.use("Agg")

# ── Optional GPU libraries ──────────────────────────────────────────────────
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

_cached_gpu_name = None
_cached_gpu_usage = None         # (value, timestamp)
_GPU_USAGE_CACHE_TTL = 5.0       # seconds

# ── Safety constants ────────────────────────────────────────────────────────
MAX_STEPS = 10_000          # Prevent infinite loops
DEFAULT_TIMEOUT = 10        # Seconds before execution is killed

# Allowed built-ins (exclude dangerous ones)
_SAFE_BUILTINS = {
    k: v for k, v in __builtins__.__dict__.items()
    if k not in {
        "exit", "quit", "exec", "eval", "compile",
        "__import__", "open", "input", "breakpoint",
        "globals", "locals",
    }
} if isinstance(__builtins__, type(sys)) else {
    k: v for k, v in __builtins__.items()
    if k not in {
        "exit", "quit", "exec", "eval", "compile",
        "__import__", "open", "input", "breakpoint",
        "globals", "locals",
    }
}
# Re-add print (captured via stdout redirect)
_SAFE_BUILTINS["print"] = print
# Allow range, len, etc.
for _fn_name in ["range", "len", "int", "float", "str", "bool", "list",
                  "dict", "tuple", "set", "sorted", "reversed", "enumerate",
                  "zip", "map", "filter", "sum", "min", "max", "abs",
                  "round", "repr", "type", "isinstance", "hasattr",
                  "getattr", "setattr", "chr", "ord", "hex", "bin",
                  "all", "any", "format", "iter", "next", "pow",
                  "divmod", "hash", "id", "callable", "super", "object",
                  "staticmethod", "classmethod", "property",
                  "Exception", "ValueError", "TypeError", "KeyError",
                  "IndexError", "AttributeError", "RuntimeError",
                  "StopIteration", "ZeroDivisionError", "OverflowError",
                  "NotImplementedError", "NameError", "IOError",
                  "True", "False", "None"]:
    if _fn_name in dir(__builtins__) if isinstance(__builtins__, type(sys)) else _fn_name in __builtins__:
        try:
            _SAFE_BUILTINS[_fn_name] = getattr(__builtins__, _fn_name) if isinstance(__builtins__, type(sys)) else __builtins__[_fn_name]
        except (KeyError, AttributeError):
            pass


# ─────────────────────────────────────────────────────────────────────────────
# GPU DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def _detect_gpu_name() -> str:
    """Detect GPU name using GPUtil → WMI → PowerShell fallback chain."""
    global _cached_gpu_name
    if _cached_gpu_name is not None:
        return _cached_gpu_name

    if GPU_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                _cached_gpu_name = gpus[0].name
                return _cached_gpu_name
        except Exception:
            pass

    if WMI_AVAILABLE:
        try:
            cards = _wmi_obj.query(
                "SELECT Name, AdapterRAM FROM Win32_VideoController"
            )
            if cards:
                _cached_gpu_name = cards[0].Name
                return _cached_gpu_name
        except Exception:
            pass

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-CimInstance Win32_VideoController | Select-Object -First 1).Name"],
            capture_output=True, text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        name = result.stdout.strip()
        if name:
            _cached_gpu_name = name
            return _cached_gpu_name
    except Exception:
        pass

    _cached_gpu_name = "Unknown GPU"
    return _cached_gpu_name


def get_gpu_usage() -> float:
    """Returns GPU usage % via GPUtil → WMI perf counters → PowerShell, with caching."""
    global _cached_gpu_usage
    import time as _time

    # Return cached value if still fresh
    if _cached_gpu_usage is not None:
        val, ts = _cached_gpu_usage
        if _time.time() - ts < _GPU_USAGE_CACHE_TTL:
            return val

    result = _get_gpu_usage_uncached()
    _cached_gpu_usage = (result, _time.time())
    return result


def _get_gpu_usage_uncached() -> float:
    """Actual GPU usage query (expensive)."""
    if GPU_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                return gpus[0].load * 100
        except Exception:
            pass

    if WMI_AVAILABLE:
        try:
            items = _wmi_obj.query(
                "SELECT UtilizationPercentage "
                "FROM Win32_PerfFormattedData_GPUPerformanceCounters_GPUEngine"
            )
            if items:
                vals = [int(i.UtilizationPercentage) for i in items
                        if i.UtilizationPercentage is not None]
                return max(vals) if vals else 0.0
        except Exception:
            pass

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Counter '\\GPU Engine(*)\\Utilization Percentage' "
             "-ErrorAction SilentlyContinue).CounterSamples | "
             "Sort-Object CookedValue -Descending | "
             "Select-Object -First 1 -ExpandProperty CookedValue"],
            capture_output=True, text=True, timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        val = result.stdout.strip()
        if val:
            return float(val)
    except Exception:
        pass

    return 0.0


def get_gpu_info() -> tuple:
    """Returns (gpu_name, gpu_mem_used_MB, gpu_mem_total_MB)."""
    gpu_name = _detect_gpu_name()
    gpu_mem_used = 0
    gpu_mem_total = 0

    if GPU_AVAILABLE:
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_mem_used = gpus[0].memoryUsed
                gpu_mem_total = gpus[0].memoryTotal
        except Exception:
            pass

    if gpu_mem_total == 0 and WMI_AVAILABLE:
        try:
            cards = _wmi_obj.query(
                "SELECT AdapterRAM FROM Win32_VideoController"
            )
            if cards and cards[0].AdapterRAM:
                gpu_mem_total = int(cards[0].AdapterRAM) // (1024 * 1024)
        except Exception:
            pass

    return gpu_name, gpu_mem_used, gpu_mem_total


# ─────────────────────────────────────────────────────────────────────────────
# SAFE VALUE FORMATTING
# ─────────────────────────────────────────────────────────────────────────────
def _safe_repr(value, max_len: int = 100) -> str:
    """Safely represent any value, truncating to max_len."""
    try:
        r = repr(value)
        if len(r) > max_len:
            return r[:max_len - 3] + "..."
        return r
    except Exception:
        return "<unrepresentable>"


def _get_type_name(value) -> str:
    """Get a clean type name for variable display."""
    t = type(value).__name__
    if isinstance(value, (list, tuple, set, frozenset)):
        return f"{t}[{len(value)}]"
    elif isinstance(value, dict):
        return f"dict[{len(value)}]"
    elif isinstance(value, str):
        return f"str[{len(value)}]"
    return t


# ─────────────────────────────────────────────────────────────────────────────
# EXECUTION ENGINE
# ─────────────────────────────────────────────────────────────────────────────
class ExecutionTimeoutError(Exception):
    """Raised when code execution exceeds the time limit."""
    pass


class StepLimitError(Exception):
    """Raised when code execution exceeds the step limit."""
    pass


def run_code(code_str: str, timeout: int = DEFAULT_TIMEOUT,
             max_steps: int = MAX_STEPS) -> dict:
    """
    Execute code_str with step-level tracing and resource profiling.

    Returns a dict with:
        logs, stdout_lines, stats, time_points, memory_points,
        cpu_points, gpu_points, step_points, call_tree,
        variables_timeline, error
    """
    logs = []
    step_counter = [0]
    call_depth = [0]
    max_depth = [0]

    # Resource tracking over time
    time_points = []
    memory_points = []
    cpu_points = []
    gpu_points = []
    step_points = []

    # Variable timeline: list of (step, {name: {"value": ..., "type": ...}})
    variables_timeline = []

    # Call tree construction
    call_stack = []  # stack of {"name": ..., "children": [], "return_value": None}
    call_tree = []   # top-level roots

    stdout_capture = io.StringIO()
    process = psutil.Process(os.getpid())
    start_time = [None]
    aborted = [False]
    abort_reason = [""]
    last_gpu_pct = [0.0]       # Cache GPU reading (sampled outside tracer)

    def tracer(frame, event, arg):
        if aborted[0]:
            return None

        if frame.f_code.co_filename != "<user_code>":
            return tracer

        elapsed = time.perf_counter() - start_time[0]

        if event == "call":
            call_depth[0] += 1
            max_depth[0] = max(max_depth[0], call_depth[0])

            node = {
                "name": frame.f_code.co_name,
                "line": frame.f_lineno,
                "children": [],
                "return_value": None,
            }

            if call_stack:
                call_stack[-1]["children"].append(node)
            else:
                call_tree.append(node)

            call_stack.append(node)

            logs.append({
                "kind": "call", "depth": call_depth[0],
                "name": frame.f_code.co_name,
                "line": frame.f_lineno, "time": elapsed,
            })

        elif event == "return":
            ret_repr = _safe_repr(arg, 80)

            if call_stack:
                call_stack[-1]["return_value"] = ret_repr
                call_stack.pop()

            logs.append({
                "kind": "return", "depth": call_depth[0],
                "name": frame.f_code.co_name,
                "value": ret_repr,
                "line": frame.f_lineno, "time": elapsed,
            })
            call_depth[0] = max(0, call_depth[0] - 1)

        elif event == "line":
            step_counter[0] += 1

            # Check step limit
            if step_counter[0] > max_steps:
                aborted[0] = True
                abort_reason[0] = (
                    f"Execution stopped: exceeded {max_steps:,} steps. "
                    "Possible infinite loop detected."
                )
                raise StepLimitError(abort_reason[0])

            # Lightweight resource sampling (only on line events)
            mem_rss = process.memory_info().rss
            cpu_pct = psutil.cpu_percent(interval=None)
            gpu_pct = last_gpu_pct[0]

            # Capture ALL variable types (not just primitives)
            user_vars = {}
            for k, v in frame.f_locals.items():
                if k.startswith("__"):
                    continue
                user_vars[k] = {
                    "value": _safe_repr(v),
                    "type": _get_type_name(v),
                }

            # Simplified vars for log display (primitives only, string format)
            simple_vars = {
                k: info["value"]
                for k, info in user_vars.items()
                if info["type"] in ("int", "float", "str", "bool", "NoneType")
                   or info["type"].startswith("str[")
            }

            logs.append({
                "kind": "line", "step": step_counter[0],
                "line": frame.f_lineno, "vars": simple_vars,
                "time": elapsed,
            })

            variables_timeline.append({
                "step": step_counter[0],
                "line": frame.f_lineno,
                "vars": user_vars,
            })

            time_points.append(round(elapsed, 6))
            memory_points.append(mem_rss)
            cpu_points.append(cpu_pct)
            gpu_points.append(gpu_pct)
            step_points.append(step_counter[0])

        return tracer

    # ── Execute with timeout ────────────────────────────────────────────
    # Pre-sample GPU before tracing (the call is too slow to use mid-trace)
    last_gpu_pct[0] = get_gpu_usage()

    tracemalloc.start()
    start_time[0] = time.perf_counter()
    error_msg = ""
    timed_out = False

    def _exec_target():
        nonlocal error_msg
        try:
            compiled = compile(code_str, "<user_code>", "exec")
            old_stdout = sys.stdout
            sys.stdout = stdout_capture
            sys.settrace(tracer)
            exec(compiled, {"__name__": "__main__", "__builtins__": _SAFE_BUILTINS})
            sys.settrace(None)
            sys.stdout = old_stdout
        except StepLimitError:
            sys.settrace(None)
            sys.stdout = sys.__stdout__
            error_msg = abort_reason[0]
        except Exception:
            sys.settrace(None)
            sys.stdout = sys.__stdout__
            error_msg = traceback.format_exc()

    exec_thread = threading.Thread(target=_exec_target, daemon=True)
    exec_thread.start()
    exec_thread.join(timeout=timeout)

    if exec_thread.is_alive():
        aborted[0] = True
        abort_reason[0] = (
            f"Execution timed out after {timeout} seconds. "
            "The program was terminated."
        )
        timed_out = True
        error_msg = abort_reason[0]
        # Give thread a moment to notice the abort flag
        exec_thread.join(timeout=0.5)

    # Restore stdout safety
    sys.settrace(None)
    if sys.stdout != sys.__stdout__:
        sys.stdout = sys.__stdout__

    end_time = time.perf_counter()
    try:
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
    except Exception:
        peak_mem = 0

    execution_time = end_time - start_time[0]
    cpu_final = psutil.cpu_percent(interval=0.05)
    gpu_final = get_gpu_usage()
    ram_pct = psutil.virtual_memory().percent
    gpu_name, gpu_mem_used, gpu_mem_total = get_gpu_info()

    stats = {
        "total_steps": step_counter[0],
        "execution_time": execution_time,
        "peak_memory_kb": peak_mem / 1024,
        "cpu_percent": cpu_final,
        "ram_percent": ram_pct,
        "gpu_percent": gpu_final,
        "gpu_name": gpu_name,
        "gpu_mem_used": gpu_mem_used,
        "gpu_mem_total": gpu_mem_total,
        "max_call_depth": max_depth[0],
        "timed_out": timed_out,
        "step_limit_hit": step_counter[0] >= max_steps,
    }

    return {
        "logs": logs,
        "stdout_lines": stdout_capture.getvalue().splitlines(),
        "stats": stats,
        "time_points": time_points,
        "memory_points": [m / 1024 for m in memory_points],
        "cpu_points": cpu_points,
        "gpu_points": gpu_points,
        "step_points": step_points,
        "call_tree": call_tree,
        "variables_timeline": variables_timeline,
        "error": error_msg,
    }
