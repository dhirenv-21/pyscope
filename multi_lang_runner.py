"""
PyScope — Multi-Language Runner
================================
Execute Python, C, C++, Java, and JavaScript code via subprocess.
Returns a result dict compatible with the Python execution engine output.

Includes pre-flight compiler/runtime detection so we give clear
"install X" messages instead of cryptic WinError 2 crashes.
"""

import os
import re
import glob
import time
import shutil
import functools
import subprocess
import tempfile

import psutil

from execution_engine import run_code as run_python_code, get_gpu_usage, get_gpu_info


# ─────────────────────────────────────────────────────────────────────────────
# PATH REFRESH (Windows)  — pick up compilers installed after app launch
# ─────────────────────────────────────────────────────────────────────────────
if os.name == "nt":
    try:
        import winreg
        _machine_path = ""
        _user_path = ""
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
                _machine_path = winreg.QueryValueEx(key, "Path")[0]
        except OSError:
            pass
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                _user_path = winreg.QueryValueEx(key, "Path")[0]
        except OSError:
            pass
        if _machine_path or _user_path:
            os.environ["PATH"] = _machine_path + ";" + _user_path
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_TIMEOUT = 5  # seconds (user-requested limit)
SUPPORTED_LANGUAGES = ["Python", "C", "C++", "Java", "JavaScript"]

# Workspace-local temp dir (avoid system /tmp)
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMP_ROOT = os.path.join(_PROJECT_DIR, "__pyscope_temp__")

_IS_WINDOWS = os.name == "nt"


# ─────────────────────────────────────────────────────────────────────────────
# EXECUTABLE LOOKUP — env overrides → JAVA_HOME → PATH → known install dirs
# ─────────────────────────────────────────────────────────────────────────────
@functools.lru_cache(maxsize=32)
def _find_executable(name: str) -> str | None:
    """Locate `name` even when it isn't on PATH (common on Windows)."""
    if name in ("javac", "java"):
        java_home = os.environ.get("JAVA_HOME", "").strip().strip('"')
        if java_home:
            cand = os.path.join(
                java_home, "bin",
                f"{name}.exe" if _IS_WINDOWS else name,
            )
            if os.path.isfile(cand):
                return cand

    env_var = {"gcc": "CC", "g++": "CXX", "node": "NODE"}.get(name)
    if env_var:
        override = os.environ.get(env_var, "").strip().strip('"')
        if override and os.path.isfile(override):
            return override

    found = shutil.which(name)
    if found:
        return found

    if not _IS_WINDOWS:
        return None

    exe = f"{name}.exe"
    patterns: list[str] = []

    if name in ("gcc", "g++"):
        patterns = [
            rf"C:\msys64\mingw64\bin\{exe}",
            rf"C:\msys64\ucrt64\bin\{exe}",
            rf"C:\msys64\clang64\bin\{exe}",
            rf"C:\MinGW\bin\{exe}",
            rf"C:\TDM-GCC-64\bin\{exe}",
            rf"C:\Strawberry\c\bin\{exe}",
            rf"C:\cygwin64\bin\{exe}",
            rf"C:\cygwin\bin\{exe}",
            rf"C:\Program Files\mingw-w64\*\mingw64\bin\{exe}",
            rf"C:\Program Files (x86)\mingw-w64\*\mingw64\bin\{exe}",
            rf"C:\Program Files\CodeBlocks\MinGW\bin\{exe}",
            rf"C:\Program Files (x86)\CodeBlocks\MinGW\bin\{exe}",
            rf"C:\Program Files\LLVM\bin\{exe}",
        ]
    elif name in ("javac", "java"):
        patterns = [
            rf"C:\Program Files\Java\jdk*\bin\{exe}",
            rf"C:\Program Files (x86)\Java\jdk*\bin\{exe}",
            rf"C:\Program Files\Eclipse Adoptium\jdk-*\bin\{exe}",
            rf"C:\Program Files\Microsoft\jdk-*\bin\{exe}",
            rf"C:\Program Files\Amazon Corretto\jdk*\bin\{exe}",
            rf"C:\Program Files\Zulu\zulu-*\bin\{exe}",
            rf"C:\Program Files\BellSoft\LibericaJDK-*\bin\{exe}",
            rf"C:\Program Files\Java\jre*\bin\{exe}",
        ]
    elif name == "node":
        patterns = [
            rf"C:\Program Files\nodejs\{exe}",
            rf"C:\Program Files (x86)\nodejs\{exe}",
            os.path.expandvars(rf"%LOCALAPPDATA%\Programs\nodejs\{exe}"),
            os.path.expandvars(rf"%APPDATA%\npm\{exe}"),
        ]

    for pat in patterns:
        for hit in sorted(glob.glob(pat), reverse=True):
            if os.path.isfile(hit):
                return hit

    return None


