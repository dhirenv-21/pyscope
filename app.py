"""
PyScope — Main Application (v5 · Premium IDE)
=================================================
Streamlit orchestration layer.  Routes between Landing → Editor → Compare
and wires up the execution engine, UI components, and insights modules.
"""

# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────
import os
import glob

import streamlit as st
import matplotlib.pyplot as plt

from ui_styles import get_css
from execution_engine import run_code
from multi_lang_runner import (run_code_multilang, SUPPORTED_LANGUAGES,
                               SAMPLE_CODE, HELLO_TEMPLATES, check_toolchain)
from insights import generate_insights, generate_comparison_verdict, generate_cross_language_insights
from graph_utils import build_graphs, build_single_graph, build_comparison_chart, build_summary_chart
from ui_components import (
    render_landing_page,
    render_header,
    render_file_explorer,
    render_code_display,
    render_logs,
    render_variables,
    render_call_stack,
    render_stats_cards,
    render_console,
    render_insights,
    render_comparison_table,
)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PyScope",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ─────────────────────────────────────────────────────────────────────────────
# DEFAULT CODE
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_CODE = '''\
def calculate_sum(n):
    total = 0
    for i in range(1, n + 1):
        total += i
    return total

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

number = 5
result = calculate_sum(number)
fact   = factorial(6)
print("Sum 1..5  :", result)
print("6!        :", fact)
'''

COMPARE_CODE_A = '''\
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
'''

