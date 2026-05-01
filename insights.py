"""
PyScope — Smart Insights Engine
================================
Rule-based analysis of execution stats to generate actionable insights.
"""


def generate_insights(stats: dict, logs: list, call_tree: list = None) -> list:
    """
    Analyse execution stats and produce a list of insight dicts.

    Each insight: {
        "icon": str,
        "title": str,
        "description": str,
        "severity": "success" | "info" | "warning" | "danger"
    }
    """
    insights = []
    total_steps = stats.get("total_steps", 0)
    exec_time = stats.get("execution_time", 0)
    exec_time_ms = exec_time * 1000
    peak_mem = stats.get("peak_memory_kb", 0)
    cpu_pct = stats.get("cpu_percent", 0)
    max_depth = stats.get("max_call_depth", 0)
    timed_out = stats.get("timed_out", False)
    step_limit = stats.get("step_limit_hit", False)

    # Count function calls/returns
    call_count = sum(1 for l in logs if l.get("kind") == "call")
    return_count = sum(1 for l in logs if l.get("kind") == "return")

    # ── Timeout / step limit ────────────────────────────────────────────
    if timed_out:
        insights.append({
            "icon": "⏰",
            "title": "Execution Timed Out",
            "description": (
                "The program was terminated because it exceeded the time limit. "
                "This usually indicates an infinite loop or very expensive computation."
            ),
            "severity": "danger",
        })

    if step_limit:
        insights.append({
            "icon": "🔁",
            "title": "Step Limit Reached",
            "description": (
                f"Execution was stopped after {total_steps:,} steps. "
                "This suggests an infinite or very long-running loop. "
                "Consider adding proper termination conditions."
            ),
            "severity": "danger",
        })

    # ── CPU analysis ────────────────────────────────────────────────────
    if cpu_pct > 80:
        insights.append({
            "icon": "🔥",
            "title": "Very High CPU Usage",
            "description": (
                f"CPU usage peaked at {cpu_pct:.1f}%. This indicates compute-intensive "
                "operations. Consider algorithmic optimisation or caching intermediate results."
            ),
            "severity": "danger",
        })
    elif cpu_pct > 50:
        insights.append({
            "icon": "⚡",
            "title": "Elevated CPU Usage",
            "description": (
                f"CPU usage reached {cpu_pct:.1f}%. The code is moderately compute-intensive. "
                "Loop optimisation may help reduce processing load."
            ),
            "severity": "warning",
        })

    # ── Memory analysis ─────────────────────────────────────────────────
    if peak_mem > 10000:
        insights.append({
            "icon": "🧠",
            "title": "High Memory Usage",
            "description": (
                f"Peak memory usage was {peak_mem:.0f} KB. This could indicate large data "
                "structures, deep recursion, or memory-inefficient operations. "
                "Consider using generators or processing data in chunks."
            ),
            "severity": "warning",
        })
    elif peak_mem > 5000:
        insights.append({
            "icon": "💾",
            "title": "Moderate Memory Usage",
            "description": (
                f"Peak memory was {peak_mem:.0f} KB. Monitor memory growth if processing "
                "larger datasets in production."
            ),
            "severity": "info",
        })

    # ── Step efficiency ─────────────────────────────────────────────────
    if total_steps < 10 and exec_time_ms > 500:
        insights.append({
            "icon": "🐌",
            "title": "Slow Despite Few Steps",
            "description": (
                f"Only {total_steps} steps but {exec_time_ms:.0f}ms execution time. "
                "This suggests expensive I/O operations, sleep calls, or external process waits."
            ),
            "severity": "warning",
        })
    elif total_steps > 500:
        insights.append({
            "icon": "🔄",
            "title": "High Step Count",
            "description": (
                f"The program executed {total_steps:,} steps. Consider optimising loops "
                "or using built-in functions (e.g., sum(), map()) for better performance."
            ),
            "severity": "info",
        })

    # ── Call depth analysis ─────────────────────────────────────────────
    if max_depth > 10:
        insights.append({
            "icon": "📚",
            "title": "Deep Recursion Detected",
            "description": (
                f"Maximum call depth was {max_depth}. Deep recursion can cause stack overflow "
                "on larger inputs. Consider converting to an iterative approach."
            ),
            "severity": "warning",
        })
    elif max_depth > 5:
        insights.append({
            "icon": "📖",
            "title": "Moderate Call Depth",
            "description": (
                f"Maximum call depth reached {max_depth}. The recursive approach works for "
                "this input size but may not scale well."
            ),
            "severity": "info",
        })

    # ── Function usage ──────────────────────────────────────────────────
    if call_count == 0 and total_steps > 0:
        insights.append({
            "icon": "📝",
            "title": "No Functions Used",
            "description": (
                "The code runs entirely at module level with no function definitions. "
                "Consider organizing logic into functions for better readability and reuse."
            ),
            "severity": "info",
        })
    elif call_count > 20:
        insights.append({
            "icon": "📞",
            "title": "Many Function Calls",
            "description": (
                f"{call_count} function calls detected. If performance is critical, "
                "consider reducing call overhead or inlining small utility functions."
            ),
            "severity": "info",
        })

    # ── Fast execution (positive) ───────────────────────────────────────
    if exec_time_ms < 50 and total_steps > 0 and not timed_out and not step_limit:
        insights.append({
            "icon": "🚀",
            "title": "Fast Execution",
            "description": (
                f"Completed in {exec_time_ms:.1f}ms — excellent performance! "
                "The code is efficient for this input size."
            ),
            "severity": "success",
        })

    # ── Clean execution (positive) ──────────────────────────────────────
    if total_steps > 0 and not timed_out and not step_limit and peak_mem < 1000:
        insights.append({
            "icon": "✨",
            "title": "Clean Execution",
            "description": (
                "Low memory footprint and successful completion. "
                "The code is well-structured for this workload."
            ),
            "severity": "success",
        })

    return insights