def reset_toolchain_cache():
    """Clear cached executable paths (call after the user installs a compiler)."""
    _find_executable.cache_clear()


# ─────────────────────────────────────────────────────────────────────────────
# COMPILER / RUNTIME DETECTION
# ─────────────────────────────────────────────────────────────────────────────
def check_toolchain(language: str) -> str | None:
    """
    Check whether the compiler/runtime for `language` is available.
    Returns None if OK, or a human-readable error string if missing.
    """
    if language == "Python":
        return None

    if language == "C":
        if not _find_executable("gcc"):
            return (
                "C compiler not found.\n"
                "Install MinGW-w64 (or set the CC environment variable to your gcc.exe).\n"
                "  → https://www.mingw-w64.org/"
            )

    elif language == "C++":
        if not _find_executable("g++"):
            return (
                "C++ compiler not found.\n"
                "Install MinGW-w64 (or set the CXX environment variable to your g++.exe).\n"
                "  → https://www.mingw-w64.org/"
            )

    elif language == "Java":
        if not _find_executable("javac"):
            return (
                "Java compiler not found.\n"
                "Install the JDK (or set JAVA_HOME to your JDK install dir).\n"
                "  → https://adoptium.net/"
            )
        if not _find_executable("java"):
            return (
                "Java runtime not found.\n"
                "Install the JDK/JRE (or set JAVA_HOME)."
            )

    elif language == "JavaScript":
        if not _find_executable("node"):
            return (
                "Node.js not found.\n"
                "Install Node.js (or set the NODE environment variable to your node.exe).\n"
                "  → https://nodejs.org/"
            )

    return None


# ─────────────────────────────────────────────────────────────────────────────
# TEMP DIRECTORY MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
def _get_temp_dir() -> str:
    """Create and return a workspace-local temp directory."""
    os.makedirs(_TEMP_ROOT, exist_ok=True)
    return tempfile.mkdtemp(dir=_TEMP_ROOT)


def _cleanup_temp(path: str):
    """Safely remove a temp directory."""
    try:
        if path and os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
    except Exception:
        pass


def cleanup_all_temp():
    """Remove the entire temp root (call on app shutdown)."""
    _cleanup_temp(_TEMP_ROOT)


