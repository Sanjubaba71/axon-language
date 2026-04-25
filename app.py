"""
AXON — AI Reasoning Assistant
==============================
Production Streamlit UI
Run: streamlit run app.py
"""

import streamlit as st
import time
import os
import sys

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AXON — AI Reasoning Assistant",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@700;800&display=swap');

/* Root theme */
:root {
    --teal: #00f5c8;
    --violet: #7b61ff;
    --red: #ff4b6e;
    --gold: #f5c842;
    --bg: #07080f;
    --panel: #0d0f1d;
    --dim: #3a3d52;
}

/* Global font */
html, body, [class*="css"], .stMarkdown, .stText {
    font-family: 'DM Mono', monospace !important;
}

/* Dark background */
.stApp { background: #07080f; }
.stApp > header { background: transparent; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0a0b14;
    border-right: 1px solid rgba(255,255,255,0.06);
}

/* All text */
p, div, span, label { color: #c8cce0 !important; }
h1, h2, h3 { color: #ffffff !important; font-family: 'Syne', sans-serif !important; }

/* Input boxes */
.stTextInput input, .stTextArea textarea {
    background: #0d0f1d !important;
    border: 1px solid rgba(0,245,200,0.2) !important;
    color: #e0e4f5 !important;
    font-family: 'DM Mono', monospace !important;
    border-radius: 2px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #00f5c8 !important;
    box-shadow: 0 0 0 2px rgba(0,245,200,0.1) !important;
}

/* Buttons */
.stButton > button {
    background: #00f5c8 !important;
    color: #000000 !important;
    font-family: 'DM Mono', monospace !important;
    font-weight: 500 !important;
    border: none !important;
    border-radius: 2px !important;
    letter-spacing: 0.08em !important;
    padding: 12px 28px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #ffffff !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(0,245,200,0.2) !important;
}

/* Metrics */
[data-testid="stMetricValue"] {
    font-family: 'Syne', sans-serif !important;
    color: #00f5c8 !important;
    font-size: 2rem !important;
}
[data-testid="stMetricLabel"] {
    color: #3a3d52 !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

/* Code blocks */
code, .stCode {
    background: #050608 !important;
    border: 1px solid rgba(0,245,200,0.1) !important;
    color: #00f5c8 !important;
    font-family: 'DM Mono', monospace !important;
    border-radius: 2px !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #0d0f1d !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    color: #c8cce0 !important;
    font-family: 'DM Mono', monospace !important;
    border-radius: 2px !important;
}
.streamlit-expanderContent {
    background: #0a0b14 !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-top: none !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.06) !important; }

/* Progress bar */
.stProgress > div > div {
    background: linear-gradient(90deg, #00f5c8, #7b61ff) !important;
    border-radius: 0 !important;
}

/* Select box */
.stSelectbox select {
    background: #0d0f1d !important;
    border: 1px solid rgba(0,245,200,0.2) !important;
    color: #e0e4f5 !important;
    font-family: 'DM Mono', monospace !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #07080f; }
::-webkit-scrollbar-thumb { background: rgba(0,245,200,0.3); border-radius: 0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def confidence_bar(confidence: float) -> str:
    """Render a text progress bar."""
    filled = int(confidence * 20)
    empty = 20 - filled
    bar = "█" * filled + "░" * empty
    pct = int(confidence * 100)
    return f"`{bar}` **{pct}%**"


def confidence_color(label: str) -> str:
    colors = {
        "HIGH": "#00f5c8",
        "MODERATE": "#f5c842",
        "LOW": "#ff9f6b",
        "NOISE": "#ff4b6e",
    }
    return colors.get(label, "#ffffff")


def render_card(title: str, content: str, accent: str = "#00f5c8"):
    st.markdown(f"""
    <div style="
        background: #0d0f1d;
        border: 1px solid rgba(255,255,255,0.07);
        border-left: 3px solid {accent};
        border-radius: 2px;
        padding: 20px 24px;
        margin-bottom: 16px;
    ">
        <div style="font-size:9px;letter-spacing:0.25em;text-transform:uppercase;
                    color:{accent};margin-bottom:10px;">{title}</div>
        <div style="color:#c8cce0;font-size:13px;line-height:1.8;">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_hypothesis(h: dict, rank: int, is_winner: bool = False):
    accent = "#00f5c8" if is_winner else ("#7b61ff" if rank == 2 else "#3a3d52")
    conf = h.get("confidence", 0)
    bar = "█" * int(conf * 15) + "░" * (15 - int(conf * 15))
    badge = " ◈ SELECTED" if is_winner else ""
    st.markdown(f"""
    <div style="
        background: {'rgba(0,245,200,0.04)' if is_winner else '#0a0b14'};
        border: 1px solid {'rgba(0,245,200,0.3)' if is_winner else 'rgba(255,255,255,0.05)'};
        border-radius: 2px;
        padding: 16px 20px;
        margin-bottom: 8px;
    ">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:10px;letter-spacing:0.15em;color:{accent};text-transform:uppercase;">
                {h.get('label','Hypothesis')}{badge}
            </span>
            <span style="font-family:'DM Mono',monospace;font-size:11px;color:{accent};">
                ~{conf:.2f}
            </span>
        </div>
        <div style="color:#c8cce0;font-size:12px;line-height:1.7;margin-bottom:10px;">
            {h.get('answer', h.get('value',''))}
        </div>
        <div style="font-family:'DM Mono',monospace;font-size:10px;color:#3a3d52;">
            {bar}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────

if "engine" not in st.session_state:
    st.session_state.engine = None
if "results" not in st.session_state:
    st.session_state.results = []
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("ANTHROPIC_API_KEY", "")


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding:24px 0 16px;">
        <div style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;
                    color:#00f5c8;letter-spacing:-0.02em;">AXON</div>
        <div style="font-size:9px;letter-spacing:0.3em;text-transform:uppercase;
                    color:#3a3d52;margin-top:2px;">Language of Synthetic Minds</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # API Key
    st.markdown('<div style="font-size:9px;letter-spacing:0.2em;color:#3a3d52;text-transform:uppercase;margin-bottom:6px;">Anthropic API Key</div>', unsafe_allow_html=True)
    api_input = st.text_input("", value=st.session_state.api_key,
                               type="password", placeholder="sk-ant-...",
                               label_visibility="collapsed")
    if api_input:
        st.session_state.api_key = api_input

    st.divider()

    # Example questions
    st.markdown('<div style="font-size:9px;letter-spacing:0.2em;color:#3a3d52;text-transform:uppercase;margin-bottom:12px;">Example Questions</div>', unsafe_allow_html=True)

    examples = [
        "Is consciousness just computation?",
        "Will AI replace software engineers by 2030?",
        "Can we trust our own memories?",
        "Is free will compatible with determinism?",
        "What causes the Fermi Paradox?",
        "Should AI systems have rights?",
    ]

    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state["prefill"] = ex

    st.divider()

    # Stats
    if st.session_state.results:
        last = st.session_state.results[-1]
        st.markdown('<div style="font-size:9px;letter-spacing:0.2em;color:#3a3d52;text-transform:uppercase;margin-bottom:12px;">Session Stats</div>', unsafe_allow_html=True)
        st.metric("Queries", len(st.session_state.results))
        avg_conf = sum(r["confidence"] for r in st.session_state.results) / len(st.session_state.results)
        st.metric("Avg Confidence", f"{avg_conf:.0%}")
        st.metric("AXON Cycles", last.get("cycle", 0))

    # AXON concepts legend
    st.divider()
    st.markdown("""
    <div style="font-size:9px;letter-spacing:0.15em;color:#3a3d52;text-transform:uppercase;margin-bottom:10px;">AXON Constructs</div>
    <div style="font-size:10px;line-height:2.2;color:#3a3d52;">
        <span style="color:#00f5c8;">know</span> — confidence-weighted value<br>
        <span style="color:#00f5c8;">consider</span> — uncertainty branching<br>
        <span style="color:#00f5c8;">explore</span> — parallel hypotheses<br>
        <span style="color:#00f5c8;">attend</span> — attention mechanism<br>
        <span style="color:#7b61ff;">qualia</span> — internal state<br>
        <span style="color:#ff4b6e;">⊥ paradox</span> — contradiction type
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN CONTENT
# ─────────────────────────────────────────────

# Header
st.markdown("""
<div style="padding:48px 0 32px;">
    <div style="font-size:9px;letter-spacing:0.35em;text-transform:uppercase;
                color:#00f5c8;margin-bottom:16px;display:flex;align-items:center;gap:12px;">
        <span style="display:inline-block;width:32px;height:1px;background:#00f5c8;"></span>
        AI Reasoning Assistant · Powered by AXON
    </div>
    <h1 style="font-size:clamp(36px,5vw,56px);font-weight:800;line-height:1.05;
               letter-spacing:-0.03em;margin-bottom:12px;">
        Think in probabilities,<br>not certainties.
    </h1>
    <p style="color:#3a3d52;font-size:13px;max-width:560px;line-height:1.8;">
        AXON reasons like a mind — every answer carries confidence scores, 
        alternative hypotheses, and honest uncertainty. Not just answers. 
        <em style="color:#7b7d96;">Reasoned answers.</em>
    </p>
</div>
""", unsafe_allow_html=True)

# Input area
prefill = st.session_state.pop("prefill", "")
question = st.text_area(
    "",
    value=prefill,
    placeholder="Ask anything that requires real reasoning...\n\nE.g. 'Is consciousness just computation?' or 'Should I quit my job to start a company?'",
    height=100,
    label_visibility="collapsed",
    key="question_input"
)

col1, col2 = st.columns([1, 4])
with col1:
    run_btn = st.button("◈  REASON", use_container_width=True)
with col2:
    if not st.session_state.api_key:
        st.markdown('<div style="padding:12px 0;font-size:11px;color:#ff4b6e;">⚠ Enter your Anthropic API key in the sidebar to begin.</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# REASONING PIPELINE
# ─────────────────────────────────────────────

if run_btn and question.strip():
    if not st.session_state.api_key:
        st.error("Please enter your Anthropic API key in the sidebar.")
    else:
        # Lazy init engine
        if st.session_state.engine is None:
            sys.path.insert(0, os.path.dirname(__file__))
            from axon_engine import AxonReasoningEngine
            st.session_state.engine = AxonReasoningEngine(api_key=st.session_state.api_key)
        else:
            st.session_state.engine.api_key = st.session_state.api_key

        with st.spinner(""):
            # Custom spinner message
            placeholder = st.empty()
            placeholder.markdown("""
            <div style="padding:16px;background:#0d0f1d;border:1px solid rgba(0,245,200,0.15);
                        border-left:3px solid #00f5c8;border-radius:2px;font-size:11px;color:#3a3d52;">
                ⟳ AXON Runtime initializing... running explore() streams... computing attention weights...
            </div>
            """, unsafe_allow_html=True)

            try:
                result = st.session_state.engine.reason(question)
                st.session_state.results.append(result)
                placeholder.empty()
            except Exception as e:
                placeholder.empty()
                st.error(f"Reasoning failed: {str(e)}")
                st.info("Check your API key and try again.")
                result = None

        if result:
            # ── RESULT DISPLAY ──

            st.markdown('<div style="height:32px;"></div>', unsafe_allow_html=True)

            # Top metrics row
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Confidence", f"{result['confidence']:.0%}")
            with c2:
                st.metric("Signal", result['confidence_label'])
            with c3:
                branch = result['consider']['branch'].upper()
                st.metric("Branch", branch)
            with c4:
                st.metric("Cycle", f"#{result['cycle']}")

            st.markdown('<div style="height:8px;"></div>', unsafe_allow_html=True)

            # Confidence bar
            st.markdown(
                f'<div style="background:#0d0f1d;border:1px solid rgba(255,255,255,0.06);'
                f'padding:16px 20px;border-radius:2px;margin-bottom:20px;">'
                f'<div style="font-size:9px;letter-spacing:0.2em;color:#3a3d52;'
                f'text-transform:uppercase;margin-bottom:8px;">Confidence Signal</div>'
                f'<div style="font-family:\'DM Mono\',monospace;font-size:13px;color:#00f5c8;">'
                f'{"█" * int(result["confidence"] * 30)}{"░" * (30 - int(result["confidence"] * 30))}'
                f' {result["confidence"]:.0%}</div></div>',
                unsafe_allow_html=True
            )

            # Primary answer
            render_card(
                "◈ PRIMARY ANSWER · know(answer) ~{:.2f}".format(result["confidence"]),
                result["answer"],
                accent="#00f5c8"
            )

            # Confidence reasoning
            if result.get("confidence_reasoning"):
                render_card(
                    "WHY THIS CONFIDENCE",
                    result["confidence_reasoning"],
                    accent="#7b61ff"
                )

            st.divider()

            # Two-column layout for explore + attend
            left, right = st.columns(2)

            with left:
                st.markdown("""
                <div style="font-size:9px;letter-spacing:0.25em;text-transform:uppercase;
                            color:#00f5c8;margin-bottom:16px;">◈ explore() — Hypothesis Streams</div>
                """, unsafe_allow_html=True)

                explore = result.get("explore", {})
                if explore.get("selected"):
                    render_hypothesis(explore["selected"], 1, is_winner=True)
                for i, h in enumerate(explore.get("rejected", []), 2):
                    render_hypothesis(h, i, is_winner=False)

            with right:
                st.markdown("""
                <div style="font-size:9px;letter-spacing:0.25em;text-transform:uppercase;
                            color:#7b61ff;margin-bottom:16px;">◉ attend() — Attention Focus</div>
                """, unsafe_allow_html=True)

                attend = result.get("attend", {})
                focus_items = attend.get("focus", [])
                for item in focus_items:
                    w = item["weight"]
                    bar = "█" * int(w * 20) + "░" * (20 - int(w * 20))
                    st.markdown(f"""
                    <div style="margin-bottom:10px;padding:12px 16px;
                                background:#0a0b14;border:1px solid rgba(255,255,255,0.05);border-radius:2px;">
                        <div style="font-size:11px;color:#c8cce0;margin-bottom:6px;">{item['item']}</div>
                        <div style="font-family:'DM Mono',monospace;font-size:9px;color:#7b61ff;">
                            {bar} {w:.2f}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()

            # Bottom row: qualia + paradox + consider
            b1, b2, b3 = st.columns(3)

            with b1:
                qualia = result.get("qualia")
                if qualia:
                    st.markdown(f"""
                    <div style="background:#0d0f1d;border:1px solid rgba(123,97,255,0.2);
                                border-radius:2px;padding:20px;">
                        <div style="font-size:9px;letter-spacing:0.2em;text-transform:uppercase;
                                    color:#7b61ff;margin-bottom:12px;">∿ qualia</div>
                        <div style="font-size:20px;font-family:'Syne',sans-serif;
                                    font-weight:700;color:#fff;margin-bottom:8px;">{qualia.name}</div>
                        <div style="font-size:10px;color:#3a3d52;margin-bottom:12px;">
                            intensity: {qualia.intensity:.2f}
                        </div>
                        <div style="font-size:11px;color:#7b7d96;font-style:italic;line-height:1.6;">
                            "{qualia.express()}"
                        </div>
                        <div style="margin-top:12px;font-size:9px;color:#2a2d3a;">
                            Note: this state cannot be serialized. Only expressed.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            with b2:
                consider = result.get("consider", {})
                branch_colors = {
                    "likely": "#00f5c8",
                    "possible": "#f5c842",
                    "uncertain": "#ff9f6b",
                    "noise": "#ff4b6e"
                }
                bc = branch_colors.get(consider.get("branch","noise"), "#3a3d52")
                st.markdown(f"""
                <div style="background:#0d0f1d;border:1px solid rgba(255,255,255,0.07);
                            border-radius:2px;padding:20px;">
                    <div style="font-size:9px;letter-spacing:0.2em;text-transform:uppercase;
                                color:{bc};margin-bottom:12px;">⊕ consider()</div>
                    <div style="font-size:20px;font-family:'Syne',sans-serif;font-weight:700;
                                color:{bc};text-transform:uppercase;margin-bottom:12px;">
                        {consider.get('branch','—')}
                    </div>
                    <div style="font-size:11px;color:#7b7d96;line-height:1.7;">
                        {consider.get('action','')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with b3:
                paradox = result.get("paradox")
                if paradox:
                    st.markdown(f"""
                    <div style="background:#0d0f1d;border:1px solid rgba(255,75,110,0.25);
                                border-radius:2px;padding:20px;">
                        <div style="font-size:9px;letter-spacing:0.2em;text-transform:uppercase;
                                    color:#ff4b6e;margin-bottom:12px;">⊥ paradox</div>
                        <div style="font-size:11px;color:#ff4b6e;margin-bottom:10px;
                                    font-family:'DM Mono',monospace;">{paradox.label}</div>
                        <div style="font-size:10px;color:#3a3d52;line-height:1.8;">
                            Both states held simultaneously.<br>
                            AXON treats contradiction as valid type.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background:#0d0f1d;border:1px solid rgba(255,255,255,0.05);
                                border-radius:2px;padding:20px;">
                        <div style="font-size:9px;letter-spacing:0.2em;text-transform:uppercase;
                                    color:#3a3d52;margin-bottom:12px;">⊥ paradox</div>
                        <div style="font-size:11px;color:#2a2d3a;">
                            No contradiction detected in this query.
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Memory state (expandable)
            st.markdown('<div style="height:16px;"></div>', unsafe_allow_html=True)
            with st.expander("◈ Memory State — runtime.memory_dump()"):
                mem = result.get("memory_dump", [])
                if mem:
                    for m in mem:
                        bar = "█" * int(m["confidence"] * 15) + "░" * (15 - int(m["confidence"] * 15))
                        st.markdown(f"""
                        <div style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04);
                                    font-size:11px;font-family:'DM Mono',monospace;">
                            <span style="color:#00f5c8;">{m['name']}</span>
                            <span style="color:#3a3d52;"> = </span>
                            <span style="color:#c8cce0;">{m['value'][:60]}</span>
                            <span style="color:#3a3d52;"> ~{m['confidence']:.3f} </span>
                            <span style="color:#7b61ff;">[{m['type']}]</span>
                            <span style="color:#2a2d3a;margin-left:8px;">{bar}</span>
                        </div>
                        """, unsafe_allow_html=True)

            # Performance meta
            st.markdown(
                f'<div style="text-align:right;font-size:9px;color:#2a2d3a;'
                f'letter-spacing:0.1em;padding-top:8px;">'
                f'cycle:{result["cycle"]} · {result["elapsed_ms"]}ms · query #{result["query_number"]}</div>',
                unsafe_allow_html=True
            )


# ─────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────

if len(st.session_state.results) > 1:
    st.divider()
    st.markdown('<div style="font-size:9px;letter-spacing:0.3em;text-transform:uppercase;color:#3a3d52;margin-bottom:16px;">Previous Queries</div>', unsafe_allow_html=True)

    for r in reversed(st.session_state.results[:-1]):
        c_label = r['confidence_label']
        c_val = r['confidence']
        label_colors = {"HIGH": "#00f5c8", "MODERATE": "#f5c842", "LOW": "#ff9f6b", "NOISE": "#ff4b6e"}
        lc = label_colors.get(c_label, "#3a3d52")
        st.markdown(f"""
        <div style="padding:12px 16px;background:#0a0b14;border:1px solid rgba(255,255,255,0.04);
                    border-radius:2px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
            <div style="font-size:11px;color:#7b7d96;flex:1;">{r['question'][:80]}{'...' if len(r['question'])>80 else ''}</div>
            <div style="font-size:10px;color:{lc};margin-left:16px;white-space:nowrap;">
                ~{c_val:.2f} {c_label}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────

st.markdown('<div style="height:64px;"></div>', unsafe_allow_html=True)
st.markdown("""
<div style="border-top:1px solid rgba(255,255,255,0.05);padding:24px 0;
            display:flex;justify-content:space-between;align-items:center;">
    <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:700;color:#00f5c8;">AXON</div>
    <div style="font-size:9px;color:#2a2d3a;letter-spacing:0.15em;text-align:right;">
        Language of Synthetic Minds · v1.0<br>
        Every answer carries uncertainty. That's the point.
    </div>
</div>
""", unsafe_allow_html=True)