def generate_comparison_verdict(stats_a: dict, stats_b: dict,
                                label_a: str = "A", label_b: str = "B") -> dict:
    """
    Compare two execution results and produce a verdict.

    Returns: {
        "winner": "A" | "B" | "Tie",
        "reason": str,
        "label_a": str,
        "label_b": str,
        "details": [{"metric": ..., "a": ..., "b": ..., "better": "A"|"B"|"Tie"}, ...]
    }
    """
    metrics = []

    def _compare(name, a_val, b_val, lower_is_better=True, unit=""):
        if a_val is None or b_val is None:
            better = "Tie"
        elif lower_is_better:
            if a_val < b_val:
                better = "A"
            elif b_val < a_val:
                better = "B"
            else:
                better = "Tie"
        else:
            if a_val > b_val:
                better = "A"
            elif b_val > a_val:
                better = "B"
            else:
                better = "Tie"

        metrics.append({
            "metric": name,
            "a": a_val,
            "b": b_val,
            "better": better,
            "unit": unit,
        })

    _compare("Execution Time", stats_a.get("execution_time", 0) * 1000,
             stats_b.get("execution_time", 0) * 1000, True, "ms")

    # Only compare steps if both are Python (traced)
    lang_a = stats_a.get("language", "Python")
    lang_b = stats_b.get("language", "Python")
    if lang_a == "Python" and lang_b == "Python":
        _compare("Total Steps", stats_a.get("total_steps", 0),
                 stats_b.get("total_steps", 0), True, "")

    _compare("Peak Memory", stats_a.get("peak_memory_kb", 0),
             stats_b.get("peak_memory_kb", 0), True, "KB")
    _compare("CPU Usage", stats_a.get("cpu_percent", 0),
             stats_b.get("cpu_percent", 0), True, "%")

    a_wins = sum(1 for m in metrics if m["better"] == "A")
    b_wins = sum(1 for m in metrics if m["better"] == "B")

    if a_wins > b_wins:
        winner = "A"
        reason = f"{label_a} wins in {a_wins} of {len(metrics)} metrics — more efficient overall."
    elif b_wins > a_wins:
        winner = "B"
        reason = f"{label_b} wins in {b_wins} of {len(metrics)} metrics — more efficient overall."
    else:
        winner = "Tie"
        reason = "Both programs perform similarly across all metrics."

    return {
        "winner": winner,
        "reason": reason,
        "label_a": label_a,
        "label_b": label_b,
        "details": metrics,
    }


# ─────────────────────────────────────────────────────────────────────────────
# CROSS-LANGUAGE INSIGHTS (rule-based)
# ─────────────────────────────────────────────────────────────────────────────
_COMPILED_LANGS = {"C++", "Java"}
_INTERPRETED_LANGS = {"Python", "JavaScript"}


