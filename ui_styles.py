"""
PyScope — UI Styles
====================
Linear-inspired premium CSS. One token system, two themes (dark/light).
All spacing on an 8px scale; all radii on an 8px scale; transitions 0.2s.
"""


# ─────────────────────────────────────────────────────────────────────────────
# THEME TOKENS
# ─────────────────────────────────────────────────────────────────────────────
def _tokens(mode: str) -> dict:
    if mode == "dark":
        return {
            "bg":           "#0b0c0f",
            "bg_elev":      "#111317",
            "panel":        "#14161b",
            "panel_hover":  "#181a20",
            "border":       "rgba(255,255,255,0.06)",
            "border_str":   "rgba(255,255,255,0.10)",
            "text":         "#e6e7ea",
            "text_dim":     "#9396a3",
            "text_mute":    "#6b6d7a",
            "accent":       "#7c6aef",
            "accent_hov":   "#8b7af2",
            "accent_glow":  "rgba(124,106,239,0.18)",
            "success":      "#34d399",
            "warning":      "#fbbf24",
            "danger":       "#f87171",
            "info":         "#38bdf8",
            "code_bg":      "#0d0f13",
            "code_line_hl": "rgba(124,106,239,0.10)",
            "code_line_bd": "#7c6aef",
            "shadow_sm":    "0 1px 2px rgba(0,0,0,0.30)",
            "shadow_md":    "0 4px 12px rgba(0,0,0,0.35)",
            "shadow_lg":    "0 12px 32px rgba(0,0,0,0.45)",
            "scroll":       "rgba(255,255,255,0.10)",
        }
    return {
        "bg":           "#f8fafc",
        "bg_elev":      "#ffffff",
        "panel":        "#ffffff",
        "panel_hover":  "#f1f3f5",
        "border":       "rgba(15,17,21,0.08)",
        "border_str":   "rgba(15,17,21,0.14)",
        "text":         "#1a1d2e",
        "text_dim":     "#4b5066",
        "text_mute":    "#8b8fa3",
        "accent":       "#5e6ad2",
        "accent_hov":   "#4b56c2",
        "accent_glow":  "rgba(94,106,210,0.14)",
        "success":      "#10b981",
        "warning":      "#d97706",
        "danger":       "#dc2626",
        "info":         "#0284c7",
        "code_bg":      "#f3f4f7",
        "code_line_hl": "rgba(94,106,210,0.10)",
        "code_line_bd": "#5e6ad2",
        "shadow_sm":    "0 1px 3px rgba(15,17,21,0.06)",
        "shadow_md":    "0 4px 12px rgba(15,17,21,0.08)",
        "shadow_lg":    "0 12px 32px rgba(15,17,21,0.12)",
        "scroll":       "rgba(15,17,21,0.18)",
    }