COMPARE_CODE_B = '''\
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
'''


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
defaults = {
    "page": "landing",       # landing | editor | compare
    "mode": "normal",        # normal  | compare  (UI mode guard)
    "theme": "dark",

    # Editor — multi-language
    "code": DEFAULT_CODE,
    "active_file": "✦ scratch",
    "editor_language": "Python",

    # Execution results
    "logs": [],
    "stdout_lines": [],
    "stats": {},
    "time_points": [],
    "memory_points": [],
    "cpu_points": [],
    "gpu_points": [],
    "step_points": [],
    "call_tree": [],
    "variables_timeline": [],
    "insights_list": [],
    "run_status": None,
    "error_msg": "",
    "has_results": False,
    "current_step": 0,
    "is_running": False,

    # Compare mode
    "compare_code_a": COMPARE_CODE_A,
    "compare_code_b": COMPARE_CODE_B,
    "compare_lang_a": "Python",
    "compare_lang_b": "C++",
    "compare_results_a": None,
    "compare_results_b": None,
    "compare_verdict": None,
    "compare_has_results": False,
    "compare_cross_insights": [],
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

theme_mode = st.session_state["theme"]

# ── Inject CSS ──
st.markdown(get_css(theme_mode), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOADING OVERLAY COMPONENT
# ─────────────────────────────────────────────────────────────────────────────
def _show_loading(message: str = "Running your code…"):
    """Show a premium full-screen loading overlay."""
    st.markdown(f"""
    <div class="loading-overlay" id="pyscope-loader">
        <div class="loading-spinner"></div>
        <div class="loading-text">{message}</div>
        <div class="loading-sub">Tracing execution · Monitoring resources</div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# GRAPH POPUP DIALOGS  (module-level for @st.dialog)
# ─────────────────────────────────────────────────────────────────────────────
@st.dialog("📈 Memory (KB)", width="large")
def show_memory_graph():
    fig = build_single_graph(
        st.session_state["time_points"],
        st.session_state["memory_points"],
        "Memory Usage Over Time", "KB",
        color="#818cf8", mode=st.session_state["theme"],
    )
    st.pyplot(fig)
    plt.close(fig)

@st.dialog("📈 CPU (%)", width="large")
def show_cpu_graph():
    fig = build_single_graph(
        st.session_state["time_points"],
        st.session_state["cpu_points"],
        "CPU Usage Over Time", "%",
        color="#34d399", mode=st.session_state["theme"],
    )
    st.pyplot(fig)
    plt.close(fig)

@st.dialog("📈 GPU (%)", width="large")
def show_gpu_graph():
    fig = build_single_graph(
        st.session_state["time_points"],
        st.session_state["gpu_points"],
        "GPU Usage Over Time", "%",
        color="#38bdf8", mode=st.session_state["theme"],
    )
    st.pyplot(fig)
    plt.close(fig)

@st.dialog("📈 Execution Steps", width="large")
def show_steps_graph():
    fig = build_single_graph(
        st.session_state["time_points"],
        st.session_state["step_points"],
        "Execution Steps Over Time", "#",
        color="#fb923c", mode=st.session_state["theme"],
    )
    st.pyplot(fig)
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _list_py_files():
    """List .py files in the project directory."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    py_files = sorted(glob.glob(os.path.join(project_dir, "*.py")))
    return [os.path.basename(f) for f in py_files]


def _read_file(filename: str) -> str:
    """Read a .py file from the project directory."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(project_dir, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"# File not found: {filename}"


def _get_highlight_line() -> int:
    """Determine which source line is active at the current step."""
    if not st.session_state["has_results"]:
        return -1
    step = st.session_state.get("current_step", 0)
    highlight = -1
    for entry in st.session_state.get("logs", []):
        if entry.get("kind") != "line":
            continue
        if entry.get("step", 0) <= step:
            highlight = entry.get("line", -1)
        else:
            break
    return highlight


def _run_and_store(user_code: str, language: str = "Python"):
    """Execute code in the given language and store results in session state."""
    # Pre-flight toolchain check
    missing = check_toolchain(language)
    if missing:
        st.session_state["run_status"] = "error"
        st.session_state["error_msg"] = missing
        st.session_state["has_results"] = False
        return

    result = run_code_multilang(user_code, language)

    st.session_state["logs"] = result["logs"]
    st.session_state["stdout_lines"] = result["stdout_lines"]
    st.session_state["stats"] = result["stats"]
    st.session_state["time_points"] = result["time_points"]
    st.session_state["memory_points"] = result["memory_points"]
    st.session_state["cpu_points"] = result["cpu_points"]
    st.session_state["gpu_points"] = result["gpu_points"]
    st.session_state["step_points"] = result["step_points"]
    st.session_state["call_tree"] = result["call_tree"]
    st.session_state["variables_timeline"] = result["variables_timeline"]
    st.session_state["has_results"] = True
    st.session_state["current_step"] = result["stats"].get("total_steps", 0)

    if result["error"]:
        st.session_state["run_status"] = "error"
        st.session_state["error_msg"] = result["error"]
    else:
        st.session_state["run_status"] = "success"
        st.session_state["error_msg"] = ""

    # Insights only make sense for Python (traced)
    if language == "Python":
        st.session_state["insights_list"] = generate_insights(
            result["stats"], result["logs"], result["call_tree"]
        )
    else:
        st.session_state["insights_list"] = []


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: LANDING
# ═══════════════════════════════════════════════════════════════════════════════
def page_landing():
    st.markdown(render_landing_page(), unsafe_allow_html=True)

    # Action buttons — tight center
    _, btn_col, _ = st.columns([3.5, 2, 3.5])
    with btn_col:
        st.markdown('<div class="run-btn">', unsafe_allow_html=True)
        if st.button("▶  Start Coding", key="landing_start", use_container_width=True):
            st.session_state["page"] = "editor"
            st.session_state["mode"] = "normal"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("⚖  Compare Algorithms", key="landing_compare", use_container_width=True):
            st.session_state["page"] = "compare"
            st.session_state["mode"] = "compare"
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: EDITOR  — 3-column IDE layout
# ═══════════════════════════════════════════════════════════════════════════════
def page_editor():
    # ── Header bar ───────────────────────────────────────────────────────
    h_left, h_spacer, h_compare, h_home, h_theme = st.columns([5, 1.5, 1, 0.6, 0.5])
    with h_left:
        st.markdown(render_header(), unsafe_allow_html=True)
    with h_compare:
        if st.button("⚖ Compare", key="btn_compare", use_container_width=True):
            st.session_state["page"] = "compare"
            st.session_state["mode"] = "compare"
            st.rerun()
    with h_home:
        if st.button("🏠", key="btn_home", help="Back to home"):
            st.session_state["page"] = "landing"
            st.session_state["mode"] = "normal"
            st.rerun()
    with h_theme:
        theme_toggle = st.toggle(
            "☀" if theme_mode == "light" else "☾",
            value=(theme_mode == "light"),
            key="theme_toggle",
            help="Toggle light / dark",
        )
        if theme_toggle and theme_mode == "dark":
            st.session_state["theme"] = "light"
            st.rerun()
        elif not theme_toggle and theme_mode == "light":
            st.session_state["theme"] = "dark"
            st.rerun()

    # ── 3-column IDE layout ──────────────────────────────────────────────
    sidebar_col, editor_col, panel_col = st.columns([0.75, 2.2, 2.05], gap="small")

    # ═══ LEFT SIDEBAR ═══
    with sidebar_col:
        # File Explorer
        py_files = _list_py_files()
        file_options = ["✦ scratch"] + py_files
        st.markdown(
            render_file_explorer(py_files, st.session_state["active_file"]),
            unsafe_allow_html=True,
        )
        current_active = st.session_state["active_file"]
        selected_file = st.selectbox(
            "Load file",
            file_options,
            index=file_options.index(current_active)
                if current_active in file_options else 0,
            key="file_selector",
            label_visibility="collapsed",
        )
        if selected_file != current_active:
            st.session_state["active_file"] = selected_file
            if selected_file == "✦ scratch":
                lang = st.session_state.get("editor_language", "Python")
                st.session_state["code"] = (
                    DEFAULT_CODE if lang == "Python"
                    else HELLO_TEMPLATES.get(lang, "")
                )
            else:
                st.session_state["code"] = _read_file(selected_file)
                if selected_file.endswith(".py"):
                    st.session_state["editor_language"] = "Python"
            st.session_state.pop("code_editor", None)
            st.session_state["has_results"] = False
            st.rerun()

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        # Language selector
        cur_lang = st.session_state["editor_language"]
        lang_sel = st.selectbox(
            "Language",
            SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(cur_lang)
                if cur_lang in SUPPORTED_LANGUAGES else 0,
            key="editor_lang_sel",
        )
        if lang_sel != cur_lang:
            st.session_state["editor_language"] = lang_sel
            st.session_state["code"] = HELLO_TEMPLATES.get(lang_sel, "")
            st.session_state["active_file"] = "✦ scratch"
            for stale in ("code_editor", "file_selector"):
                st.session_state.pop(stale, None)
            st.session_state["has_results"] = False
            st.session_state["run_status"] = None
            st.session_state["error_msg"] = ""
            st.session_state["stdout_lines"] = []
            st.rerun()

        st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

        # Action buttons
        st.markdown('<div class="run-btn">', unsafe_allow_html=True)
        run_clicked = st.button("▶  Run", key="btn_run", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:0.15rem'></div>", unsafe_allow_html=True)
        reset_clicked = st.button("⟲ Reset", key="btn_reset", use_container_width=True)

    # ═══ CENTER: EDITOR ═══
    with editor_col:
        st.markdown(f'<div class="sec">Editor — {lang_sel}</div>', unsafe_allow_html=True)

        placeholder = {
            "Python": "# Write Python code here…",
            "C": "// Write C code here…",
            "C++": "// Write C++ code here…",
            "Java": "// Write Java code here…",
            "JavaScript": "// Write JavaScript code here…",
        }.get(lang_sel, "// Write code here…")

        code_input = st.text_area(
            label="code_editor",
            value=st.session_state["code"],
            height=310,
            label_visibility="collapsed",
            placeholder=placeholder,
            key="code_editor",
        )

        # Line-numbered code display with active line highlight
        if st.session_state["has_results"]:
            highlight = _get_highlight_line()
            st.markdown(
                render_code_display(
                    code_input,
                    highlight_line=highlight,
                    filename=st.session_state["active_file"],
                ),
                unsafe_allow_html=True,
            )

        # Console
        console_status = "idle"
        if st.session_state["run_status"] == "success":
            console_status = "success"
        elif st.session_state["run_status"] == "error":
            console_status = "error"

        st.markdown(
            render_console(
                st.session_state["stdout_lines"],
                st.session_state["error_msg"],
                console_status,
            ),
            unsafe_allow_html=True,
        )

    # ═══ RIGHT PANEL ═══
    with panel_col:
        if st.session_state["has_results"]:
            # Status pill
            status_cls = "success" if st.session_state["run_status"] == "success" else "error"
            status_txt = "✓ Done" if st.session_state["run_status"] == "success" else "✗ Error"
            st.markdown(
                f'<div class="status-pill {status_cls}">'
                f'<div class="status-dot"></div>{status_txt}</div>',
                unsafe_allow_html=True,
            )

            # ── Stats Grid ──
            if st.session_state["stats"]:
                st.markdown(
                    render_stats_cards(st.session_state["stats"]),
                    unsafe_allow_html=True,
                )

                # Stat-linked graph popup buttons
                s1, s2, s3, s4 = st.columns(4)
                with s1:
                    if st.button("📈 Mem", key="popup_mem", use_container_width=True):
                        show_memory_graph()
                with s2:
                    if st.button("📈 CPU", key="popup_cpu", use_container_width=True):
                        show_cpu_graph()
                with s3:
                    if st.button("📈 GPU", key="popup_gpu", use_container_width=True):
                        show_gpu_graph()
                with s4:
                    if st.button("📈 Steps", key="popup_steps", use_container_width=True):
                        show_steps_graph()

            # ── Step Debugging Controls ──
            total_steps = st.session_state["stats"].get("total_steps", 0)

            if total_steps > 1:
                st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)
                sel = st.slider(
                    "Step", 1, total_steps,
                    st.session_state.get("current_step", total_steps),
                    key="step_slider",
                )
                st.session_state["current_step"] = sel

                nav1, nav2, nav3 = st.columns([1, 2, 1])
                with nav1:
                    if st.button("◀ Back", key="step_back", use_container_width=True):
                        st.session_state["current_step"] = max(1, sel - 1)
                        st.rerun()
                with nav2:
                    st.markdown(
                        f'<div class="step-badge">Step {sel} / {total_steps}</div>',
                        unsafe_allow_html=True,
                    )
                with nav3:
                    if st.button("Next ▶", key="step_fwd", use_container_width=True):
                        st.session_state["current_step"] = min(total_steps, sel + 1)
                        st.rerun()
            else:
                sel = total_steps
                st.session_state["current_step"] = sel

            # ── Analysis Tabs ──
            is_python = st.session_state.get("editor_language", "Python") == "Python"
            tab_trace, tab_vars, tab_stack, tab_graphs, tab_insights = st.tabs(
                ["🔍 Trace", "📋 Variables", "🌳 Call Stack", "📊 Graphs", "🧠 Insights"]
            )

            _NOT_PYTHON_MSG = (
                '<div class="trace-empty">'
                '⚠️ Step-level tracing is only available for Python. '
                'Other languages show output, stats, and graphs only.'
                '</div>'
            )

            with tab_trace:
                if is_python:
                    st.markdown(
                        render_logs(st.session_state["logs"], upto=sel),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(_NOT_PYTHON_MSG, unsafe_allow_html=True)

            with tab_vars:
                if is_python:
                    step = st.session_state.get("current_step", total_steps)
                    st.markdown(
                        render_variables(st.session_state["variables_timeline"], step),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(_NOT_PYTHON_MSG, unsafe_allow_html=True)

            with tab_stack:
                if is_python:
                    st.markdown(
                        render_call_stack(st.session_state["call_tree"]),
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(_NOT_PYTHON_MSG, unsafe_allow_html=True)

            with tab_graphs:
                if st.session_state["time_points"]:
                    fig = build_graphs(
                        st.session_state["time_points"],
                        st.session_state["memory_points"],
                        st.session_state["cpu_points"],
                        st.session_state["gpu_points"],
                        st.session_state["step_points"],
                        mode=theme_mode,
                        gpu_name=st.session_state["stats"].get("gpu_name", "GPU"),
                    )
                    st.pyplot(fig)
                    plt.close(fig)
                else:
                    # Non-Python: show summary bar chart from stats
                    if st.session_state["stats"]:
                        fig = build_summary_chart(
                            st.session_state["stats"],
                            mode=theme_mode,
                        )
                        st.pyplot(fig)
                        plt.close(fig)
                    else:
                        st.markdown(
                            '<div class="trace-empty">No data to graph yet.</div>',
                            unsafe_allow_html=True,
                        )

            with tab_insights:
                st.markdown(
                    render_insights(st.session_state["insights_list"]),
                    unsafe_allow_html=True,
                )

        else:
            # Empty state
            st.markdown("""
            <div class="empty">
              <span class="empty-icon">⬡</span>
              <span>Run your code to see results</span>
              <span class="empty-hint">Trace · Variables · Call Stack · Graphs · Insights</span>
            </div>
            """, unsafe_allow_html=True)

    # ── Handlers ─────────────────────────────────────────────────────────
    if reset_clicked:
        for key in ["logs", "stdout_lines", "time_points", "memory_points",
                     "cpu_points", "gpu_points", "step_points", "call_tree",
                     "variables_timeline", "insights_list"]:
            st.session_state[key] = []
        st.session_state["stats"] = {}
        st.session_state["run_status"] = None
        st.session_state["error_msg"] = ""
        st.session_state["has_results"] = False
        st.session_state["current_step"] = 0
        st.rerun()

    if run_clicked:
        user_code = code_input.strip()
        if not user_code:
            st.warning("Enter some code first.")
        else:
            selected_lang = st.session_state.get("editor_language", "Python")
            st.session_state["code"] = user_code
            _show_loading(f"Running {selected_lang} code…")
            _run_and_store(user_code, language=selected_lang)
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE: COMPARE (Cross-Language)
# ═══════════════════════════════════════════════════════════════════════════════
def page_compare():
    # Header
    h_left, h_spacer, h_editor, h_home = st.columns([5, 2, 1, 0.6])
    with h_left:
        st.markdown(render_header(), unsafe_allow_html=True)
    with h_editor:
        if st.button("✏️ Editor", key="cmp_editor", use_container_width=True):
            st.session_state["page"] = "editor"
            st.rerun()
    with h_home:
        if st.button("🏠", key="cmp_home", help="Back to home"):
            st.session_state["page"] = "landing"
            st.rerun()

    # Title
    st.markdown(
        '<div class="compare-header">'
        '<h2>⚖️ Cross-Language Comparison</h2>'
        '<p>Run two programs in different languages and compare performance</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Language selectors + editors side by side ───────────────────────
    col_a, col_b = st.columns(2, gap="medium")

    with col_a:
        st.markdown(
            '<div class="compare-label"><span class="badge">A</span> Program A</div>',
            unsafe_allow_html=True,
        )
        lang_a = st.selectbox(
            "Language A",
            SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(st.session_state["compare_lang_a"]),
            key="select_lang_a",
            label_visibility="collapsed",
        )
        # Auto-fill sample code when language changes
        if lang_a != st.session_state["compare_lang_a"]:
            st.session_state["compare_lang_a"] = lang_a
            st.session_state["compare_code_a"] = SAMPLE_CODE.get(lang_a, "")
            st.session_state.pop("compare_editor_a", None)
            st.session_state["compare_has_results"] = False
            st.rerun()

        code_a = st.text_area(
            "Program A",
            value=st.session_state["compare_code_a"],
            height=260,
            label_visibility="collapsed",
            key="compare_editor_a",
        )

    with col_b:
        st.markdown(
            '<div class="compare-label"><span class="badge">B</span> Program B</div>',
            unsafe_allow_html=True,
        )
        lang_b = st.selectbox(
            "Language B",
            SUPPORTED_LANGUAGES,
            index=SUPPORTED_LANGUAGES.index(st.session_state["compare_lang_b"]),
            key="select_lang_b",
            label_visibility="collapsed",
        )
        if lang_b != st.session_state["compare_lang_b"]:
            st.session_state["compare_lang_b"] = lang_b
            st.session_state["compare_code_b"] = SAMPLE_CODE.get(lang_b, "")
            st.session_state.pop("compare_editor_b", None)
            st.session_state["compare_has_results"] = False
            st.rerun()

        code_b = st.text_area(
            "Program B",
            value=st.session_state["compare_code_b"],
            height=260,
            label_visibility="collapsed",
            key="compare_editor_b",
        )

    # Run button
    _, btn_col, _ = st.columns([2, 1.5, 2])
    with btn_col:
        st.markdown('<div class="run-btn">', unsafe_allow_html=True)
        compare_clicked = st.button(
            "⚡ Run Comparison",
            key="btn_compare_run",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Results ──────────────────────────────────────────────────────────
    if st.session_state["compare_has_results"]:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        res_a = st.session_state["compare_results_a"]
        res_b = st.session_state["compare_results_b"]
        verdict = st.session_state["compare_verdict"]
        sel_lang_a = st.session_state["compare_lang_a"]
        sel_lang_b = st.session_state["compare_lang_b"]

        # Output side by side
        out_left, out_right = st.columns(2, gap="medium")
        with out_left:
            st.markdown(
                f'<div class="compare-label"><span class="badge">A</span> {sel_lang_a} — Output</div>',
                unsafe_allow_html=True,
            )
            if res_a and res_a.get("stdout_lines"):
                st.markdown(render_console(res_a["stdout_lines"]), unsafe_allow_html=True)
            if res_a and res_a.get("error"):
                st.markdown(
                    f'<div class="err-box">{res_a["error"]}</div>',
                    unsafe_allow_html=True,
                )
        with out_right:
            st.markdown(
                f'<div class="compare-label"><span class="badge">B</span> {sel_lang_b} — Output</div>',
                unsafe_allow_html=True,
            )
            if res_b and res_b.get("stdout_lines"):
                st.markdown(render_console(res_b["stdout_lines"]), unsafe_allow_html=True)
            if res_b and res_b.get("error"):
                st.markdown(
                    f'<div class="err-box">{res_b["error"]}</div>',
                    unsafe_allow_html=True,
                )

        # Stats side by side
        s_left, s_right = st.columns(2, gap="medium")
        with s_left:
            st.markdown(
                f'<div class="compare-label"><span class="badge">A</span> {sel_lang_a} — Stats</div>',
                unsafe_allow_html=True,
            )
            if res_a and res_a.get("stats"):
                st.markdown(render_stats_cards(res_a["stats"]), unsafe_allow_html=True)

        with s_right:
            st.markdown(
                f'<div class="compare-label"><span class="badge">B</span> {sel_lang_b} — Stats</div>',
                unsafe_allow_html=True,
            )
            if res_b and res_b.get("stats"):
                st.markdown(render_stats_cards(res_b["stats"]), unsafe_allow_html=True)

        # Comparison table + verdict
        if verdict:
            st.markdown(render_comparison_table(verdict), unsafe_allow_html=True)

        # Comparison chart
        if verdict and verdict.get("details"):
            fig = build_comparison_chart(
                verdict["details"],
                mode=st.session_state["theme"],
                label_a=f"{sel_lang_a} (A)",
                label_b=f"{sel_lang_b} (B)",
            )
            st.pyplot(fig)
            plt.close(fig)

        # Cross-language insights
        cross_ins = st.session_state.get("compare_cross_insights", [])
        if cross_ins:
            st.markdown(
                '<div class="sec">🌐 Cross-Language Insights</div>',
                unsafe_allow_html=True,
            )
            st.markdown(render_insights(cross_ins), unsafe_allow_html=True)

        # Per-program insights (only meaningful for Python)
        col_ia, col_ib = st.columns(2, gap="medium")
        with col_ia:
            if sel_lang_a == "Python" and res_a:
                st.markdown(
                    f'<div class="sec">Insights — {sel_lang_a}</div>',
                    unsafe_allow_html=True,
                )
                insights_a = generate_insights(
                    res_a.get("stats", {}), res_a.get("logs", [])
                )
                st.markdown(render_insights(insights_a), unsafe_allow_html=True)
        with col_ib:
            if sel_lang_b == "Python" and res_b:
                st.markdown(
                    f'<div class="sec">Insights — {sel_lang_b}</div>',
                    unsafe_allow_html=True,
                )
                insights_b = generate_insights(
                    res_b.get("stats", {}), res_b.get("logs", [])
                )
                st.markdown(render_insights(insights_b), unsafe_allow_html=True)

    # ── Handler ──────────────────────────────────────────────────────────
    if compare_clicked:
        a_code = code_a.strip()
        b_code = code_b.strip()
        sel_a = st.session_state["compare_lang_a"]
        sel_b = st.session_state["compare_lang_b"]

        if not a_code or not b_code:
            st.warning("Please enter code for both programs.")
        else:
            st.session_state["compare_code_a"] = a_code
            st.session_state["compare_code_b"] = b_code
            _show_loading(f"Running {sel_a} vs {sel_b}…")

            res_a = run_code_multilang(a_code, sel_a)
            res_b = run_code_multilang(b_code, sel_b)

            label_a = f"{sel_a} (A)"
            label_b = f"{sel_b} (B)"

            st.session_state["compare_results_a"] = res_a
            st.session_state["compare_results_b"] = res_b
            st.session_state["compare_verdict"] = generate_comparison_verdict(
                res_a["stats"], res_b["stats"],
                label_a=label_a, label_b=label_b,
            )
            st.session_state["compare_cross_insights"] = generate_cross_language_insights(
                res_a["stats"], res_b["stats"], sel_a, sel_b,
            )
            st.session_state["compare_has_results"] = True
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
page = st.session_state.get("page", "landing")

if page == "editor":
    page_editor()
elif page == "compare":
    page_compare()
else:
    page_landing()