def generate_cross_language_insights(stats_a: dict, stats_b: dict,
                                     lang_a: str, lang_b: str) -> list:
    """
    Generate rule-based insights about cross-language performance differences.
    Returns a list of insight dicts (icon, title, description, severity).
    """
    insights = []
    time_a = stats_a.get("execution_time", 0) * 1000
    time_b = stats_b.get("execution_time", 0) * 1000
    mem_a = stats_a.get("peak_memory_kb", 0)
    mem_b = stats_b.get("peak_memory_kb", 0)

    # Same-language comparison
    if lang_a == lang_b:
        insights.append({
            "icon": "🔬",
            "title": "Same-Language Comparison",
            "description": (
                f"Both programs run in {lang_a}. Differences are due to "
                "algorithm design, not language overhead."
            ),
            "severity": "info",
        })
        return insights

    # Compiled vs interpreted
    a_compiled = lang_a in _COMPILED_LANGS
    b_compiled = lang_b in _COMPILED_LANGS

    if a_compiled and not b_compiled:
        insights.append({
            "icon": "⚙️",
            "title": f"{lang_a} is Compiled",
            "description": (
                f"{lang_a} compiles to native machine code before execution, "
                f"which typically gives it a speed advantage over interpreted "
                f"languages like {lang_b}."
            ),
            "severity": "info",
        })
    elif b_compiled and not a_compiled:
        insights.append({
            "icon": "⚙️",
            "title": f"{lang_b} is Compiled",
            "description": (
                f"{lang_b} compiles to native machine code before execution, "
                f"which typically gives it a speed advantage over interpreted "
                f"languages like {lang_a}."
            ),
            "severity": "info",
        })

    # Speed analysis
    if time_a > 0 and time_b > 0:
        if time_a < time_b and time_b > 0:
            ratio = time_b / time_a
            if ratio > 2:
                insights.append({
                    "icon": "🚀",
                    "title": f"{lang_a} was {ratio:.1f}x faster",
                    "description": (
                        f"{lang_a} completed in {time_a:.1f}ms vs "
                        f"{lang_b}'s {time_b:.1f}ms. "
                        f"{'Compiled code avoids interpreter overhead.' if lang_a in _COMPILED_LANGS else 'This may be due to algorithmic differences or runtime optimizations.'}"
                    ),
                    "severity": "success",
                })
        elif time_b < time_a and time_a > 0:
            ratio = time_a / time_b
            if ratio > 2:
                insights.append({
                    "icon": "🚀",
                    "title": f"{lang_b} was {ratio:.1f}x faster",
                    "description": (
                        f"{lang_b} completed in {time_b:.1f}ms vs "
                        f"{lang_a}'s {time_a:.1f}ms. "
                        f"{'Compiled code avoids interpreter overhead.' if lang_b in _COMPILED_LANGS else 'This may be due to algorithmic differences or runtime optimizations.'}"
                    ),
                    "severity": "success",
                })

    # Memory analysis
    if mem_a > 0 and mem_b > 0:
        if mem_a > mem_b * 2:
            insights.append({
                "icon": "💾",
                "title": f"{lang_a} uses more memory",
                "description": (
                    f"{lang_a} used {mem_a:.0f} KB vs {lang_b}'s {mem_b:.0f} KB. "
                    f"{'Interpreted languages carry runtime/interpreter overhead.' if lang_a in _INTERPRETED_LANGS else 'This may be due to different data structure sizes.'}"
                ),
                "severity": "warning",
            })
        elif mem_b > mem_a * 2:
            insights.append({
                "icon": "💾",
                "title": f"{lang_b} uses more memory",
                "description": (
                    f"{lang_b} used {mem_b:.0f} KB vs {lang_a}'s {mem_a:.0f} KB. "
                    f"{'Interpreted languages carry runtime/interpreter overhead.' if lang_b in _INTERPRETED_LANGS else 'This may be due to different data structure sizes.'}"
                ),
                "severity": "warning",
            })

    # Python-specific note about tracing
    if lang_a == "Python" or lang_b == "Python":
        py_lang = lang_a if lang_a == "Python" else lang_b
        other_lang = lang_b if lang_a == "Python" else lang_a
        insights.append({
            "icon": "🐍",
            "title": "Python includes step-level tracing",
            "description": (
                f"PyScope traces every line of {py_lang} code with full "
                f"variable state. {other_lang} runs via subprocess without "
                "tracing, so its timing reflects pure execution speed."
            ),
            "severity": "info",
        })

    # Java JVM startup overhead
    if "Java" in (lang_a, lang_b):
        insights.append({
            "icon": "☕",
            "title": "Java JVM startup overhead",
            "description": (
                "Java's execution time includes JVM startup cost (~200-500ms). "
                "For short programs, this dominates the measurement. "
                "In production, JIT compilation makes Java competitive with C++."
            ),
            "severity": "info",
        })

    # JavaScript V8 note
    if "JavaScript" in (lang_a, lang_b):
        insights.append({
            "icon": "⚡",
            "title": "JavaScript V8 JIT compilation",
            "description": (
                "Node.js uses the V8 engine with JIT compilation, which can "
                "optimise hot loops to near-native speed. Short scripts may "
                "not benefit from this optimisation."
            ),
            "severity": "info",
        })

    return insights