# ─────────────────────────────────────────────────────────────────────────────
# EMPTY RESULT SKELETON
# ─────────────────────────────────────────────────────────────────────────────
def _empty_result(error: str = "") -> dict:
    """Return a result dict matching the Python engine format."""
    return {
        "logs": [],
        "stdout_lines": [],
        "stats": {
            "total_steps": 0,
            "execution_time": 0,
            "peak_memory_kb": 0,
            "cpu_percent": 0,
            "ram_percent": 0,
            "gpu_percent": 0,
            "gpu_name": "N/A",
            "gpu_mem_used": 0,
            "gpu_mem_total": 0,
            "max_call_depth": 0,
            "timed_out": False,
            "step_limit_hit": False,
            "language": "",
        },
        "time_points": [],
        "memory_points": [],
        "cpu_points": [],
        "gpu_points": [],
        "step_points": [],
        "call_tree": [],
        "variables_timeline": [],
        "error": error,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SUBPROCESS-BASED RUNNER
# ─────────────────────────────────────────────────────────────────────────────
def _run_subprocess(cmd: list, timeout: int = DEFAULT_TIMEOUT,
                    cwd: str = None) -> dict:
    """
    Run a command, capture output, and measure resources.
    Returns {stdout, stderr, returncode, time_s, peak_mem_kb, cpu_pct}.
    """
    process_obj = psutil.Process(os.getpid())
    mem_before = process_obj.memory_info().rss

    start = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        elapsed = time.perf_counter() - start
        mem_after = process_obj.memory_info().rss
        cpu_pct = psutil.cpu_percent(interval=0.05)

        return {
            "stdout": proc.stdout or "",
            "stderr": proc.stderr or "",
            "returncode": proc.returncode,
            "time_s": elapsed,
            "peak_mem_kb": max(0, (mem_after - mem_before)) / 1024,
            "cpu_pct": cpu_pct,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return {
            "stdout": "",
            "stderr": f"Execution timed out after {timeout} seconds.",
            "returncode": -1,
            "time_s": elapsed,
            "peak_mem_kb": 0,
            "cpu_pct": 0,
            "timed_out": True,
        }
    except FileNotFoundError as e:
        return {
            "stdout": "",
            "stderr": f"Compiler/runtime not found: {e}",
            "returncode": -1,
            "time_s": 0,
            "peak_mem_kb": 0,
            "cpu_pct": 0,
            "timed_out": False,
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1,
            "time_s": 0,
            "peak_mem_kb": 0,
            "cpu_pct": 0,
            "timed_out": False,
        }


def _subprocess_to_result(run_info: dict, language: str) -> dict:
    """Convert raw subprocess output into our standard result dict."""
    gpu_usage = get_gpu_usage()
    gpu_name, gpu_mem_used, gpu_mem_total = get_gpu_info()

    error = ""
    if run_info["returncode"] != 0:
        error = run_info["stderr"]
    if run_info["timed_out"]:
        error = run_info["stderr"]

    result = _empty_result(error)
    result["stdout_lines"] = (
        run_info["stdout"].splitlines() if run_info["stdout"] else []
    )
    result["stats"] = {
        "total_steps": 0,
        "execution_time": run_info["time_s"],
        "peak_memory_kb": run_info["peak_mem_kb"],
        "cpu_percent": run_info["cpu_pct"],
        "ram_percent": psutil.virtual_memory().percent,
        "gpu_percent": gpu_usage,
        "gpu_name": gpu_name,
        "gpu_mem_used": gpu_mem_used,
        "gpu_mem_total": gpu_mem_total,
        "max_call_depth": 0,
        "timed_out": run_info["timed_out"],
        "step_limit_hit": False,
        "language": language,
    }
    return result


# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE-SPECIFIC RUNNERS
# ─────────────────────────────────────────────────────────────────────────────

def _missing_tool_result(language: str) -> dict:
    result = _empty_result(check_toolchain(language) or f"{language} toolchain not found.")
    result["stats"]["language"] = language
    return result


def _run_c(code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Compile and run C code."""
    gcc = _find_executable("gcc")
    if not gcc:
        return _missing_tool_result("C")

    tmp = _get_temp_dir()
    try:
        src = os.path.join(tmp, "main.c")
        exe = os.path.join(tmp, "main.exe")

        with open(src, "w", encoding="utf-8") as f:
            f.write(code)

        compile_info = _run_subprocess(
            [gcc, "-o", exe, src, "-O2", "-lm"],
            timeout=30, cwd=tmp,
        )
        if compile_info["returncode"] != 0:
            result = _empty_result(
                f"C Compilation Error:\n{compile_info['stderr']}"
            )
            result["stats"]["language"] = "C"
            return result

        run_info = _run_subprocess([exe], timeout=timeout, cwd=tmp)
        return _subprocess_to_result(run_info, "C")
    finally:
        _cleanup_temp(tmp)


def _run_cpp(code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Compile and run C++ code."""
    gpp = _find_executable("g++")
    if not gpp:
        return _missing_tool_result("C++")

    tmp = _get_temp_dir()
    try:
        src = os.path.join(tmp, "main.cpp")
        exe = os.path.join(tmp, "main.exe")

        with open(src, "w", encoding="utf-8") as f:
            f.write(code)

        compile_info = _run_subprocess(
            [gpp, "-o", exe, src, "-std=c++17", "-O2"],
            timeout=30, cwd=tmp,
        )
        if compile_info["returncode"] != 0:
            result = _empty_result(
                f"C++ Compilation Error:\n{compile_info['stderr']}"
            )
            result["stats"]["language"] = "C++"
            return result

        run_info = _run_subprocess([exe], timeout=timeout, cwd=tmp)
        return _subprocess_to_result(run_info, "C++")
    finally:
        _cleanup_temp(tmp)


def _run_java(code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Compile and run Java code."""
    javac = _find_executable("javac")
    java = _find_executable("java")
    if not javac or not java:
        return _missing_tool_result("Java")

    tmp = _get_temp_dir()
    try:
        # Try to find the class name: public class first, then any class
        match = re.search(r"public\s+class\s+(\w+)", code)
        if not match:
            match = re.search(r"class\s+(\w+)", code)
        class_name = match.group(1) if match else "Main"

        src = os.path.join(tmp, f"{class_name}.java")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)

        compile_info = _run_subprocess(
            [javac, src], timeout=30, cwd=tmp,
        )
        if compile_info["returncode"] != 0:
            result = _empty_result(
                f"Java Compilation Error:\n{compile_info['stderr']}"
            )
            result["stats"]["language"] = "Java"
            return result

        run_info = _run_subprocess(
            [java, "-cp", tmp, class_name],
            timeout=timeout, cwd=tmp,
        )
        return _subprocess_to_result(run_info, "Java")
    finally:
        _cleanup_temp(tmp)


def _run_javascript(code: str, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Run JavaScript code via Node.js."""
    node = _find_executable("node")
    if not node:
        return _missing_tool_result("JavaScript")

    tmp = _get_temp_dir()
    try:
        src = os.path.join(tmp, "main.js")
        with open(src, "w", encoding="utf-8") as f:
            f.write(code)

        run_info = _run_subprocess(
            [node, src], timeout=timeout, cwd=tmp,
        )
        return _subprocess_to_result(run_info, "JavaScript")
    finally:
        _cleanup_temp(tmp)


# ─────────────────────────────────────────────────────────────────────────────
# UNIFIED ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
_RUNNERS = {
    "C": _run_c,
    "C++": _run_cpp,
    "Java": _run_java,
    "JavaScript": _run_javascript,
}


def run_code_multilang(code: str, language: str,
                       timeout: int = DEFAULT_TIMEOUT) -> dict:
    """
    Run code in the specified language and return a standardised result dict.

    1. Pre-flight check: is the compiler/runtime installed?
    2. For Python → full tracing engine.
    3. For C/C++/Java/JS → subprocess compile+run.
    """
    language = language.strip()

    # ── Pre-flight compiler check ────────────────────────────────────────
    missing = check_toolchain(language)
    if missing:
        result = _empty_result(missing)
        result["stats"]["language"] = language
        return result

    # ── Dispatch ─────────────────────────────────────────────────────────
    if language == "Python":
        result = run_python_code(code, timeout=timeout)
        result["stats"]["language"] = "Python"
        return result

    runner = _RUNNERS.get(language)
    if runner:
        return runner(code, timeout)

    return _empty_result(f"Unsupported language: {language}")


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT SAMPLE CODE PER LANGUAGE (for comparison mode)
# ─────────────────────────────────────────────────────────────────────────────
SAMPLE_CODE = {
    "Python": '''\
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

data = [64, 34, 25, 12, 22, 11, 90]
result = bubble_sort(data)
print("Sorted:", result)
''',

    "C": '''\
#include <stdio.h>

void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n - i - 1; j++)
            if (arr[j] > arr[j+1]) {
                int tmp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = tmp;
            }
}

int main() {
    int data[] = {64, 34, 25, 12, 22, 11, 90};
    int n = sizeof(data) / sizeof(data[0]);
    bubbleSort(data, n);
    printf("Sorted:");
    for (int i = 0; i < n; i++) printf(" %d", data[i]);
    printf("\\n");
    return 0;
}
''',

    "C++": '''\
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

void bubbleSort(vector<int>& arr) {
    int n = arr.size();
    for (int i = 0; i < n; i++)
        for (int j = 0; j < n - i - 1; j++)
            if (arr[j] > arr[j+1])
                swap(arr[j], arr[j+1]);
}

int main() {
    vector<int> data = {64, 34, 25, 12, 22, 11, 90};
    bubbleSort(data);
    cout << "Sorted:";
    for (int x : data) cout << " " << x;
    cout << endl;
    return 0;
}
''',

    "Java": '''\
public class Main {
    static void bubbleSort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i < n; i++)
            for (int j = 0; j < n - i - 1; j++)
                if (arr[j] > arr[j+1]) {
                    int tmp = arr[j];
                    arr[j] = arr[j+1];
                    arr[j+1] = tmp;
                }
    }

    public static void main(String[] args) {
        int[] data = {64, 34, 25, 12, 22, 11, 90};
        bubbleSort(data);
        System.out.print("Sorted:");
        for (int x : data) System.out.print(" " + x);
        System.out.println();
    }
}
''',

    "JavaScript": '''\
function bubbleSort(arr) {
    const n = arr.length;
    for (let i = 0; i < n; i++)
        for (let j = 0; j < n - i - 1; j++)
            if (arr[j] > arr[j + 1])
                [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
    return arr;
}

const data = [64, 34, 25, 12, 22, 11, 90];
const result = bubbleSort(data);
console.log("Sorted:", result.join(" "));
''',
}


# ─────────────────────────────────────────────────────────────────────────────
# HELLO-WORLD TEMPLATES (for editor mode)
# ─────────────────────────────────────────────────────────────────────────────
HELLO_TEMPLATES = {
    "Python": 'print("Hello World")\n',

    "C": '''\
#include <stdio.h>
int main() {
    printf("Hello World\\n");
    return 0;
}
''',

    "C++": '''\
#include <iostream>
using namespace std;
int main() {
    cout << "Hello World" << endl;
    return 0;
}
''',

    "Java": '''\
public class Main {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
''',

    "JavaScript": 'console.log("Hello World");\n',
}
