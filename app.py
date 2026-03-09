import streamlit as st
from groq import Groq
import re
import zipfile
import io
from datetime import datetime

# ══════════════════════════════════════════════
# 1. PAGE CONFIG  ← must be FIRST st call
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="LogicForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="auto",
)

# ══════════════════════════════════════════════
# 2. CSS  — high-contrast light theme, mobile-ready
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --bg:        #f0f4ff;
    --surface:   #ffffff;
    --surface2:  #f8faff;
    --border:    #d1d9f0;
    --accent:    #4f46e5;
    --accent-h:  #4338ca;
    --accent-lt: #eef2ff;
    --green:     #059669;
    --green-lt:  #ecfdf5;
    --amber:     #d97706;
    --amber-lt:  #fffbeb;
    --red:       #dc2626;
    --red-lt:    #fef2f2;
    --blue:      #2563eb;
    --blue-lt:   #eff6ff;
    --text:      #1e293b;
    --text2:     #475569;
    --text3:     #94a3b8;
    --radius:    12px;
    --shadow:    0 2px 12px rgba(79,70,229,0.08);
    --shadow-lg: 0 8px 32px rgba(79,70,229,0.12);
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"] {
    background: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text) !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: var(--text) !important; }

/* Headings */
h1,h2,h3,h4 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 4px !important;
    gap: 2px !important;
    flex-wrap: wrap !important;
    box-shadow: var(--shadow) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text2) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 8px 14px !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #ffffff !important;
}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
    background: var(--accent-lt) !important;
    color: var(--accent) !important;
}

/* Buttons */
.stButton > button {
    background: var(--accent) !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(79,70,229,0.25) !important;
}
.stButton > button:hover {
    background: var(--accent-h) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(79,70,229,0.35) !important;
}

/* Download buttons */
.stDownloadButton > button {
    background: var(--green) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(5,150,105,0.25) !important;
}
.stDownloadButton > button:hover {
    background: #047857 !important;
    box-shadow: 0 4px 16px rgba(5,150,105,0.35) !important;
}

/* Inputs */
.stTextArea textarea,
.stTextInput > div > div > input {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    border-radius: var(--radius) !important;
    font-size: 14px !important;
}
.stTextArea textarea:focus,
.stTextInput > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important;
}
.stTextArea textarea::placeholder,
.stTextInput > div > div > input::placeholder { color: var(--text3) !important; }

/* Labels */
label, p { color: var(--text) !important; }
.stSelectbox label, .stTextArea label, .stTextInput label,
.stRadio label, .stMultiSelect label, .stSlider label {
    color: var(--text) !important;
    font-weight: 600 !important;
    font-size: 13px !important;
}

/* Code blocks */
.stCodeBlock, pre {
    background: #1e1b4b !important;
    border: 1px solid #312e81 !important;
    border-radius: var(--radius) !important;
}
.stCodeBlock code, pre code {
    font-family: 'JetBrains Mono', monospace !important;
    color: #e0e7ff !important;
}

/* Metrics */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 12px 16px !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stMetricValue"] { color: var(--accent) !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: var(--text2) !important; }

/* Chat messages */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow) !important;
    margin-bottom: 8px !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-weight: 600 !important;
}

/* Alerts */
.stAlert, [data-baseweb="notification"] { border-radius: var(--radius) !important; }

/* Spinner */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* Radio & checkbox text */
.stRadio label span, .stCheckbox label span { color: var(--text) !important; }

/* Multiselect tags */
.stMultiSelect [data-baseweb="tag"] {
    background: var(--accent) !important;
    color: white !important;
    border-radius: 6px !important;
}

/* Header banner */
.lf-header {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #2563eb 100%);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: var(--shadow-lg);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
}
.lf-header h1 { color: white !important; font-size: clamp(20px, 4vw, 30px) !important; margin: 0 !important; }
.lf-header p  { color: rgba(255,255,255,0.8) !important; margin: 4px 0 0 0 !important; font-size: 13px !important; }
.lf-badge {
    background: rgba(255,255,255,0.2); color: white;
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px; padding: 4px 14px;
    font-size: 12px; font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

/* Section headers */
.sec-title { font-size: 17px; font-weight: 700; color: var(--text); margin-bottom: 2px; }
.sec-sub   { font-size: 13px; color: var(--text2); margin-bottom: 16px; }

/* Coloured info cards */
.card-green {
    background: var(--green-lt); border: 1px solid #a7f3d0;
    border-left: 4px solid var(--green);
    border-radius: var(--radius); padding: 14px 18px; margin-bottom: 12px;
    color: var(--text);
}
.card-blue {
    background: var(--blue-lt); border: 1px solid #bfdbfe;
    border-left: 4px solid var(--blue);
    border-radius: var(--radius); padding: 14px 18px; margin-bottom: 12px;
    color: var(--text);
}
.card-amber {
    background: var(--amber-lt); border: 1px solid #fde68a;
    border-left: 4px solid var(--amber);
    border-radius: var(--radius); padding: 14px 18px; margin-bottom: 12px;
    color: var(--text);
}

/* Empty states */
.empty-state {
    background: var(--surface2); border: 2px dashed var(--border);
    border-radius: var(--radius); padding: 40px 20px;
    text-align: center; color: var(--text3); font-size: 14px;
}

/* History card */
.hist-card {
    background: var(--surface); border: 1px solid var(--border);
    border-left: 4px solid var(--accent); border-radius: var(--radius);
    padding: 14px 18px; margin-bottom: 10px; box-shadow: var(--shadow);
}
.hist-meta { font-size: 11px; color: var(--text3); font-family: 'JetBrains Mono', monospace; margin-top: 4px; }

/* ── Floating 3-dot menu button (always visible) ── */
#lf-menu-btn {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 99999;
    width: 42px;
    height: 42px;
    background: var(--accent);
    border: none;
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    box-shadow: 0 3px 12px rgba(79,70,229,0.4);
    transition: background 0.2s, transform 0.15s;
}
#lf-menu-btn:hover { background: var(--accent-h); transform: scale(1.05); }
#lf-menu-btn span {
    display: block;
    width: 5px; height: 5px;
    background: white;
    border-radius: 50%;
}

