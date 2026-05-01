"""
PyScope — UI Components
========================
HTML render helpers consumed by app.py.  All output is a single HTML string
designed for st.markdown(unsafe_allow_html=True).
"""

import html


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def _esc(s) -> str:
    """HTML-escape a value, coercing to str."""
    return html.escape(str(s), quote=False)


def _fmt_num(value: float, digits: int = 1) -> str:
    """Format a number with thousands separators and a fixed decimal width."""
    if value is None:
        return "—"
    try:
        if isinstance(value, int) or float(value).is_integer():
            return f"{int(value):,}"
        return f"{float(value):,.{digits}f}"
    except (ValueError, TypeError):
        return str(value)


# ─────────────────────────────────────────────────────────────────────────────
# LANDING PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_landing_page() -> str:
    return (
        '<div class="landing">'
        '<div class="landing-glow landing-glow-1"></div>'
        '<div class="landing-glow landing-glow-2"></div>'
        '<div class="landing-inner">'
        '  <div class="landing-brand">'
        '    <div class="landing-logo">'
        '      <svg width="36" height="36" viewBox="0 0 48 48" fill="none">'
        '        <defs><linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48">'
        '          <stop offset="0%" stop-color="#818cf8"/>'
        '          <stop offset="100%" stop-color="#6366f1"/>'
        '        </linearGradient></defs>'
        '        <path d="M24 2L44 13.5V36.5L24 48L4 36.5V13.5L24 2Z" fill="url(#logoGrad)" opacity="0.15"/>'
        '        <path d="M24 6L40 15.5V32.5L24 42L8 32.5V15.5L24 6Z" stroke="url(#logoGrad)" stroke-width="1.5" fill="none"/>'
        '        <path d="M18 18L14 24L18 30" stroke="#818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        '        <path d="M30 18L34 24L30 30" stroke="#818cf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
        '        <path d="M26 16L22 32" stroke="#a5b4fc" stroke-width="1.5" stroke-linecap="round"/>'
        '      </svg>'
        '    </div>'
        '    <span class="landing-brand-name">PyScope</span>'
        '    <div class="landing-badge"><span class="dot"></span><span>v5</span></div>'
        '  </div>'
        '  <h1 class="landing-title">Trace. Profile.<br/><span class="landing-title-accent">Understand.</span></h1>'
        '  <p class="landing-subtitle">'
        '    Paste any Python code, run it, and get a full execution trace'
        '    with live CPU, RAM &amp; GPU profiling — plus actionable insights.'
        '  </p>'
        '  <div class="landing-section-label">How it works</div>'
        '  <div class="landing-steps">'
        '    <div class="landing-step">'
        '      <div class="landing-step-num">1</div>'
        '      <div class="landing-step-body">'
        '        <div class="landing-step-title">Write or paste code</div>'
        '        <div class="landing-step-desc">Use the built-in editor or load any .py file from your project</div>'
        '      </div>'
        '    </div>'
        '    <div class="landing-step">'
        '      <div class="landing-step-num">2</div>'
        '      <div class="landing-step-body">'
        '        <div class="landing-step-title">Run &amp; trace execution</div>'
        '        <div class="landing-step-desc">Every line is traced with variables, call depth, and timing</div>'
        '      </div>'
        '    </div>'
        '    <div class="landing-step">'
        '      <div class="landing-step-num">3</div>'
        '      <div class="landing-step-body">'
        '        <div class="landing-step-title">Analyze resources</div>'
        '        <div class="landing-step-desc">See CPU, memory, and GPU usage over time with interactive graphs</div>'
        '      </div>'
        '    </div>'
        '    <div class="landing-step">'
        '      <div class="landing-step-num">4</div>'
        '      <div class="landing-step-body">'
        '        <div class="landing-step-title">Read insights &amp; optimize</div>'
        '        <div class="landing-step-desc">Get auto-generated tips on recursion depth, memory, and complexity</div>'
        '      </div>'
        '    </div>'
        '  </div>'
        '  <div class="landing-trust">'
        '    <span>⚡ Instant analysis</span>'
        '    <span class="landing-trust-dot"></span>'
        '    <span>🔒 Runs locally</span>'
        '    <span class="landing-trust-dot"></span>'
        '    <span>📊 Side-by-side compare</span>'
        '  </div>'
        '</div>'
        '</div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────────────────────────────────────
def render_header() -> str:
    return """
    <div class="header">
      <div class="header-mark">
        <svg width="22" height="22" viewBox="0 0 48 48" fill="none">
          <defs>
            <linearGradient id="hLogoGrad" x1="0" y1="0" x2="48" y2="48">
              <stop offset="0%" stop-color="#818cf8"/>
              <stop offset="100%" stop-color="#6366f1"/>
            </linearGradient>
          </defs>
          <path d="M24 2L44 13.5V36.5L24 48L4 36.5V13.5L24 2Z" fill="url(#hLogoGrad)" opacity="0.2"/>
          <path d="M24 6L40 15.5V32.5L24 42L8 32.5V15.5L24 6Z" stroke="url(#hLogoGrad)" stroke-width="2" fill="none"/>
          <path d="M18 18L14 24L18 30" stroke="#818cf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M30 18L34 24L30 30" stroke="#818cf8" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="header-title">PyScope</div>
      <div class="header-sub">Execution tracer<br/>and profiler</div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# FILE EXPLORER
# ─────────────────────────────────────────────────────────────────────────────
def render_file_explorer(py_files: list, active_file: str) -> str:
    items = ['<div class="fx-list">']

    # Scratch entry
    scratch_active = "active" if active_file == "✦ scratch" else ""
    items.append(
        f'<div class="fx-item {scratch_active}">'
        f'<span class="fx-icon">✦</span><span>scratch</span></div>'
    )

    if py_files:
        for f in py_files:
            cls = "active" if f == active_file else ""
            items.append(
                f'<div class="fx-item {cls}">'
                f'<span class="fx-icon">›</span><span>{_esc(f)}</span></div>'
            )
    else:
        items.append('<div class="fx-empty">No .py files</div>')

    items.append("</div>")

    return f"""
    <div class="fx">
      <div class="fx-head">
        <span>Files</span>
        <span class="fx-count">{len(py_files)}</span>
      </div>
      {''.join(items)}
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# CODE DISPLAY (line-numbered with active-line highlight)
# ─────────────────────────────────────────────────────────────────────────────
def render_code_display(code: str, highlight_line: int = -1,
                        filename: str = "") -> str:
    lines = code.splitlines() or [""]
    rows = []
    for idx, src in enumerate(lines, 1):
        hl = "hl" if idx == highlight_line else ""
        # Preserve leading whitespace via &nbsp;
        rendered = _esc(src).replace(" ", "&nbsp;") if src else "&nbsp;"
        rows.append(
            f'<div class="code-line {hl}">'
            f'<span class="ln">{idx}</span>'
            f'<span class="src">{rendered}</span>'
            f'</div>'
        )

    name = _esc(filename) if filename else "untitled"
    return f"""
    <div class="code-wrap">
      <div class="code-head">
        <div class="code-dots"><span></span><span></span><span></span></div>
        <span>{name}</span>
      </div>
      <div class="code-body">{''.join(rows)}</div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# STATS CARDS
# ─────────────────────────────────────────────────────────────────────────────
def render_stats_cards(stats: dict) -> str:
    exec_ms = (stats.get("execution_time", 0) or 0) * 1000
    total_steps = stats.get("total_steps", 0) or 0
    peak_mem = stats.get("peak_memory_kb", 0) or 0
    cpu = stats.get("cpu_percent", 0) or 0
    gpu = stats.get("gpu_percent", 0) or 0
    ram = stats.get("ram_percent", 0) or 0
    depth = stats.get("max_call_depth", 0) or 0

    cards = [
        {
            "label": "Time",
            "icon": "◷",
            "value": _fmt_num(exec_ms, 1),
            "unit": "ms",
            "sub": f"{total_steps:,} steps",
        },
        {
            "label": "Memory",
            "icon": "▣",
            "value": _fmt_num(peak_mem, 0),
            "unit": "KB",
            "sub": f"RAM {ram:.0f}%",
        },
        {
            "label": "CPU",
            "icon": "▰",
            "value": _fmt_num(cpu, 1),
            "unit": "%",
            "sub": f"depth {depth}",
        },
        {
            "label": "GPU",
            "icon": "▲",
            "value": _fmt_num(gpu, 1),
            "unit": "%",
            "sub": _esc(stats.get("gpu_name", "—"))[:18] or "—",
        },
    ]

    parts = ['<div class="stats">']
    for c in cards:
        parts.append(
            f'<div class="stat">'
            f'<div class="stat-label"><span class="stat-icon">{c["icon"]}</span>{c["label"]}</div>'
            f'<div class="stat-value">{c["value"]}<span class="stat-unit"> {c["unit"]}</span></div>'
            f'<div class="stat-sub">{c["sub"]}</div>'
            f'</div>'
        )
    parts.append('</div>')
    return ''.join(parts)


# ─────────────────────────────────────────────────────────────────────────────
# CONSOLE (stdout + error)
# ─────────────────────────────────────────────────────────────────────────────
def render_console(stdout_lines: list, error_msg: str = "",
                   status: str = "idle") -> str:
    tag_text = {"idle": "Idle", "success": "Success", "error": "Error"}.get(status, "Idle")

    if stdout_lines:
        body = "\n".join(_esc(l) for l in stdout_lines)
    else:
        body = '<span class="console-empty">No output yet — run your code to see stdout here.</span>'

    err_html = ""
    if error_msg:
        err_html = f'<div class="console-err">{_esc(error_msg)}</div>'

    return (
        '<div class="console">'
        f'<div class="console-head"><span>›_ Console</span>'
        f'<span class="console-tag {status}">{tag_text}</span></div>'
        f'<div class="console-body">{body}</div>'
        f'{err_html}'
        '</div>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# TRACE LOGS
# ─────────────────────────────────────────────────────────────────────────────
def render_logs(logs: list, upto: int = None) -> str:
    if not logs:
        return '<div class="trace"><div class="trace-empty">No trace yet.</div></div>'

    rows = []
    for entry in logs:
        kind = entry.get("kind", "")
        # Filter by step
        if upto is not None:
            step = entry.get("step")
            if kind == "line" and step is not None and step > upto:
                break

        if kind == "line":
            step = entry.get("step", "")
            line = entry.get("line", "")
            vars_ = entry.get("vars", {}) or {}
            vars_str = ", ".join(f"{_esc(k)}={_esc(v)}" for k, v in vars_.items())
            msg = f"<b>line</b> · {vars_str}" if vars_str else "<b>line</b>"
            rows.append(
                f'<div class="trace-row">'
                f'<span class="trace-step">step {step}</span>'
                f'<span class="trace-line">L{line}</span>'
                f'<span class="trace-msg">{msg}</span>'
                f'</div>'
            )
        elif kind == "call":
            depth = entry.get("depth", 1)
            indent = "› " * max(0, depth - 1)
            name = _esc(entry.get("name", ""))
            line = entry.get("line", "")
            rows.append(
                f'<div class="trace-row call">'
                f'<span class="trace-step">call</span>'
                f'<span class="trace-line">L{line}</span>'
                f'<span class="trace-msg">{indent}→ <b>{name}()</b></span>'
                f'</div>'
            )
        elif kind == "return":
            depth = entry.get("depth", 1)
            indent = "› " * max(0, depth - 1)
            name = _esc(entry.get("name", ""))
            value = _esc(entry.get("value", ""))
            line = entry.get("line", "")
            rows.append(
                f'<div class="trace-row return">'
                f'<span class="trace-step">ret</span>'
                f'<span class="trace-line">L{line}</span>'
                f'<span class="trace-msg">{indent}← <b>{name}</b> = {value}</span>'
                f'</div>'
            )

    if not rows:
        return '<div class="trace"><div class="trace-empty">No events at this step.</div></div>'

    return f'<div class="trace">{"".join(rows)}</div>'


# ─────────────────────────────────────────────────────────────────────────────
# VARIABLES (snapshot at a step)
# ─────────────────────────────────────────────────────────────────────────────
def render_variables(timeline: list, step: int) -> str:
    if not timeline:
        return '<div class="vars"><div class="vars-empty">No variables captured.</div></div>'

    # Find the most recent entry whose step <= requested step
    snapshot = None
    for entry in timeline:
        if entry.get("step", 0) <= step:
            snapshot = entry
        else:
            break
    if snapshot is None:
        snapshot = timeline[0]

    vars_ = snapshot.get("vars", {}) or {}
    if not vars_:
        return f"""
        <div class="vars">
          <div class="vars-meta">
            <span>Step <b>{snapshot.get('step', step)}</b></span>
            <span>Line <b>{snapshot.get('line', '—')}</b></span>
          </div>
          <div class="vars-empty">No user variables in scope.</div>
        </div>
        """

    rows = []
    for name, info in sorted(vars_.items()):
        rows.append(
            f'<tr>'
            f'<td class="v-name">{_esc(name)}</td>'
            f'<td class="v-type">{_esc(info.get("type", ""))}</td>'
            f'<td class="v-value">{_esc(info.get("value", ""))}</td>'
            f'</tr>'
        )

    return f"""
    <div class="vars">
      <div class="vars-meta">
        <span>Step <b>{snapshot.get('step', step)}</b> · {len(vars_)} variable{'s' if len(vars_) != 1 else ''}</span>
        <span>Line <b>{snapshot.get('line', '—')}</b></span>
      </div>
      <table class="vars-table">
        <thead><tr><th>Name</th><th>Type</th><th>Value</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# CALL STACK (recursive tree)
# ─────────────────────────────────────────────────────────────────────────────
def render_call_stack(call_tree: list) -> str:
    if not call_tree:
        return '<div class="stack"><div class="stack-empty">No function calls recorded.</div></div>'

    lines = []

    def _walk(node, prefix: str = "", is_last: bool = True):
        connector = "└─ " if is_last else "├─ "
        tree = _esc(prefix + connector)
        name = _esc(node.get("name", ""))
        line = node.get("line", "")
        ret = node.get("return_value")
        ret_html = f' <span class="stack-ret">→ {_esc(ret)}</span>' if ret is not None else ""
        line_html = f' <span class="stack-line">L{line}</span>' if line else ""
        lines.append(
            f'<div class="stack-node">'
            f'<span class="stack-tree">{tree}</span>'
            f'<span class="stack-fn">{name}()</span>{line_html}{ret_html}'
            f'</div>'
        )
        children = node.get("children", []) or []
        new_prefix = prefix + ("   " if is_last else "│  ")
        for i, child in enumerate(children):
            _walk(child, new_prefix, i == len(children) - 1)

    for i, root in enumerate(call_tree):
        _walk(root, "", i == len(call_tree) - 1)

    return f'<div class="stack">{"".join(lines)}</div>'


# ─────────────────────────────────────────────────────────────────────────────
# INSIGHTS
# ─────────────────────────────────────────────────────────────────────────────
def render_insights(insights: list) -> str:
    if not insights:
        return '<div class="insights"><div class="ins-empty">No insights — run code to generate analysis.</div></div>'

    cards = []
    for ins in insights:
        sev = ins.get("severity", "info")
        icon = _esc(ins.get("icon", "◆"))
        title = _esc(ins.get("title", ""))
        desc = _esc(ins.get("description", ""))
        cards.append(
            f'<div class="ins-card {sev}">'
            f'<div class="ins-icon">{icon}</div>'
            f'<div class="ins-body">'
            f'<div class="ins-title">{title}</div>'
            f'<div class="ins-desc">{desc}</div>'
            f'</div></div>'
        )
    return f'<div class="insights">{"".join(cards)}</div>'


# ─────────────────────────────────────────────────────────────────────────────
# COMPARISON TABLE + VERDICT
# ─────────────────────────────────────────────────────────────────────────────
def render_comparison_table(verdict: dict) -> str:
    if not verdict:
        return ""

    details = verdict.get("details", []) or []
    label_a = _esc(verdict.get("label_a", "Program A"))
    label_b = _esc(verdict.get("label_b", "Program B"))

    rows = []
    for d in details:
        metric = _esc(d.get("metric", ""))
        unit = _esc(d.get("unit", "") or "")
        a = _fmt_num(d.get("a", 0), 1)
        b = _fmt_num(d.get("b", 0), 1)
        better = d.get("better", "Tie")

        a_cls = "win" if better == "A" else ("lose" if better == "B" else "")
        b_cls = "win" if better == "B" else ("lose" if better == "A" else "")
        winner_cell = {
            "A": label_a,
            "B": label_b,
        }.get(better, "Tie")

        rows.append(
            f'<tr>'
            f'<td class="metric">{metric}</td>'
            f'<td class="{a_cls}">{a}{(" " + unit) if unit else ""}</td>'
            f'<td class="{b_cls}">{b}{(" " + unit) if unit else ""}</td>'
            f'<td>{winner_cell}</td>'
            f'</tr>'
        )

    winner = verdict.get("winner", "Tie")
    reason = _esc(verdict.get("reason", ""))
    if winner == "Tie":
        winner_label = '<span class="cmp-verdict-winner">Tie</span>'
    elif winner == "A":
        winner_label = f'<span class="cmp-verdict-winner">{label_a}</span> wins'
    else:
        winner_label = f'<span class="cmp-verdict-winner">{label_b}</span> wins'

    return (
        f'<div class="cmp-verdict">'
        f'<div class="cmp-verdict-title">Verdict</div>'
        f'<div class="cmp-verdict-body">{winner_label} — {reason}</div>'
        f'</div>'
        f'<table class="cmp-tbl">'
        f'<thead>'
        f'<tr><th>Metric</th><th>{label_a}</th><th>{label_b}</th><th>Winner</th></tr>'
        f'</thead>'
        f'<tbody>{"".join(rows)}</tbody>'
        f'</table>'
    )
