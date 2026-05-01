"""
PyScope — Graph Utilities
==========================
Matplotlib-based graph builders for overview, individual metrics,
and comparison charts.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# THEME HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _get_chart_colors(mode: str) -> dict:
    """Return a dict of chart-related colors for the given mode."""
    dark = mode == "dark"
    return {
        "fig_bg":  "#0f1117" if dark else "#f8f9fb",
        "ax_bg":   "#0f1117" if dark else "#f8f9fb",
        "grid":    "#2a2b3d" if dark else "#e2e4ea",
        "tick":    "#6b6d82" if dark else "#9ea0b8",
        "title":   "#e2e4f0" if dark else "#1a1b26",
        "label":   "#6b6d82" if dark else "#9ea0b8",
        "spine":   "#2a2b3d" if dark else "#e2e4ea",
        "accent":  "#7c6aef",
        "colors":  ["#818cf8", "#34d399", "#38bdf8", "#fb923c"],
    }


def _style_ax(ax, c: dict):
    """Apply common styling to an axes object."""
    ax.set_facecolor(c["ax_bg"])
    for sp in ax.spines.values():
        sp.set_edgecolor(c["spine"])
    ax.tick_params(axis="both", colors=c["tick"], labelsize=7)
    ax.grid(True, color=c["grid"], linewidth=0.3, linestyle="-", alpha=0.5)


# ─────────────────────────────────────────────────────────────────────────────
# OVERVIEW GRAPH (4 subplots)
# ─────────────────────────────────────────────────────────────────────────────
def build_graphs(time_pts, mem_pts, cpu_pts, gpu_pts, step_pts,
                 mode="dark", gpu_name="GPU"):
    """Returns a matplotlib Figure with four clean subplots (overview)."""
    c = _get_chart_colors(mode)

    titles = [
        "Memory  (KB)",
        "CPU  (%)",
        f"GPU  —  {gpu_name}",
        "Steps",
    ]
    ylabels = ["KB", "%", "%", "#"]
    data = [mem_pts, cpu_pts, gpu_pts, step_pts]
    colors = c["colors"]

    fig, axes = plt.subplots(4, 1, figsize=(9, 8.5))
    fig.patch.set_facecolor(c["fig_bg"])

    for ax, title, ylabel, color, ydata in zip(axes, titles, ylabels, colors, data):
        _style_ax(ax, c)

        if len(time_pts) > 1:
            ax.fill_between(time_pts, ydata, alpha=0.08, color=color)
            ax.plot(time_pts, ydata, color=color, linewidth=1.4)
        else:
            ax.text(0.5, 0.5, "Insufficient data",
                    ha="center", va="center", color=c["tick"],
                    transform=ax.transAxes, fontsize=9,
                    fontfamily="sans-serif")

        ax.set_title(title, color=c["title"], fontsize=9.5, fontweight="500",
                     pad=6, loc="left", fontfamily="sans-serif")
        ax.set_xlabel("Time (s)", color=c["label"], fontsize=7.5,
                      fontfamily="sans-serif")
        ax.set_ylabel(ylabel, color=c["label"], fontsize=7.5,
                      fontfamily="sans-serif")

    fig.tight_layout(pad=2.0)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SINGLE METRIC GRAPH (for popup / dialog)
# ─────────────────────────────────────────────────────────────────────────────
def build_single_graph(time_pts, data_pts, title: str, ylabel: str,
                       color: str = "#818cf8", mode: str = "dark"):
    """
    Returns a matplotlib Figure with a single, larger metric chart.
    Includes min/max/avg annotations and gradient fill.
    """
    c = _get_chart_colors(mode)

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    fig.patch.set_facecolor(c["fig_bg"])
    _style_ax(ax, c)

    if len(time_pts) > 1 and len(data_pts) > 1:
        ax.fill_between(time_pts, data_pts, alpha=0.1, color=color)
        ax.plot(time_pts, data_pts, color=color, linewidth=2, zorder=5)

        # Annotations: min, max, avg
        arr = np.array(data_pts)
        avg_val = np.mean(arr)
        min_val = np.min(arr)
        max_val = np.max(arr)

        ax.axhline(y=avg_val, color=color, linewidth=0.8, linestyle="--",
                    alpha=0.5, zorder=3)

        # Add text annotations
        text_props = dict(fontsize=8, fontfamily="sans-serif",
                          color=c["title"], alpha=0.8)
        ax.text(time_pts[-1], avg_val, f"  avg: {avg_val:.1f}",
                va="center", **text_props)

        # Mark min and max points
        min_idx = int(np.argmin(arr))
        max_idx = int(np.argmax(arr))
        ax.scatter([time_pts[min_idx]], [min_val], color="#34d399",
                   s=30, zorder=10, edgecolors="white", linewidth=0.5)
        ax.scatter([time_pts[max_idx]], [max_val], color="#f87171",
                   s=30, zorder=10, edgecolors="white", linewidth=0.5)

        ax.annotate(f"min: {min_val:.1f}",
                    xy=(time_pts[min_idx], min_val),
                    xytext=(5, -15), textcoords="offset points",
                    fontsize=7, color="#34d399", fontfamily="sans-serif")
        ax.annotate(f"max: {max_val:.1f}",
                    xy=(time_pts[max_idx], max_val),
                    xytext=(5, 10), textcoords="offset points",
                    fontsize=7, color="#f87171", fontfamily="sans-serif")
    else:
        ax.text(0.5, 0.5, "Insufficient data",
                ha="center", va="center", color=c["tick"],
                transform=ax.transAxes, fontsize=11,
                fontfamily="sans-serif")

    ax.set_title(title, color=c["title"], fontsize=12, fontweight="600",
                 pad=10, loc="left", fontfamily="sans-serif")
    ax.set_xlabel("Time (s)", color=c["label"], fontsize=9,
                  fontfamily="sans-serif")
    ax.set_ylabel(ylabel, color=c["label"], fontsize=9,
                  fontfamily="sans-serif")

    fig.tight_layout(pad=1.5)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# COMPARISON BAR CHART
# ─────────────────────────────────────────────────────────────────────────────
def build_comparison_chart(details: list, mode: str = "dark",
                           label_a: str = "Program A",
                           label_b: str = "Program B"):
    """
    Build a grouped bar chart comparing Program A vs Program B.

    `details` is a list of:
        {"metric": str, "a": float, "b": float, "better": "A"|"B"|"Tie", "unit": str}
    """
    c = _get_chart_colors(mode)

    metrics = [d["metric"] for d in details]
    a_vals = [d["a"] for d in details]
    b_vals = [d["b"] for d in details]

    x = np.arange(len(metrics))
    width = 0.32

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    fig.patch.set_facecolor(c["fig_bg"])
    _style_ax(ax, c)

    bars_a = ax.bar(x - width / 2, a_vals, width, label=label_a,
                    color="#818cf8", alpha=0.85, edgecolor="none",
                    zorder=5, linewidth=0)
    bars_b = ax.bar(x + width / 2, b_vals, width, label=label_b,
                    color="#34d399", alpha=0.85, edgecolor="none",
                    zorder=5, linewidth=0)

    # Add value labels on bars
    for bar, val in zip(bars_a, a_vals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{val:.1f}", ha="center", va="bottom",
                    fontsize=7, color=c["title"], fontfamily="sans-serif")

    for bar, val in zip(bars_b, b_vals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{val:.1f}", ha="center", va="bottom",
                    fontsize=7, color=c["title"], fontfamily="sans-serif")

    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=8, color=c["title"],
                       fontfamily="sans-serif")
    ax.set_title("Performance Comparison", color=c["title"], fontsize=12,
                 fontweight="600", pad=10, loc="left", fontfamily="sans-serif")
    ax.legend(fontsize=8, loc="upper right",
              facecolor=c["fig_bg"], edgecolor=c["spine"],
              labelcolor=c["title"])

    fig.tight_layout(pad=1.5)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY BAR CHART (for non-Python languages with no time-series data)
# ─────────────────────────────────────────────────────────────────────────────
def build_summary_chart(stats: dict, mode: str = "dark"):
    """
    Build a summary bar chart showing key metrics from a single execution.
    Used when there are no time-series data points (non-Python languages).
    """
    c = _get_chart_colors(mode)

    exec_ms = (stats.get("execution_time", 0) or 0) * 1000
    peak_mem = stats.get("peak_memory_kb", 0) or 0
    cpu = stats.get("cpu_percent", 0) or 0
    gpu = stats.get("gpu_percent", 0) or 0
    language = stats.get("language", "Code")

    labels = ["Time (ms)", "Memory (KB)", "CPU (%)", "GPU (%)"]
    values = [exec_ms, peak_mem, cpu, gpu]
    colors = c["colors"]  # 4 accent colors

    fig, ax = plt.subplots(1, 1, figsize=(8, 4))
    fig.patch.set_facecolor(c["fig_bg"])
    _style_ax(ax, c)

    x = np.arange(len(labels))
    bars = ax.bar(x, values, 0.5, color=colors, alpha=0.85,
                  edgecolor="none", zorder=5)

    # Value labels on bars
    for bar, val in zip(bars, values):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{val:.1f}", ha="center", va="bottom",
                    fontsize=8, color=c["title"], fontfamily="sans-serif")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9, color=c["title"],
                       fontfamily="sans-serif")
    ax.set_title(f"{language} — Execution Summary", color=c["title"],
                 fontsize=12, fontweight="600", pad=10, loc="left",
                 fontfamily="sans-serif")

    fig.tight_layout(pad=1.5)
    return fig