/* Sidebar overlay panel */
#lf-sidebar-overlay {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(15,15,30,0.45);
    z-index: 99997;
    backdrop-filter: blur(2px);
}
#lf-sidebar-overlay.open { display: block; }

#lf-sidebar-panel {
    position: fixed;
    top: 0; left: 0;
    width: min(320px, 90vw);
    height: 100vh;
    background: var(--surface);
    border-right: 1px solid var(--border);
    box-shadow: 4px 0 24px rgba(79,70,229,0.15);
    z-index: 99998;
    transform: translateX(-110%);
    transition: transform 0.28s cubic-bezier(0.4,0,0.2,1);
    overflow-y: auto;
    padding: 16px;
}
#lf-sidebar-panel.open { transform: translateX(0); }

#lf-sidebar-close {
    position: absolute;
    top: 12px; right: 12px;
    background: var(--accent-lt);
    border: none;
    border-radius: 8px;
    width: 32px; height: 32px;
    cursor: pointer;
    font-size: 16px;
    color: var(--accent);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700;
}
#lf-sidebar-close:hover { background: var(--accent); color: white; }

/* Hide native Streamlit sidebar on mobile, show our custom one */
@media (max-width: 768px) {
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    #lf-menu-btn { display: flex !important; }

    /* Header */
    .lf-header { padding: 14px 16px; gap: 8px; padding-left: 68px; }
    .lf-header h1 { font-size: 19px !important; }
    .lf-badge { font-size: 10px; padding: 3px 10px; }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 2px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 11px !important; padding: 7px 9px !important; }

    /* Buttons */
    .stButton > button { font-size: 13px !important; padding: 9px 14px !important; }
    .stDownloadButton > button { font-size: 13px !important; }

    /* Chat input */
    [data-testid="stChatInput"] textarea { font-size: 14px !important; }

    /* Metrics */
    [data-testid="stMetric"] { padding: 10px 12px !important; }
    .sec-title { font-size: 16px; }
    .empty-state { padding: 28px 16px; }
}

/* On desktop: hide the floating button */
@media (min-width: 769px) {
    #lf-menu-btn { display: none !important; }
    #lf-sidebar-overlay { display: none !important; }
    #lf-sidebar-panel { display: none !important; }
}

/* Small phones */
@media (max-width: 480px) {
    .lf-header h1 { font-size: 16px !important; }
    .stTabs [data-baseweb="tab"] { font-size: 10px !important; padding: 6px 7px !important; }
}