# ─────────────────────────────────────────────────────────────────────────────
# CSS BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def get_css(mode: str = "dark") -> str:
    t = _tokens(mode)

    return f"""
<style>
/* ═══════════════════════════════════════════════════════════════════════════
   GLOBAL — fonts, reset, base
   ═══════════════════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: {t['text']};
}}

.stApp {{
    background: {t['bg']};
    background-image: radial-gradient(ellipse at 50% 0%, { 'rgba(129,140,248,0.06)' if mode == 'dark' else 'rgba(99,102,241,0.04)' } 0%, transparent 60%);
    color: {t['text']};
}}

/* Hide Streamlit chrome */
#MainMenu, header[data-testid="stHeader"], footer, .stDeployButton,
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {{
    display: none !important;
}}

/* Tighten the main container */
.block-container {{
    padding: 1.25rem 1.75rem 2rem !important;
    max-width: 100% !important;
}}

/* Custom scrollbars */
::-webkit-scrollbar {{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: {t['scroll']};
    border-radius: 8px;
    border: 2px solid transparent;
    background-clip: padding-box;
}}
::-webkit-scrollbar-thumb:hover {{ background: {t['border_str']}; background-clip: padding-box; }}

/* Selection */
::selection {{ background: {t['accent_glow']}; color: {t['text']}; }}

/* ═══════════════════════════════════════════════════════════════════════════
   ANIMATIONS
   ═══════════════════════════════════════════════════════════════════════════ */
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to   {{ opacity: 1; }}
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(8px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes scaleIn {{
    from {{ opacity: 0; transform: scale(0.96); }}
    to   {{ opacity: 1; transform: scale(1); }}
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50%      {{ opacity: 0.55; }}
}}
@keyframes spin {{
    to {{ transform: rotate(360deg); }}
}}

.stApp > div {{ animation: fadeIn 0.25s ease-out; }}

/* ═══════════════════════════════════════════════════════════════════════════
   STREAMLIT COMPONENT OVERRIDES
   ═══════════════════════════════════════════════════════════════════════════ */

/* Buttons */
.stButton > button {{
    background: {t['panel']};
    color: {t['text']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    padding: 0.5rem 0.95rem;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: -0.01em;
    transition: all 0.18s ease;
    box-shadow: {t['shadow_sm']};
    line-height: 1.2;
}}
.stButton > button:hover {{
    background: {t['panel_hover']};
    border-color: {t['border_str']};
    transform: translateY(-1px);
    box-shadow: {t['shadow_md']};
}}
.stButton > button:active {{
    transform: translateY(0);
}}
.stButton > button:focus,
.stButton > button:focus-visible {{
    outline: none;
    box-shadow: 0 0 0 3px {t['accent_glow']};
    border-color: {t['accent']};
}}

/* Primary "Run" button (wrapped in .run-btn) */
.run-btn .stButton > button {{
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
    color: #ffffff;
    border: 1px solid rgba(129,140,248,0.5);
    box-shadow: 0 1px 0 rgba(255,255,255,0.12) inset, 0 4px 16px rgba(99,102,241,0.3);
    font-weight: 600;
    letter-spacing: -0.01em;
}}
.run-btn .stButton > button:hover {{
    filter: brightness(1.1);
    transform: translateY(-2px);
    box-shadow: 0 1px 0 rgba(255,255,255,0.15) inset, 0 8px 24px rgba(99,102,241,0.4);
}}

/* Text area / code editor */
.stTextArea textarea {{
    background: {t['code_bg']} !important;
    color: {t['text']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 10px !important;
    font-family: 'JetBrains Mono', ui-monospace, Menlo, Consolas, monospace !important;
    font-size: 13.5px !important;
    line-height: 1.65 !important;
    padding: 0.85rem 1rem !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
    caret-color: {t['accent']};
}}
.stTextArea textarea:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
    outline: none !important;
}}
.stTextArea label {{ display: none !important; }}

/* Selectbox */
div[data-baseweb="select"] > div {{
    background: {t['panel']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    min-height: 36px !important;
    transition: border-color 0.18s ease;
}}
div[data-baseweb="select"] > div:hover {{
    border-color: {t['border_str']} !important;
}}
div[data-baseweb="select"] [data-baseweb="tag"] {{ background: {t['accent_glow']} !important; }}

/* Slider */
.stSlider [data-baseweb="slider"] {{ padding-top: 0.4rem; }}
.stSlider [role="slider"] {{
    background: {t['accent']} !important;
    border: 2px solid {t['bg']} !important;
    box-shadow: 0 0 0 1px {t['accent']}, 0 2px 8px {t['accent_glow']};
    height: 16px !important;
    width: 16px !important;
}}
.stSlider [data-baseweb="slider"] > div > div > div {{ background: {t['accent']} !important; }}
.stSlider label {{ color: {t['text_dim']}; font-size: 12px; font-weight: 500; }}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {{
    gap: 4px;
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 0.6rem;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent;
    color: {t['text_dim']};
    border-radius: 7px;
    padding: 0.45rem 0.85rem;
    font-size: 12.5px;
    font-weight: 500;
    border: 1px solid transparent;
    transition: all 0.15s ease;
}}
.stTabs [data-baseweb="tab"]:hover {{
    background: {t['panel_hover']};
    color: {t['text']};
}}
.stTabs [aria-selected="true"] {{
    background: {t['panel']} !important;
    color: {t['text']} !important;
    border-color: {t['border_str']} !important;
    box-shadow: {t['shadow_sm']};
}}
.stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}
.stTabs [data-baseweb="tab-panel"] {{ padding-top: 0.4rem; animation: fadeIn 0.2s ease; }}

/* Toggle */
[data-testid="stWidgetLabel"] p {{ font-size: 12px; color: {t['text_dim']}; }}

/* Dialog (graph popup) */
div[role="dialog"] {{
    background: {t['bg_elev']} !important;
    border: 1px solid {t['border_str']} !important;
    border-radius: 14px !important;
    box-shadow: {t['shadow_lg']} !important;
    animation: scaleIn 0.18s ease-out;
}}

/* Warning / info boxes */
.stAlert {{
    border-radius: 10px;
    border: 1px solid {t['border']};
    background: {t['panel']};
}}

/* ═══════════════════════════════════════════════════════════════════════════
   SECTION LABEL
   ═══════════════════════════════════════════════════════════════════════════ */
.sec {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: {t['text_mute']};
    margin: 0.4rem 0 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}}
.sec::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: {t['border']};
}}

/* ═══════════════════════════════════════════════════════════════════════════
   LANDING PAGE
   ═══════════════════════════════════════════════════════════════════════════ */
.landing {{
    position: relative;
    overflow: hidden;
    padding: 2rem 1rem 0.5rem;
    animation: fadeIn 0.35s ease-out;
}}

/* Centered anchoring container */
.landing-inner {{
    max-width: 760px;
    margin: 0 auto;
    position: relative;
    z-index: 1;
}}

/* Subtle background glows */
.landing-glow {{
    position: absolute;
    border-radius: 50%;
    filter: blur(90px);
    pointer-events: none;
    z-index: 0;
}}
.landing-glow-1 {{
    width: 380px; height: 380px;
    top: -100px; left: 50%;
    transform: translateX(-65%);
    background: radial-gradient(circle, { 'rgba(129,140,248,0.13)' if mode == 'dark' else 'rgba(99,102,241,0.07)' } 0%, transparent 70%);
}}
.landing-glow-2 {{
    width: 300px; height: 300px;
    top: 60px; left: 50%;
    transform: translateX(30%);
    background: radial-gradient(circle, { 'rgba(99,102,241,0.09)' if mode == 'dark' else 'rgba(99,102,241,0.05)' } 0%, transparent 70%);
}}

/* Brand row */
.landing-brand {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.6rem;
}}
.landing-logo {{
    width: 36px; height: 36px;
    display: grid;
    place-items: center;
    flex-shrink: 0;
}}
.landing-brand-name {{
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #818cf8, #6366f1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* Badge — inline with brand */
.landing-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.2rem 0.6rem;
    background: {t['panel']};
    border: 1px solid {t['border_str']};
    border-radius: 100px;
    font-size: 10.5px;
    font-weight: 500;
    color: {t['text_mute']};
    margin-left: 0.3rem;
}}
.landing-badge .dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #34d399;
    box-shadow: 0 0 0 3px rgba(52,211,153,0.18);
    animation: pulse 2.4s ease infinite;
}}

/* Hero title */
.landing-title {{
    font-size: 46px;
    font-weight: 800;
    letter-spacing: -0.04em;
    line-height: 1.1;
    margin: 0 0 0.75rem;
    color: {t['text']};
}}
.landing-title-accent {{
    background: linear-gradient(135deg, #818cf8 0%, #6366f1 50%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}

/* Subtitle */
.landing-subtitle {{
    font-size: 15.5px;
    color: {t['text_dim']};
    margin: 0 0 2rem;
    max-width: 540px;
    line-height: 1.6;
}}

/* Section label */
.landing-section-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: {t['text_mute']};
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}}
.landing-section-label::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: {t['border']};
}}

/* Step cards — vertical list */
.landing-steps {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 1.6rem;
}}
.landing-step {{
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    padding: 0.85rem 1rem;
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    transition: border-color 0.18s ease, box-shadow 0.18s ease;
    animation: slideUp 0.35s ease both;
}}
.landing-step:nth-child(1) {{ animation-delay: 0.03s; }}
.landing-step:nth-child(2) {{ animation-delay: 0.07s; }}
.landing-step:nth-child(3) {{ animation-delay: 0.11s; }}
.landing-step:nth-child(4) {{ animation-delay: 0.15s; }}
.landing-step:hover {{
    border-color: { 'rgba(129,140,248,0.25)' if mode == 'dark' else 'rgba(99,102,241,0.2)' };
    box-shadow: {t['shadow_sm']};
}}
.landing-step-num {{
    width: 28px; height: 28px;
    border-radius: 8px;
    background: linear-gradient(135deg, rgba(129,140,248,0.15), rgba(99,102,241,0.08));
    color: #818cf8;
    display: grid;
    place-items: center;
    font-size: 12.5px;
    font-weight: 700;
    flex-shrink: 0;
    margin-top: 1px;
    border: 1px solid { 'rgba(129,140,248,0.15)' if mode == 'dark' else 'rgba(99,102,241,0.12)' };
}}
.landing-step-title {{
    font-size: 13.5px;
    font-weight: 600;
    color: {t['text']};
    margin-bottom: 2px;
    letter-spacing: -0.01em;
}}
.landing-step-desc {{
    font-size: 12px;
    color: {t['text_dim']};
    line-height: 1.45;
}}

/* Trust bar */
.landing-trust {{
    display: flex;
    align-items: center;
    gap: 0.75rem;
    color: {t['text_mute']};
    font-size: 11.5px;
    font-weight: 500;
}}
.landing-trust-dot {{
    width: 3px; height: 3px;
    border-radius: 50%;
    background: {t['text_mute']};
    opacity: 0.45;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   HEADER
   ═══════════════════════════════════════════════════════════════════════════ */
.header {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.2rem 0 1rem;
}}
.header-mark {{
    width: 34px; height: 34px;
    border-radius: 9px;
    background: linear-gradient(135deg, rgba(129,140,248,0.15), rgba(99,102,241,0.08));
    display: grid;
    place-items: center;
    box-shadow: 0 4px 10px rgba(129,140,248,0.15);
    border: 1px solid rgba(129,140,248,0.2);
}}
.header-title {{
    font-size: 16px;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #818cf8, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.header-sub {{
    font-size: 11.5px;
    color: {t['text_mute']};
    margin-left: 0.55rem;
    padding-left: 0.7rem;
    border-left: 1px solid {t['border']};
    line-height: 1.2;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   FILE EXPLORER
   ═══════════════════════════════════════════════════════════════════════════ */
.fx {{
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    padding: 0.55rem 0.4rem;
    margin-bottom: 0.5rem;
}}
.fx-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.15rem 0.5rem 0.5rem;
    font-size: 11px;
    font-weight: 600;
    color: {t['text_mute']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.fx-count {{
    background: {t['panel_hover']};
    color: {t['text_dim']};
    padding: 1px 7px;
    border-radius: 100px;
    font-size: 10.5px;
    font-weight: 600;
    letter-spacing: 0;
}}
.fx-list {{ display: flex; flex-direction: column; gap: 1px; }}
.fx-item {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 0.55rem;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: {t['text_dim']};
    cursor: default;
    transition: background 0.15s ease, color 0.15s ease;
}}
.fx-item:hover {{
    background: {t['panel_hover']};
    color: {t['text']};
}}
.fx-item.active {{
    background: {t['accent_glow']};
    color: {t['text']};
    font-weight: 500;
}}
.fx-item.active .fx-icon {{ color: {t['accent']}; }}
.fx-icon {{
    color: {t['text_mute']};
    font-size: 11px;
    width: 12px;
    flex-shrink: 0;
}}
.fx-empty {{
    padding: 0.6rem 0.55rem;
    font-size: 11.5px;
    color: {t['text_mute']};
    text-align: center;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   CODE DISPLAY (line-numbered, with active-line highlight)
   ═══════════════════════════════════════════════════════════════════════════ */
.code-wrap {{
    background: {t['code_bg']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    margin-top: 0.55rem;
    overflow: hidden;
    box-shadow: {t['shadow_sm']};
    animation: slideUp 0.25s ease;
}}
.code-head {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 0.85rem;
    background: {t['bg_elev']};
    border-bottom: 1px solid {t['border']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    color: {t['text_dim']};
}}
.code-dots {{ display: flex; gap: 5px; }}
.code-dots span {{ width: 9px; height: 9px; border-radius: 50%; background: {t['border_str']}; }}
.code-body {{
    margin: 0;
    padding: 0.6rem 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    line-height: 1.7;
    overflow-x: auto;
}}
.code-line {{
    display: flex;
    padding: 0 0.85rem;
    white-space: pre;
    border-left: 2px solid transparent;
}}
.code-line.hl {{
    background: {t['code_line_hl']};
    border-left-color: {t['code_line_bd']};
}}
.code-line .ln {{
    color: {t['text_mute']};
    user-select: none;
    width: 2.4rem;
    text-align: right;
    padding-right: 0.85rem;
    flex-shrink: 0;
}}
.code-line.hl .ln {{ color: {t['accent']}; font-weight: 600; }}
.code-line .src {{ color: {t['text']}; flex: 1; }}

/* ═══════════════════════════════════════════════════════════════════════════
   STATS CARDS
   ═══════════════════════════════════════════════════════════════════════════ */
.stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin: 0.4rem 0 0.6rem;
}}
.stat {{
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-top: 2px solid transparent;
    border-radius: 10px;
    padding: 0.7rem 0.85rem;
    transition: all 0.18s ease;
    animation: slideUp 0.3s ease both;
}}
.stat:nth-child(1) {{ animation-delay: 0.02s; border-top-color: #818cf8; }}
.stat:nth-child(2) {{ animation-delay: 0.06s; border-top-color: #34d399; }}
.stat:nth-child(3) {{ animation-delay: 0.10s; border-top-color: #38bdf8; }}
.stat:nth-child(4) {{ animation-delay: 0.14s; border-top-color: #fb923c; }}
.stat:hover {{
    border-color: rgba(129,140,248,0.3);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99,102,241,0.1), {t['shadow_md']};
}}
.stat-label {{
    font-size: 10.5px;
    font-weight: 600;
    color: {t['text_mute']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}}
.stat-icon {{ font-size: 11px; opacity: 0.85; }}
.stat-value {{
    margin-top: 0.25rem;
    font-size: 19px;
    font-weight: 600;
    color: {t['text']};
    letter-spacing: -0.02em;
    font-variant-numeric: tabular-nums;
    line-height: 1.15;
}}
.stat-unit {{
    font-size: 11px;
    color: {t['text_mute']};
    font-weight: 500;
    margin-left: 2px;
}}
.stat-sub {{
    font-size: 10.5px;
    color: {t['text_mute']};
    margin-top: 1px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   STATUS PILL  /  STEP BADGE
   ═══════════════════════════════════════════════════════════════════════════ */
.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.28rem 0.7rem;
    border-radius: 100px;
    font-size: 11.5px;
    font-weight: 500;
    border: 1px solid transparent;
    margin-bottom: 0.4rem;
    animation: fadeIn 0.25s ease;
}}
.status-pill.success {{
    background: {t['success']}14;
    color: {t['success']};
    border-color: {t['success']}30;
}}
.status-pill.error {{
    background: {t['danger']}14;
    color: {t['danger']};
    border-color: {t['danger']}30;
}}
.status-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    background: currentColor;
    box-shadow: 0 0 0 3px currentColor;
    opacity: 0.95;
}}
.status-pill .status-dot {{ box-shadow: 0 0 0 3px {t['accent_glow']}; }}
.step-badge {{
    text-align: center;
    padding: 0.45rem 0.5rem;
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-radius: 8px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    color: {t['text_dim']};
}}

/* ═══════════════════════════════════════════════════════════════════════════
   CONSOLE
   ═══════════════════════════════════════════════════════════════════════════ */
.console {{
    margin-top: 0.85rem;
    background: {t['code_bg']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    overflow: hidden;
    animation: slideUp 0.25s ease;
}}
.console-head {{
    display: flex;
    align-items: center;
    gap: 0.55rem;
    padding: 0.45rem 0.85rem;
    background: {t['bg_elev']};
    border-bottom: 1px solid {t['border']};
    font-size: 11px;
    font-weight: 600;
    color: {t['text_mute']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.console-tag {{
    margin-left: auto;
    text-transform: none;
    letter-spacing: 0;
    font-size: 10.5px;
    padding: 1px 8px;
    border-radius: 100px;
    font-weight: 500;
}}
.console-tag.idle    {{ background: {t['border']}; color: {t['text_mute']}; }}
.console-tag.success {{ background: {t['success']}18; color: {t['success']}; }}
.console-tag.error   {{ background: {t['danger']}18; color: {t['danger']}; }}
.console-body {{
    padding: 0.7rem 0.95rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    line-height: 1.65;
    color: {t['text']};
    max-height: 180px;
    overflow-y: auto;
    white-space: pre-wrap;
    word-break: break-word;
}}
.console-empty {{ color: {t['text_mute']}; font-style: italic; }}
.console-err {{
    color: {t['danger']};
    background: {t['danger']}10;
    border-top: 1px solid {t['danger']}30;
    padding: 0.65rem 0.95rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    white-space: pre-wrap;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   TRACE LOGS
   ═══════════════════════════════════════════════════════════════════════════ */
.trace {{
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    padding: 0.5rem;
    max-height: 360px;
    overflow-y: auto;
    animation: fadeIn 0.2s ease;
}}
.trace-row {{
    display: flex;
    align-items: baseline;
    gap: 0.55rem;
    padding: 0.28rem 0.55rem;
    border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    line-height: 1.45;
    transition: background 0.12s ease;
}}
.trace-row:hover {{ background: {t['panel_hover']}; }}
.trace-step {{
    color: {t['text_mute']};
    width: 3.6rem;
    flex-shrink: 0;
    font-variant-numeric: tabular-nums;
}}
.trace-line {{
    color: {t['accent']};
    font-weight: 500;
    width: 3.4rem;
    flex-shrink: 0;
}}
.trace-msg {{ color: {t['text_dim']}; flex: 1; }}
.trace-msg b {{ color: {t['text']}; font-weight: 500; }}
.trace-row.call .trace-msg    {{ color: {t['info']}; }}
.trace-row.return .trace-msg  {{ color: {t['success']}; }}
.trace-empty {{
    text-align: center;
    color: {t['text_mute']};
    padding: 2rem 0.6rem;
    font-size: 12.5px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   VARIABLES
   ═══════════════════════════════════════════════════════════════════════════ */
.vars {{
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    overflow: hidden;
    animation: fadeIn 0.2s ease;
}}
.vars-meta {{
    padding: 0.5rem 0.85rem;
    background: {t['panel_hover']};
    border-bottom: 1px solid {t['border']};
    font-size: 11.5px;
    color: {t['text_dim']};
    display: flex;
    justify-content: space-between;
}}
.vars-meta b {{ color: {t['text']}; font-weight: 500; }}
.vars-table {{ width: 100%; border-collapse: collapse; }}
.vars-table th, .vars-table td {{
    padding: 0.45rem 0.85rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    text-align: left;
    border-bottom: 1px solid {t['border']};
}}
.vars-table tr:last-child td {{ border-bottom: none; }}
.vars-table th {{
    color: {t['text_mute']};
    font-weight: 600;
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    background: transparent;
}}
.vars-table .v-name  {{ color: {t['text']}; font-weight: 500; }}
.vars-table .v-type  {{ color: {t['accent']}; font-size: 10.5px; }}
.vars-table .v-value {{ color: {t['text_dim']}; word-break: break-all; }}
.vars-empty {{
    padding: 1.5rem 0.85rem;
    text-align: center;
    color: {t['text_mute']};
    font-size: 12.5px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   CALL STACK
   ═══════════════════════════════════════════════════════════════════════════ */
.stack {{
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    padding: 0.7rem 0.85rem;
    max-height: 360px;
    overflow-y: auto;
    animation: fadeIn 0.2s ease;
}}
.stack-node {{
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
    padding: 0.22rem 0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    line-height: 1.5;
}}
.stack-tree {{
    color: {t['text_mute']};
    user-select: none;
    flex-shrink: 0;
}}
.stack-fn {{ color: {t['text']}; font-weight: 500; }}
.stack-ret {{ color: {t['success']}; opacity: 0.85; }}
.stack-line {{ color: {t['text_mute']}; font-size: 10.5px; }}
.stack-empty {{
    text-align: center;
    color: {t['text_mute']};
    padding: 1.5rem 0.6rem;
    font-size: 12.5px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   INSIGHTS
   ═══════════════════════════════════════════════════════════════════════════ */
.insights {{
    display: flex;
    flex-direction: column;
    gap: 8px;
    animation: fadeIn 0.2s ease;
}}
.ins-card {{
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-left: 3px solid {t['border_str']};
    border-radius: 8px;
    padding: 0.65rem 0.85rem;
    display: flex;
    gap: 0.7rem;
    transition: all 0.18s ease;
    animation: slideUp 0.3s ease both;
}}
.ins-card:hover {{
    border-color: {t['border_str']};
    transform: translateY(-1px);
    box-shadow: {t['shadow_sm']};
}}
.ins-card.success {{ border-left-color: {t['success']}; }}
.ins-card.info    {{ border-left-color: {t['info']}; }}
.ins-card.warning {{ border-left-color: {t['warning']}; }}
.ins-card.danger  {{ border-left-color: {t['danger']}; }}
.ins-icon {{ font-size: 18px; line-height: 1.3; flex-shrink: 0; }}
.ins-body {{ flex: 1; }}
.ins-title {{
    font-size: 13px;
    font-weight: 600;
    color: {t['text']};
    margin-bottom: 2px;
    letter-spacing: -0.005em;
}}
.ins-desc {{
    font-size: 12px;
    color: {t['text_dim']};
    line-height: 1.5;
}}
.ins-empty {{
    text-align: center;
    color: {t['text_mute']};
    padding: 2rem 0.6rem;
    font-size: 12.5px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   EMPTY STATE
   ═══════════════════════════════════════════════════════════════════════════ */
.empty {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.55rem;
    padding: 4.5rem 1rem;
    background: {t['bg_elev']};
    border: 1px dashed {t['border_str']};
    border-radius: 12px;
    color: {t['text_dim']};
    text-align: center;
    animation: fadeIn 0.3s ease;
    position: relative;
    overflow: hidden;
}}
.empty::before {{
    content: "";
    position: absolute;
    width: 200px; height: 200px;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(129,140,248,0.08) 0%, transparent 70%);
    pointer-events: none;
}}
.empty-icon {{
    font-size: 34px;
    background: linear-gradient(135deg, #818cf8, #a5b4fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
    filter: drop-shadow(0 0 10px rgba(129,140,248,0.3));
}}
.empty span:nth-child(2) {{ font-size: 14px; font-weight: 500; color: {t['text']}; }}
.empty-hint {{
    font-size: 11.5px;
    color: {t['text_mute']};
    letter-spacing: 0.02em;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   COMPARE PAGE
   ═══════════════════════════════════════════════════════════════════════════ */
.compare-header {{
    text-align: center;
    padding: 1rem 0 1.4rem;
    animation: slideUp 0.3s ease;
}}
.compare-header h2 {{
    font-size: 24px;
    font-weight: 600;
    color: {t['text']};
    margin: 0 0 0.3rem;
    letter-spacing: -0.02em;
}}
.compare-header p {{
    font-size: 13px;
    color: {t['text_dim']};
    margin: 0;
}}
.compare-label {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 12.5px;
    font-weight: 600;
    color: {t['text']};
    margin-bottom: 0.4rem;
    letter-spacing: -0.01em;
}}
.compare-label .badge {{
    width: 22px; height: 22px;
    border-radius: 6px;
    background: linear-gradient(135deg, {t['accent']}, {t['accent_hov']});
    color: #fff;
    display: grid;
    place-items: center;
    font-size: 11.5px;
    font-weight: 700;
    box-shadow: 0 2px 6px {t['accent_glow']};
}}
.cmp-tbl {{
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-radius: 10px;
    overflow: hidden;
    margin: 1rem 0;
    animation: slideUp 0.3s ease;
}}
.cmp-tbl th, .cmp-tbl td {{
    padding: 0.55rem 0.95rem;
    text-align: left;
    border-bottom: 1px solid {t['border']};
    font-size: 12.5px;
}}
.cmp-tbl tr:last-child td {{ border-bottom: none; }}
.cmp-tbl th {{
    background: {t['panel_hover']};
    color: {t['text_mute']};
    font-weight: 600;
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}}
.cmp-tbl td {{ color: {t['text_dim']}; }}
.cmp-tbl td.metric {{ color: {t['text']}; font-weight: 500; }}
.cmp-tbl td.win {{ color: {t['success']}; font-weight: 600; }}
.cmp-tbl td.lose {{ color: {t['text_mute']}; }}
.cmp-tbl tr:hover td {{ background: {t['panel_hover']}; }}

.cmp-verdict {{
    background: {t['bg_elev']};
    border: 1px solid {t['border']};
    border-left: 3px solid {t['accent']};
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin: 0.85rem 0;
    animation: slideUp 0.3s ease;
}}
.cmp-verdict-title {{
    font-size: 11px;
    font-weight: 600;
    color: {t['text_mute']};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}}
.cmp-verdict-body {{
    font-size: 13.5px;
    color: {t['text']};
    line-height: 1.5;
}}
.cmp-verdict-winner {{
    color: {t['accent']};
    font-weight: 600;
}}
.err-box {{
    background: {t['danger']}10;
    border: 1px solid {t['danger']}30;
    border-radius: 8px;
    padding: 0.55rem 0.85rem;
    color: {t['danger']};
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    margin-top: 0.5rem;
    white-space: pre-wrap;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   LOADING OVERLAY
   ═══════════════════════════════════════════════════════════════════════════ */
.loading-overlay {{
    position: fixed;
    inset: 0;
    z-index: 9999;
    background: { 'rgba(11,12,15,0.78)' if mode == 'dark' else 'rgba(250,251,252,0.85)' };
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.85rem;
    animation: fadeIn 0.18s ease;
}}
.loading-spinner {{
    width: 36px;
    height: 36px;
    border: 2.5px solid {t['border_str']};
    border-top-color: {t['accent']};
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
}}
.loading-text {{
    font-size: 14px;
    font-weight: 500;
    color: {t['text']};
    letter-spacing: -0.01em;
}}
.loading-sub {{
    font-size: 11.5px;
    color: {t['text_mute']};
    letter-spacing: 0.02em;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   COMPACT COLUMN GAPS
   ═══════════════════════════════════════════════════════════════════════════ */
[data-testid="column"] {{ padding: 0 0.4rem; }}
[data-testid="stHorizontalBlock"] {{ gap: 0.4rem; }}
.element-container {{ margin-bottom: 0.4rem; }}

/* Pyplot figures */
.stPyplot, [data-testid="stImage"] {{
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid {t['border']};
    background: {t['bg_elev']};
}}
</style>
"""