#MainMenu, footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 3. SESSION STATE
# ══════════════════════════════════════════════
_defaults: dict = {
    "chat_history":        [{"role": "assistant", "content": "👋 Hey! I'm your Senior Python Dev AI. Paste code, errors, or ask anything."}],
    "build_history":       [],
    "active_code":         "",
    "active_explanation":  "",
    "active_setup":        "",
    "total_builds":        0,
    "total_tokens":        0,
    "debug_code":          "",
    "debug_explanation":   "",
    "refactor_code":       "",
    "refactor_explanation":"",
    "test_code":           "",
    "doc_result":          "",
    "groq_api_key":        "",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════
# 4. API KEY
# ══════════════════════════════════════════════
api_key: str | None = None
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    pass
if not api_key and st.session_state.groq_api_key:
    api_key = st.session_state.groq_api_key

# ══════════════════════════════════════════════
# 5. SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚡ LogicForge")
    st.caption("AI Code Architect · v2.0")
    st.divider()

    if not api_key:
        st.markdown("### 🔑 AI API Key")
        entered = st.text_input("API Key", type="password",
                                placeholder="Enter your API key…",
                                help="Paste your API key to unlock all features",
                                label_visibility="collapsed")
        if entered:
            st.session_state.groq_api_key = entered
            api_key = entered
            st.success("✅ Key saved!")
        else:
            st.info("🔑 Enter your API key above to start")
        st.divider()

    st.markdown("### ⚙️ Settings")
    MODEL_MAP = {
        "llama-3.3-70b-versatile":       "🧠 Llama 3.3 70B — Best quality",
        "llama-3.1-8b-instant":          "⚡ Llama 3.1 8B — Fastest",
        "deepseek-r1-distill-llama-70b": "🔍 DeepSeek R1 70B — Reasoning",
    }
    model = st.selectbox("Model", list(MODEL_MAP.keys()),
                         format_func=lambda x: MODEL_MAP[x], index=0)
    framework = st.selectbox("Framework",
                             ["Streamlit", "FastAPI", "Flask", "Django", "Pure Python", "CLI Tool"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05,
                            help="Lower = precise. Higher = creative.")
    max_tokens = st.select_slider("Max Tokens",
                                  options=[2000, 4000, 6000, 8000, 12000], value=8000)

    st.divider()
    st.markdown("### 📊 Session Stats")
    c1, c2 = st.columns(2)
    c1.metric("🏗️ Builds", st.session_state.total_builds)
    tok_val = st.session_state.total_tokens
    tok_str = f"{tok_val/1000:.1f}k" if tok_val >= 1000 else str(tok_val)
    c2.metric("🔤 Tokens", tok_str)

    st.divider()
    if st.button("🗑️ Reset Session", use_container_width=True):
        for k, v in _defaults.items():
            st.session_state[k] = v
        st.rerun()

# ══════════════════════════════════════════════
# 6. HELPERS
# ══════════════════════════════════════════════
def call_groq(messages: list, max_tok: int | None = None, temp: float | None = None) -> tuple[str, int]:
    if not api_key:
        st.error("⚠️ Add your API key in the sidebar first.")
        st.stop()
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp if temp is not None else temperature,
        max_tokens=max_tok or max_tokens,
    )
    content = resp.choices[0].message.content or ""
    tokens  = getattr(resp.usage, "total_tokens", 0)
    return content, tokens


def parse_code(text: str) -> tuple[str, str]:
    """Returns (code, rest). Tries ```python first, then any ```."""
    m = re.search(r"```python\s*(.*?)```", text, re.DOTALL)
    if not m:
        m = re.search(r"```\s*([\s\S]*?)```", text)
    if m:
        code = m.group(1).strip()
        rest = (text[:m.start()] + text[m.end():]).strip()
        return code, rest
    return "", text.strip()


def make_zip(code: str, setup: str, name: str = "app") -> bytes:
    safe = re.sub(r"[^\w]", "_", name.lower())[:40] or "app"
    reqs = "\n".join(
        ln.strip().lstrip("-*• ").strip()
        for ln in setup.splitlines()
        if ln.strip() and not ln.strip().startswith("#") and " " not in ln.strip()
    ) or "streamlit\ngroq"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{safe}.py", code)
        z.writestr("requirements.txt", reqs)
        z.writestr("README.md",
                   f"# {name}\n\nGenerated by **LogicForge AI Architect**.\n\n"
                   f"## Quick start\n```bash\npip install -r requirements.txt\n"
                   f"streamlit run {safe}.py\n```\n")
    return buf.getvalue()

# ══════════════════════════════════════════════
# 7. SYSTEM PROMPTS
# ══════════════════════════════════════════════
def SYS_BUILD(fw: str) -> str:
    return (
        f"You are a Senior Python Developer. Write COMPLETE, FUNCTIONAL, PRODUCTION-READY {fw} code.\n\n"
        "RULES:\n"
        "1. Include ALL imports — code must run immediately with zero errors.\n"
        "2. No stubs, no placeholders, no TODO comments.\n"
        "3. Clean code: type hints, docstrings, meaningful names.\n\n"
        "OUTPUT FORMAT (follow exactly):\n"
        "### SECTION 1: THE CODE\n"
        "```python\n<complete working code here>\n```\n\n"
        "### SECTION 2: EXPLANATION\n"
        "<explain key functions and architecture>\n\n"
        "### SECTION 3: SETUP\n"
        "<list exact pip package names, one per line>"
    )

SYS_DEBUG = (
    "You are a Senior Python Developer specializing in debugging.\n"
    "Identify ALL bugs. Return the COMPLETE fixed code then list every fix.\n\n"
    "FORMAT:\n"
    "```python\n<complete fixed code>\n```\n\n"
    "### FIXES\n- Fix 1: what was wrong and what you changed\n- Fix 2: ..."
)

SYS_REFACTOR = (
    "You are a Senior Python Developer focused on code quality.\n"
    "Refactor for: readability, PEP 8, type hints, docstrings, DRY, performance.\n"
    "Return the COMPLETE refactored code then a brief changelog.\n\n"
    "FORMAT:\n"
    "```python\n<complete refactored code>\n```\n\n"
    "### CHANGES\n- Change 1: ...\n- Change 2: ..."
)

SYS_TESTS = (
    "You are a Senior Python Developer and QA engineer.\n"
    "Write comprehensive pytest tests: happy paths, edge cases, error handling.\n"
    "Return ONLY a python code block — nothing else outside the block.\n\n"
    "```python\n<complete test file here>\n```"
)

SYS_CHAT = (
    "You are a Senior Python Developer with 15 years of experience. "
    "Help with code reviews, debugging, architecture, best practices. "
    "Use ```python blocks for all code. Be concise but thorough."
)

SYS_DOCS = (
    "You are a Technical Writer. Write professional, comprehensive documentation in Markdown. "
    "Include badges, clear sections, code examples. Be thorough — publish-ready on GitHub."
)

# ══════════════════════════════════════════════
# 8. HEADER
# ══════════════════════════════════════════════
st.markdown("""
<div class="lf-header">
  <div>
    <h1>⚡ LogicForge AI Architect</h1>
    <p>Build · Debug · Refactor · Test · Document — all in one place</p>
  </div>
  <span class="lf-badge">v2.0 · AI Powered</span>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.warning("⚠️ **No API key detected.** Please enter your API key in the sidebar to use all features.")

# ── Floating 3-dot button + custom mobile sidebar panel ──
# Build sidebar panel content as HTML so it mirrors the native sidebar on mobile
_model_labels = {
    "llama-3.3-70b-versatile":       "🧠 Llama 3.3 70B",
    "llama-3.1-8b-instant":          "⚡ Llama 3.1 8B",
    "deepseek-r1-distill-llama-70b": "🔍 DeepSeek R1 70B",
}
_model_name = _model_labels.get(model, model)
_key_status = "✅ API key active" if api_key else "⚠️ No API key — enter below"
_builds = st.session_state.total_builds
_tokens_val = st.session_state.total_tokens
_tokens_str = f"{_tokens_val/1000:.1f}k" if _tokens_val >= 1000 else str(_tokens_val)

st.markdown(f"""
<!-- Floating 3-dot menu button (always visible on mobile) -->
<button id="lf-menu-btn" aria-label="Open settings" title="Settings">
  <span></span><span></span><span></span>
</button>

<!-- Overlay backdrop -->
<div id="lf-sidebar-overlay" onclick="closeSidebar()"></div>

<!-- Custom sidebar panel -->
<div id="lf-sidebar-panel">
  <button id="lf-sidebar-close" onclick="closeSidebar()" title="Close">✕</button>

  <div style="margin-bottom:16px">
    <div style="font-size:20px;font-weight:800;color:#4f46e5;margin-bottom:2px">⚡ LogicForge</div>
    <div style="font-size:12px;color:#94a3b8">AI Code Architect · v2.0</div>
  </div>
  <hr style="border-color:#d1d9f0;margin:12px 0">

  <div style="font-size:12px;font-weight:700;color:#1e293b;margin-bottom:6px">🔑 API Key Status</div>
  <div style="background:{'#ecfdf5' if api_key else '#fffbeb'};border:1px solid {'#a7f3d0' if api_key else '#fde68a'};border-radius:8px;padding:8px 12px;font-size:13px;color:{'#059669' if api_key else '#d97706'};margin-bottom:12px">
    {_key_status}
  </div>

  <div style="font-size:12px;font-weight:700;color:#1e293b;margin-bottom:6px">⚙️ Current Settings</div>
  <div style="background:#f8faff;border:1px solid #d1d9f0;border-radius:8px;padding:10px 12px;font-size:13px;color:#475569;line-height:1.8;margin-bottom:12px">
    <div><strong>Model:</strong> {_model_name}</div>
    <div><strong>Framework:</strong> {framework}</div>
    <div><strong>Temperature:</strong> {temperature}</div>
    <div><strong>Max Tokens:</strong> {max_tokens:,}</div>
  </div>

  <div style="font-size:12px;font-weight:700;color:#1e293b;margin-bottom:8px">📊 Session Stats</div>
  <div style="display:flex;gap:8px;margin-bottom:12px">
    <div style="flex:1;background:#eef2ff;border:1px solid #c7d2fe;border-radius:8px;padding:10px;text-align:center">
      <div style="font-size:22px;font-weight:800;color:#4f46e5">{_builds}</div>
      <div style="font-size:10px;color:#6366f1;text-transform:uppercase;letter-spacing:0.5px">Builds</div>
    </div>
    <div style="flex:1;background:#eef2ff;border:1px solid #c7d2fe;border-radius:8px;padding:10px;text-align:center">
      <div style="font-size:22px;font-weight:800;color:#4f46e5">{_tokens_str}</div>
      <div style="font-size:10px;color:#6366f1;text-transform:uppercase;letter-spacing:0.5px">Tokens</div>
    </div>
  </div>

  <div style="font-size:11px;color:#94a3b8;text-align:center;margin-top:16px;line-height:1.5">
    To change model, framework, or API key<br>use the sidebar on desktop view
  </div>
</div>

<script>
function openSidebar() {{
  document.getElementById('lf-sidebar-panel').classList.add('open');
  document.getElementById('lf-sidebar-overlay').classList.add('open');
  document.body.style.overflow = 'hidden';
}}
function closeSidebar() {{
  document.getElementById('lf-sidebar-panel').classList.remove('open');
  document.getElementById('lf-sidebar-overlay').classList.remove('open');
  document.body.style.overflow = '';
}}
document.getElementById('lf-menu-btn').addEventListener('click', openSidebar);
// Close on Escape key
document.addEventListener('keydown', function(e) {{
  if (e.key === 'Escape') closeSidebar();
}});
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 9. TABS
# ══════════════════════════════════════════════
tab_build, tab_debug, tab_refactor, tab_tests, tab_chat, tab_docs, tab_history = st.tabs([
    "🏗️ Builder", "🐛 Debugger", "♻️ Refactor",
    "🧪 Tests", "💬 Chat", "📄 Docs", "🕓 History",
])

# ═══════════════════════════════════════
# TAB 1 — BUILDER
# ═══════════════════════════════════════
with tab_build:
    st.markdown('<div class="sec-title">🏗️ App Builder</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">Describe what you want — get complete, runnable {framework} code instantly.</div>', unsafe_allow_html=True)

    bl, br = st.columns([1, 1], gap="large")

    with bl:
        user_req = st.text_area("Describe your app", height=160,
            placeholder="E.g. A Streamlit dashboard that fetches live crypto prices, shows candlestick charts, and has a portfolio P&L tracker.")
        extra = st.text_area("Extra constraints / libraries (optional)", height=70,
            placeholder="E.g. Use plotly. Add caching. Support CSV export.")
        with st.expander("⚙️ Extra options"):
            also_tests  = st.checkbox("Also generate unit tests")
            also_readme = st.checkbox("Also generate README")
        build_btn = st.button("⚡ Generate Full Code", type="primary", use_container_width=True)

    with br:
        if st.session_state.active_code:
            ct, ce, cs = st.tabs(["📋 Code", "📖 Explanation", "📦 Setup"])
            with ct:
                st.code(st.session_state.active_code, language="python")
                dc1, dc2 = st.columns(2)
                dc1.download_button("⬇️ Download .py",
                    data=st.session_state.active_code, file_name="app.py",
                    mime="text/plain", use_container_width=True)
                dc2.download_button("📦 Download .zip",
                    data=make_zip(st.session_state.active_code,
                                  st.session_state.active_setup,
                                  user_req[:40] if user_req else "app"),
                    file_name="logicforge_app.zip",
                    mime="application/zip", use_container_width=True)
            with ce:
                st.markdown(st.session_state.active_explanation or "_No explanation._")
            with cs:
                if st.session_state.active_setup:
                    st.markdown(st.session_state.active_setup)
                else:
                    st.info("No setup info available.")
        else:
            st.markdown("""
            <div class="empty-state">
              <div style="font-size:38px;margin-bottom:10px">🏗️</div>
              <div style="font-weight:600;color:#475569;margin-bottom:6px">No code yet</div>
              <div>Describe your app on the left and hit <strong>Generate Full Code</strong></div>
            </div>""", unsafe_allow_html=True)

    if build_btn:
        if not user_req.strip():
            st.warning("Please describe your app idea.")
        elif not api_key:
            st.error("Add your API key in the sidebar.")
        else:
            prompt = f"Framework: {framework}\nTask: {user_req}"
            if extra.strip():
                prompt += f"\nAdditional constraints: {extra}"
            with st.spinner("⚡ Building your app…"):
                try:
                    full_res, tokens = call_groq(
                        [{"role": "system", "content": SYS_BUILD(framework)},
                         {"role": "user",   "content": prompt}])

                    code, rest = parse_code(full_res)

                    exp_m = re.search(
                        r"(?:SECTION 2|EXPLANATION)[:\s]*(.*?)(?=###\s*SECTION 3|\Z)",
                        rest, re.DOTALL | re.IGNORECASE)
                    explanation = exp_m.group(1).strip() if exp_m else rest

                    set_m = re.search(
                        r"(?:SECTION 3|SETUP)[:\s]*(.*?)$",
                        full_res, re.DOTALL | re.IGNORECASE)
                    setup = set_m.group(1).strip() if set_m else ""

                    st.session_state.active_code        = code or full_res
                    st.session_state.active_explanation = explanation
                    st.session_state.active_setup       = setup
                    st.session_state.total_builds      += 1
                    st.session_state.total_tokens      += tokens

                    st.session_state.build_history.append({
                        "id":          st.session_state.total_builds,
                        "prompt":      user_req[:150],
                        "code":        code or full_res,
                        "explanation": explanation,
                        "setup":       setup,
                        "ts":          datetime.now().strftime("%d %b %Y, %H:%M"),
                        "model":       model,
                        "tokens":      tokens,
                        "framework":   framework,
                    })

                    if also_tests and (code or full_res):
                        tr, _ = call_groq(
                            [{"role": "system", "content": SYS_TESTS},
                             {"role": "user",   "content": f"Write pytest tests:\n```python\n{(code or full_res)[:4000]}\n```"}],
                            max_tok=3000, temp=0.05)
                        tc, _ = parse_code(tr)
                        st.session_state.test_code = tc or tr

                    if also_readme:
                        dr, _ = call_groq(
                            [{"role": "system", "content": SYS_DOCS},
                             {"role": "user",   "content": f"Write a GitHub README for: {user_req}\nFramework: {framework}"}],
                            max_tok=2000, temp=0.3)
                        st.session_state.doc_result = dr

                    st.success(f"✅ Done! {tokens:,} tokens used.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Build failed: {e}")

# ═══════════════════════════════════════
# TAB 2 — DEBUGGER
# ═══════════════════════════════════════
with tab_debug:
    st.markdown('<div class="sec-title">🐛 Bug Fixer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Paste broken code + optional traceback → get a fully fixed version with explanation.</div>', unsafe_allow_html=True)

    dl, dr = st.columns([1, 1], gap="large")
    with dl:
        buggy = st.text_area("Paste buggy code", height=200,
            placeholder="def greet(name):\n    print('Hello ' + naam)  # NameError!")
        tb = st.text_area("Error / Traceback (optional)", height=90,
            placeholder="NameError: name 'naam' is not defined")

        col_d1, col_d2 = st.columns(2)
        debug_btn = col_d1.button("🔍 Fix My Code", type="primary", use_container_width=True)
        if col_d2.button("📥 Load from Builder", use_container_width=True, key="dbg_load"):
            if st.session_state.active_code:
                st.session_state["_dbg_pre"] = st.session_state.active_code
                st.rerun()
            else:
                st.warning("No active code in Builder yet.")

        # Apply prefill (Streamlit reruns, so we show it as default value via session)
        if "_dbg_pre" in st.session_state:
            buggy = st.session_state.pop("_dbg_pre")

    with dr:
        if st.session_state.debug_code:
            st.markdown('<div class="card-green"><strong>✅ Fixed Code</strong></div>', unsafe_allow_html=True)
            st.code(st.session_state.debug_code, language="python")
            st.download_button("⬇️ Download Fixed .py",
                data=st.session_state.debug_code, file_name="fixed_app.py",
                mime="text/plain", use_container_width=True)
            if st.session_state.debug_explanation:
                with st.expander("📋 What was fixed", expanded=True):
                    st.markdown(st.session_state.debug_explanation)
        else:
            st.markdown("""
            <div class="empty-state">
              <div style="font-size:38px;margin-bottom:10px">🐛</div>
              <div style="font-weight:600;color:#475569;margin-bottom:6px">No fixes yet</div>
              <div>Paste buggy code and click <strong>Fix My Code</strong></div>
            </div>""", unsafe_allow_html=True)

    if debug_btn:
        src = buggy.strip()
        if not src:
            st.warning("Paste some code first.")
        elif not api_key:
            st.error("Add your API key in the sidebar.")
        else:
            content = f"Buggy code:\n```python\n{src}\n```"
            if tb.strip():
                content += f"\n\nTraceback:\n```\n{tb.strip()}\n```"
            with st.spinner("🔍 Analysing bugs…"):
                try:
                    res, tok = call_groq(
                        [{"role": "system", "content": SYS_DEBUG},
                         {"role": "user",   "content": content}],
                        temp=0.05)
                    fc, expl = parse_code(res)
                    st.session_state.debug_code        = fc or res
                    st.session_state.debug_explanation = expl
                    st.session_state.total_tokens     += tok
                    st.rerun()
                except Exception as e:
                    st.error(f"Debug failed: {e}")

# ═══════════════════════════════════════
# TAB 3 — REFACTOR
# ═══════════════════════════════════════
with tab_refactor:
    st.markdown('<div class="sec-title">♻️ Code Refactorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Clean up messy code — PEP 8, type hints, docstrings, performance.</div>', unsafe_allow_html=True)

    rl, rr = st.columns([1, 1], gap="large")
    with rl:
        raw_code = st.text_area("Paste code to refactor", height=200,
            placeholder="x=1\ndef f(a,b):\n  return a+b")
        goals = st.multiselect("Refactoring goals",
            ["PEP 8 compliance", "Type hints", "Docstrings",
             "Performance", "DRY principle", "Error handling", "Add logging"],
            default=["PEP 8 compliance", "Type hints", "Docstrings"])

        rc1, rc2 = st.columns(2)
        ref_btn = rc1.button("♻️ Refactor Code", type="primary", use_container_width=True)
        if rc2.button("📥 Load from Builder", use_container_width=True, key="ref_load"):
            if st.session_state.active_code:
                st.session_state["_ref_pre"] = st.session_state.active_code
                st.rerun()
            else:
                st.warning("No active code in Builder yet.")

        if "_ref_pre" in st.session_state:
            raw_code = st.session_state.pop("_ref_pre")

    with rr:
        if st.session_state.refactor_code:
            st.markdown('<div class="card-blue"><strong>✅ Refactored Code</strong></div>', unsafe_allow_html=True)
            st.code(st.session_state.refactor_code, language="python")
            st.download_button("⬇️ Download Refactored .py",
                data=st.session_state.refactor_code, file_name="refactored.py",
                mime="text/plain", use_container_width=True)
            if st.session_state.refactor_explanation:
                with st.expander("📋 Changes made", expanded=True):
                    st.markdown(st.session_state.refactor_explanation)
        else:
            st.markdown("""
            <div class="empty-state">
              <div style="font-size:38px;margin-bottom:10px">♻️</div>
              <div style="font-weight:600;color:#475569;margin-bottom:6px">No refactoring yet</div>
              <div>Paste your code and click <strong>Refactor Code</strong></div>
            </div>""", unsafe_allow_html=True)

    if ref_btn:
        src = raw_code.strip()
        if not src:
            st.warning("Paste some code first.")
        elif not api_key:
            st.error("Add your API key in the sidebar.")
        else:
            goals_str = ", ".join(goals) if goals else "general improvements"
            with st.spinner("♻️ Refactoring…"):
                try:
                    res, tok = call_groq(
                        [{"role": "system", "content": SYS_REFACTOR},
                         {"role": "user",   "content": f"Focus on: {goals_str}\n\n```python\n{src}\n```"}],
                        temp=0.1)
                    rc_code, expl = parse_code(res)
                    st.session_state.refactor_code        = rc_code or res
                    st.session_state.refactor_explanation = expl
                    st.session_state.total_tokens        += tok
                    st.rerun()
                except Exception as e:
                    st.error(f"Refactor failed: {e}")

# ═══════════════════════════════════════
# TAB 4 — TESTS
# ═══════════════════════════════════════
with tab_tests:
    st.markdown('<div class="sec-title">🧪 Test Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Auto-generate pytest tests covering happy paths, edge cases, and error handling.</div>', unsafe_allow_html=True)

    tl, tr = st.columns([1, 1], gap="large")
    with tl:
        test_src = st.text_area("Paste code to test", height=200,
            placeholder="def add(a: int, b: int) -> int:\n    return a + b")
        test_style = st.radio("Test framework", ["pytest", "unittest"], horizontal=True)

        tc1, tc2 = st.columns(2)
        test_btn = tc1.button("🧪 Generate Tests", type="primary", use_container_width=True)
        if tc2.button("📥 Load from Builder", use_container_width=True, key="tst_load"):
            if st.session_state.active_code:
                st.session_state["_tst_pre"] = st.session_state.active_code
                st.rerun()
            else:
                st.warning("No active code in Builder yet.")

        if "_tst_pre" in st.session_state:
            test_src = st.session_state.pop("_tst_pre")

    with tr:
        if st.session_state.test_code:
            st.markdown('<div class="card-amber"><strong>✅ Tests Generated</strong></div>', unsafe_allow_html=True)
            st.code(st.session_state.test_code, language="python")
            st.download_button("⬇️ Download test_app.py",
                data=st.session_state.test_code, file_name="test_app.py",
                mime="text/plain", use_container_width=True)
            st.markdown("""
            <div class="card-blue" style="margin-top:10px">
            <strong>▶ Run tests:</strong><br>
            <code>pip install pytest &amp;&amp; pytest test_app.py -v</code>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
              <div style="font-size:38px;margin-bottom:10px">🧪</div>
              <div style="font-weight:600;color:#475569;margin-bottom:6px">No tests yet</div>
              <div>Paste code and click <strong>Generate Tests</strong></div>
            </div>""", unsafe_allow_html=True)

    if test_btn:
        src = test_src.strip() or st.session_state.active_code
        if not src:
            st.warning("Paste code or load from Builder first.")
        elif not api_key:
            st.error("Add your API key in the sidebar.")
        else:
            with st.spinner("🧪 Writing tests…"):
                try:
                    res, tok = call_groq(
                        [{"role": "system", "content": SYS_TESTS},
                         {"role": "user",
                          "content": f"Write comprehensive {test_style} tests:\n```python\n{src[:5000]}\n```"}],
                        max_tok=4000, temp=0.05)
                    tc_code, _ = parse_code(res)
                    st.session_state.test_code     = tc_code or res
                    st.session_state.total_tokens += tok
                    st.rerun()
                except Exception as e:
                    st.error(f"Test generation failed: {e}")

# ═══════════════════════════════════════
# TAB 5 — CHAT
# ═══════════════════════════════════════
with tab_chat:
    st.markdown('<div class="sec-title">💬 Senior Dev Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Ask anything — code reviews, architecture, debugging, best practices.</div>', unsafe_allow_html=True)

    # Quick action buttons
    qa1, qa2, qa3, qa4 = st.columns(4)
    def _chat_send(user_msg: str):
        """Append user message and immediately get AI reply."""
        if not api_key:
            st.error("Add your API key in the sidebar.")
            return
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        try:
            msgs = [{"role": "system", "content": SYS_CHAT}]
            msgs += [{"role": m["role"], "content": m["content"]}
                     for m in st.session_state.chat_history[-20:]]
            reply, tok = call_groq(msgs, max_tok=4000, temp=0.3)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.session_state.total_tokens += tok
        except Exception as e:
            st.session_state.chat_history.append({"role": "assistant", "content": f"⚠️ Error: {e}"})
        st.rerun()

    if qa1.button("📋 Review code", use_container_width=True):
        if st.session_state.active_code:
            _chat_send(f"Please review this code and suggest improvements:\n```python\n{st.session_state.active_code[:3000]}\n```")
        else:
            st.warning("Generate code in Builder first.")
    if qa2.button("📦 Best libraries", use_container_width=True):
        _chat_send("What are the best Python libraries for data science and ML in 2025? Give a quick rundown.")
    if qa3.button("⚡ Perf tips", use_container_width=True):
        _chat_send("Give me the top 5 Python performance optimisation tips with short code examples.")
    if qa4.button("🔒 Security audit", use_container_width=True):
        if st.session_state.active_code:
            _chat_send(f"Do a security review of this code:\n```python\n{st.session_state.active_code[:3000]}\n```")
        else:
            st.warning("Generate code in Builder first.")

    # Render chat
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle quick-action replies (when history was appended and rerun happened)
    last = st.session_state.chat_history[-1] if st.session_state.chat_history else None
    if last and last["role"] == "user" and api_key:
        # Auto-reply to quick actions
        needs_reply = len(st.session_state.chat_history) >= 2 and \
                      st.session_state.chat_history[-2]["role"] != "assistant" or \
                      st.session_state.chat_history[-1]["role"] == "user" and \
                      (len(st.session_state.chat_history) == 1 or
                       st.session_state.chat_history[-2]["role"] == "user")
        # Simpler check: if last message is from user and no response yet
        # We just rely on chat_input to trigger responses

    # Chat input
    if user_input := st.chat_input("Ask anything… paste code or an error…"):
        if not api_key:
            st.error("Add your API key in the sidebar.")
        else:
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        msgs = [{"role": "system", "content": SYS_CHAT}]
                        msgs += [{"role": m["role"], "content": m["content"]}
                                 for m in st.session_state.chat_history[-20:]]
                        reply, tok = call_groq(msgs, max_tok=4000, temp=0.3)
                        st.markdown(reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": reply})
                        st.session_state.total_tokens += tok
                    except Exception as e:
                        st.error(f"Chat error: {e}")



    if len(st.session_state.chat_history) > 1:
        if st.button("🗑️ Clear chat", use_container_width=False):
            st.session_state.chat_history = [{"role": "assistant", "content": "Chat cleared. Ask me anything!"}]
            st.rerun()

# ═══════════════════════════════════════
# TAB 6 — DOCS
# ═══════════════════════════════════════
with tab_docs:
    st.markdown('<div class="sec-title">📄 Docs Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Generate professional GitHub READMEs, API references, and developer guides.</div>', unsafe_allow_html=True)

    dol, dor = st.columns([1, 1], gap="large")
    with dol:
        doc_name = st.text_input("Project name", placeholder="e.g. DataViz Pro")
        doc_desc = st.text_area("Project description", height=110,
            placeholder="Describe the app, features, and tech stack.")
        doc_code = st.text_area("Source code (optional)", height=90,
            placeholder="Paste source code for more accurate docs…")
        doc_types = st.multiselect("What to generate",
            ["GitHub README", "API Reference", "Developer Guide", "User Manual", "Changelog Template"],
            default=["GitHub README"])

        docb1, docb2 = st.columns(2)
        doc_btn = docb1.button("📄 Generate Docs", type="primary", use_container_width=True)
        if docb2.button("📥 Load code from Builder", use_container_width=True, key="doc_load"):
            if st.session_state.active_code:
                st.session_state["_doc_pre"] = st.session_state.active_code
                st.rerun()
            else:
                st.warning("No active code in Builder yet.")

        if "_doc_pre" in st.session_state:
            doc_code = st.session_state.pop("_doc_pre")

    with dor:
        if st.session_state.doc_result:
            st.success("✅ Documentation ready:")
            st.markdown(st.session_state.doc_result)
            st.download_button("⬇️ Download README.md",
                data=st.session_state.doc_result, file_name="README.md",
                mime="text/markdown", use_container_width=True)
        else:
            st.markdown("""
            <div class="empty-state">
              <div style="font-size:38px;margin-bottom:10px">📄</div>
              <div style="font-weight:600;color:#475569;margin-bottom:6px">No docs yet</div>
              <div>Fill in the details and click <strong>Generate Docs</strong></div>
            </div>""", unsafe_allow_html=True)

    if doc_btn:
        if not doc_desc.strip():
            st.warning("Provide at least a description.")
        elif not api_key:
            st.error("Add your API key in the sidebar.")
        else:
            parts = [f"Project: {doc_name or 'My App'}", f"Description: {doc_desc}"]
            if doc_code.strip():
                parts.append(f"Source code:\n```python\n{doc_code[:3000]}\n```")
            parts.append(f"Generate: {', '.join(doc_types) if doc_types else 'GitHub README'}")
            parts.append("Use Markdown. Be professional and comprehensive. Include shields.io badges.")
            with st.spinner("📝 Writing documentation…"):
                try:
                    res, tok = call_groq(
                        [{"role": "system", "content": SYS_DOCS},
                         {"role": "user",   "content": "\n\n".join(parts)}],
                        max_tok=4000, temp=0.3)
                    st.session_state.doc_result    = res
                    st.session_state.total_tokens += tok
                    st.rerun()
                except Exception as e:
                    st.error(f"Docs generation failed: {e}")

# ═══════════════════════════════════════
# TAB 7 — HISTORY
# ═══════════════════════════════════════
with tab_history:
    st.markdown('<div class="sec-title">🕓 Build History</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Every build from this session — reload, download, or review any of them.</div>', unsafe_allow_html=True)

    if not st.session_state.build_history:
        st.markdown("""
        <div class="empty-state">
          <div style="font-size:38px;margin-bottom:10px">🕓</div>
          <div style="font-weight:600;color:#475569;margin-bottom:6px">No builds yet</div>
          <div>Go to <strong>Builder</strong> tab to generate your first app</div>
        </div>""", unsafe_allow_html=True)
    else:
        total_tok = sum(b.get("tokens", 0) for b in st.session_state.build_history)
        hm1, hm2, hm3 = st.columns(3)
        hm1.metric("Total Builds",  len(st.session_state.build_history))
        hm2.metric("Total Tokens",  f"{total_tok:,}")
        hm3.metric("Models Used",   len({b["model"] for b in st.session_state.build_history}))
        st.divider()

        for _idx, item in enumerate(reversed(st.session_state.build_history)):
            bid = item.get("id", len(st.session_state.build_history) - _idx)
            label = item["prompt"][:80] + ("…" if len(item["prompt"]) > 80 else "")
            with st.expander(f"**#{bid}** — {label}"):
                st.markdown(
                    f'<div class="hist-meta">🕐 {item["ts"]} &nbsp;·&nbsp; '
                    f'🤖 {item["model"]} &nbsp;·&nbsp; '
                    f'🔧 {item["framework"]} &nbsp;·&nbsp; '
                    f'🔤 {item["tokens"]:,} tokens</div>',
                    unsafe_allow_html=True)

                st.markdown(f"**Prompt:** {item['prompt']}")
                st.divider()

                hct, het = st.tabs(["📋 Code", "📖 Explanation"])
                with hct:
                    st.code(item["code"], language="python")
                    hc1, hc2, hc3 = st.columns(3)
                    hc1.download_button("⬇️ .py",
                        data=item["code"], file_name=f"build_{bid}.py",
                        mime="text/plain", key=f"dl_py_{bid}", use_container_width=True)
                    hc2.download_button("📦 .zip",
                        data=make_zip(item["code"], item.get("setup",""), item["prompt"][:30]),
                        file_name=f"build_{bid}.zip", mime="application/zip",
                        key=f"dl_zip_{bid}", use_container_width=True)
                    if hc3.button("📥 Load as Active", key=f"load_h_{bid}", use_container_width=True):
                        st.session_state.active_code        = item["code"]
                        st.session_state.active_explanation = item.get("explanation","")
                        st.session_state.active_setup       = item.get("setup","")
                        st.success(f"✅ Build #{bid} loaded! Switch to Builder tab.")
                with het:
                    st.markdown(item.get("explanation") or "_No explanation recorded._")
