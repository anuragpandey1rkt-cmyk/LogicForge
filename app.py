import streamlit as st
from groq import Groq
import re
import zipfile
import io
from datetime import datetime

# ══════════════════════════════════════════════
# 1. SESSION STATE
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
    "sidebar_open":        True,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ══════════════════════════════════════════════
# 2. PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="LogicForge AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded" if st.session_state.sidebar_open else "collapsed",
)

# ══════════════════════════════════════════════
# 3. CSS
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

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div { color: var(--text) !important; }

/* Hide Streamlit's own arrow — we use our button */
[data-testid="collapsedControl"] { display: none !important; }

h1,h2,h3,h4 { font-family:'Inter',sans-serif !important; font-weight:700 !important; color:var(--text) !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important; padding: 4px !important;
    gap: 2px !important; flex-wrap: wrap !important; box-shadow: var(--shadow) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--text2) !important;
    border-radius: 8px !important; font-family:'Inter',sans-serif !important;
    font-weight: 600 !important; font-size: 13px !important; padding: 8px 14px !important; border: none !important;
}
.stTabs [aria-selected="true"] { background: var(--accent) !important; color: #fff !important; }
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) { background: var(--accent-lt) !important; color: var(--accent) !important; }

/* Buttons */
.stButton > button {
    background: var(--accent) !important; color: #fff !important;
    font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
    border: none !important; border-radius: var(--radius) !important;
    font-size: 14px !important; padding: 10px 20px !important;
    transition: all 0.2s ease !important; box-shadow: 0 2px 8px rgba(79,70,229,0.25) !important;
}
.stButton > button:hover { background: var(--accent-h) !important; transform: translateY(-1px) !important; box-shadow: 0 4px 16px rgba(79,70,229,0.35) !important; }

/* Sidebar toggle btn — ghost style inside header */
.sb-toggle-wrap > button {
    background: rgba(255,255,255,0.2) !important;
    border: 1.5px solid rgba(255,255,255,0.35) !important;
    border-radius: 10px !important; font-size: 18px !important;
    width: 44px !important; height: 44px !important; padding: 0 !important;
    box-shadow: none !important; color: #fff !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
.sb-toggle-wrap > button:hover { background: rgba(255,255,255,0.35) !important; transform: none !important; box-shadow: none !important; }

.stDownloadButton > button { background: var(--green) !important; color: white !important; border: none !important; box-shadow: 0 2px 8px rgba(5,150,105,0.25) !important; }
.stDownloadButton > button:hover { background: #047857 !important; box-shadow: 0 4px 16px rgba(5,150,105,0.35) !important; }

.stTextArea textarea,
.stTextInput > div > div > input {
    background: var(--surface) !important; border: 1.5px solid var(--border) !important;
    color: var(--text) !important; font-family: 'Inter', sans-serif !important;
    border-radius: var(--radius) !important; font-size: 14px !important;
}
.stTextArea textarea:focus,
.stTextInput > div > div > input:focus { border-color: var(--accent) !important; box-shadow: 0 0 0 3px rgba(79,70,229,0.12) !important; }
.stTextArea textarea::placeholder,
.stTextInput > div > div > input::placeholder { color: var(--text3) !important; }

label, p { color: var(--text) !important; }
.stSelectbox label, .stTextArea label, .stTextInput label,
.stRadio label, .stMultiSelect label, .stSlider label { color: var(--text) !important; font-weight: 600 !important; font-size: 13px !important; }

.stCodeBlock, pre { background: #1e1b4b !important; border: 1px solid #312e81 !important; border-radius: var(--radius) !important; }
.stCodeBlock code, pre code { font-family: 'JetBrains Mono', monospace !important; color: #e0e7ff !important; }

[data-testid="stMetric"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; padding: 12px 16px !important; box-shadow: var(--shadow) !important; }
[data-testid="stMetricValue"] { color: var(--accent) !important; font-weight: 700 !important; }
[data-testid="stMetricLabel"] { color: var(--text2) !important; }

[data-testid="stChatMessage"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; box-shadow: var(--shadow) !important; margin-bottom: 8px !important; }

.streamlit-expanderHeader { background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: var(--radius) !important; color: var(--text) !important; font-weight: 600 !important; }

.stAlert, [data-baseweb="notification"] { border-radius: var(--radius) !important; }
.stSpinner > div { border-top-color: var(--accent) !important; }
.stRadio label span, .stCheckbox label span { color: var(--text) !important; }
.stMultiSelect [data-baseweb="tag"] { background: var(--accent) !important; color: white !important; border-radius: 6px !important; }

.sec-title { font-size: 17px; font-weight: 700; color: var(--text); margin-bottom: 2px; }
.sec-sub   { font-size: 13px; color: var(--text2); margin-bottom: 16px; }

.card-green { background: var(--green-lt); border: 1px solid #a7f3d0; border-left: 4px solid var(--green); border-radius: var(--radius); padding: 14px 18px; margin-bottom: 12px; color: var(--text); }
.card-blue  { background: var(--blue-lt);  border: 1px solid #bfdbfe; border-left: 4px solid var(--blue);  border-radius: var(--radius); padding: 14px 18px; margin-bottom: 12px; color: var(--text); }
.card-amber { background: var(--amber-lt); border: 1px solid #fde68a; border-left: 4px solid var(--amber); border-radius: var(--radius); padding: 14px 18px; margin-bottom: 12px; color: var(--text); }

.empty-state { background: var(--surface2); border: 2px dashed var(--border); border-radius: var(--radius); padding: 40px 20px; text-align: center; color: var(--text3); font-size: 14px; }
.hist-meta  { font-size: 11px; color: var(--text3); font-family: 'JetBrains Mono', monospace; margin-top: 4px; }

/* ══════════════════════════════════════════════
   DESKTOP HEADER BOX
══════════════════════════════════════════════ */
.desk-header-box {
    background: linear-gradient(135deg,#4f46e5 0%,#7c3aed 50%,#2563eb 100%);
    border-radius: 15px; padding: 18px 22px;
    box-shadow: var(--shadow-lg);
}

/* ══════════════════════════════════════════════
   MOBILE HEADER  (compact pill)
══════════════════════════════════════════════ */
.mob-header {
    display: none;
    align-items: center; gap: 10px;
    padding: 12px 58px 12px 14px;
    background: linear-gradient(135deg,#4f46e5,#7c3aed 60%,#2563eb);
    border-radius: 14px; margin-bottom: 12px;
    box-shadow: var(--shadow-lg);
}
.mob-h-title { font-size: 17px; font-weight: 800; color: white !important; margin: 0; line-height: 1.2; }
.mob-h-sub   { font-size: 11px; color: rgba(255,255,255,0.72) !important; margin: 2px 0 0; }
.mob-badge   {
    margin-left: auto; flex-shrink: 0;
    background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px; padding: 3px 10px;
    font-size: 10px; font-weight: 700; color: white;
    font-family: 'JetBrains Mono', monospace; white-space: nowrap;
}

/* ══════════════════════════════════════════════
   MOBILE DRAWER
══════════════════════════════════════════════ */
#lf-drawer-toggle { position:fixed; opacity:0; width:0; height:0; pointer-events:none; }

#lf-drawer-trigger {
    position: fixed; top: 10px; right: 12px;
    z-index: 999999; width: 46px; height: 46px;
    background: var(--accent); border-radius: 13px; cursor: pointer;
    display: none;
    flex-direction: column; align-items: center; justify-content: center; gap: 5px;
    box-shadow: 0 4px 16px rgba(79,70,229,0.5);
    transition: background 0.15s, transform 0.12s;
    -webkit-tap-highlight-color: transparent; user-select: none;
}
#lf-drawer-trigger:active { transform: scale(0.93); background: var(--accent-h); }
#lf-drawer-trigger .dot { display: block; width: 5px; height: 5px; background: #fff; border-radius: 50%; }

#lf-drawer-backdrop {
    display: none; position: fixed; inset: 0;
    background: rgba(10,10,30,0.55); z-index: 999997;
    backdrop-filter: blur(2px); cursor: pointer;
}

#lf-drawer-panel {
    position: fixed; top: 0; left: 0;
    width: min(300px, 90vw); height: 100dvh;
    background: var(--surface); border-right: 1px solid var(--border);
    box-shadow: 8px 0 40px rgba(79,70,229,0.2);
    z-index: 999998; transform: translateX(-110%);
    transition: transform 0.28s cubic-bezier(0.4,0,0.2,1);
    overflow-y: auto; overflow-x: hidden;
    padding: 0; box-sizing: border-box;
}

#lf-panel-hdr {
    background: linear-gradient(135deg,#4f46e5,#7c3aed);
    padding: 20px 16px 16px;
    position: sticky; top: 0; z-index: 1;
    display: flex; align-items: center; justify-content: space-between;
}

#lf-drawer-close {
    width: 32px; height: 32px;
    background: rgba(255,255,255,0.18); border-radius: 8px; cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; font-weight: 800; color: white;
    -webkit-tap-highlight-color: transparent; user-select: none;
    transition: background 0.15s; flex-shrink: 0;
}
#lf-drawer-close:active { background: rgba(255,255,255,0.32); }

.p-body   { padding: 16px; }
.p-label  { font-size:10px; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:.8px; margin:0 0 6px; display:block; }
.p-divider{ border:none; border-top:1px solid var(--border); margin:14px 0; }

.p-status {
    display:flex; align-items:center; gap:6px;
    padding:10px 12px; border-radius:10px;
    font-size:13px; font-weight:600; margin-bottom:14px;
    width:100%; box-sizing:border-box;
}

.p-select {
    width:100%; padding:10px 34px 10px 12px;
    background:var(--surface2); border:1.5px solid var(--border);
    border-radius:10px; color:var(--text);
    font-family:'Inter',sans-serif; font-size:14px; font-weight:500;
    outline:none; cursor:pointer; appearance:none; -webkit-appearance:none;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%234f46e5' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
    background-repeat:no-repeat; background-position:right 12px center;
    margin-bottom:14px;
}
.p-select:focus { border-color:var(--accent); box-shadow:0 0 0 3px rgba(79,70,229,0.12); }

.p-stat-row { display:flex; gap:10px; margin-bottom:14px; }
.p-stat { flex:1; background:#eef2ff; border:1px solid #c7d2fe; border-radius:12px; padding:14px 8px; text-align:center; }
.p-stat-val { font-size:28px; font-weight:800; color:var(--accent); line-height:1; }
.p-stat-lbl { font-size:10px; color:#6366f1; margin-top:4px; font-weight:700; text-transform:uppercase; letter-spacing:.5px; }

.p-tip { background:#f1f5f9; border-radius:10px; padding:12px 14px; font-size:12px; color:#64748b; line-height:1.6; text-align:center; }

#lf-drawer-toggle:checked ~ #lf-drawer-backdrop { display:block; }
#lf-drawer-toggle:checked ~ #lf-drawer-panel    { transform:translateX(0); }

/* ══════════════════════════════════════════════
   RESPONSIVE
══════════════════════════════════════════════ */
@media (max-width: 768px) {
    [data-testid="stSidebar"],
    section[data-testid="stSidebarContent"] { display:none !important; }

    #lf-drawer-trigger { display:flex !important; }
    .mob-header        { display:flex !important; }
    .desk-header-row   { display:none !important; }
    .sb-toggle-wrap    { display:none !important; }

    [data-testid="stMainBlockContainer"] { padding:8px 10px 24px !important; }

    .stTabs [data-baseweb="tab-list"] { gap:2px !important; padding:3px !important; }
    .stTabs [data-baseweb="tab"]      { font-size:11px !important; padding:7px 8px !important; }

    .stButton > button          { font-size:13px !important; padding:9px 12px !important; }
    .stDownloadButton > button  { font-size:13px !important; }
    [data-testid="stMetric"]    { padding:10px 12px !important; }
    .sec-title                  { font-size:15px !important; }
    .sec-sub                    { font-size:12px !important; }
    .empty-state                { padding:24px 14px !important; }

    /* Stack 2-col layouts to single column on mobile */
    [data-testid="stHorizontalBlock"]      { flex-wrap:wrap !important; }
    [data-testid="stHorizontalBlock"] > div{ min-width:100% !important; flex:1 1 100% !important; }

    [data-testid="stChatInput"] textarea   { font-size:14px !important; }
}

@media (min-width: 769px) {
    #lf-drawer-trigger  { display:none !important; }
    #lf-drawer-backdrop { display:none !important; }
    #lf-drawer-panel    { display:none !important; }
    #lf-drawer-toggle   { display:none !important; }
    .mob-header         { display:none !important; }
}

@media (max-width: 420px) {
    .mob-h-title { font-size:15px !important; }
    .mob-badge   { display:none !important; }
    .stTabs [data-baseweb="tab"] { font-size:10px !important; padding:6px 6px !important; }
}

#MainMenu, footer { visibility:hidden; }
[data-testid="stToolbar"] { display:none; }
</style>
""", unsafe_allow_html=True)

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
# 5. CONSTANTS
# ══════════════════════════════════════════════
MODEL_MAP = {
    "llama-3.3-70b-versatile":                       "🧠 Llama 3.3 70B — Best quality",
    "llama-3.1-8b-instant":                          "⚡ Llama 3.1 8B — Fastest",
    "meta-llama/llama-4-maverick-17b-128e-instruct": "🦙 Llama 4 Maverick — Latest",
}
FRAMEWORKS = ["Streamlit", "FastAPI", "Flask", "Django", "Pure Python", "CLI Tool"]

# ══════════════════════════════════════════════
# 6. SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚡ LogicForge")
    st.caption("AI Code Architect · v2.0")
    st.divider()

    if not api_key:
        st.markdown("### 🔑 API Key")
        entered = st.text_input("API Key", type="password",
                                placeholder="Enter your API key…", label_visibility="collapsed")
        if entered:
            st.session_state.groq_api_key = entered
            api_key = entered
            st.success("✅ Key saved!")
        else:
            st.info("🔑 Enter your API key above to start")
        st.divider()

    st.markdown("### ⚙️ Settings")
    model = st.selectbox("Model", list(MODEL_MAP.keys()), format_func=lambda x: MODEL_MAP[x], index=0)
    framework = st.selectbox("Framework", FRAMEWORKS)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05)
    max_tokens = st.select_slider("Max Tokens", options=[2000,4000,6000,8000,12000], value=8000)
    st.divider()
    st.markdown("### 📊 Session Stats")
    c1, c2 = st.columns(2)
    c1.metric("🏗️ Builds", st.session_state.total_builds)
    tok_val = st.session_state.total_tokens
    tok_sb  = f"{tok_val/1000:.1f}k" if tok_val >= 1000 else str(tok_val)
    c2.metric("🔤 Tokens", tok_sb)
    st.divider()
    if st.button("🗑️ Reset Session", use_container_width=True):
        for k, v in _defaults.items():
            st.session_state[k] = v
        st.rerun()

# ══════════════════════════════════════════════
# 7. HELPERS
# ══════════════════════════════════════════════
def call_groq(messages, max_tok=None, temp=None):
    if not api_key:
        st.error("⚠️ Add your API key in the sidebar first.")
        st.stop()
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=model, messages=messages,
        temperature=temp if temp is not None else temperature,
        max_tokens=max_tok or max_tokens,
    )
    return resp.choices[0].message.content or "", getattr(resp.usage, "total_tokens", 0)

def parse_code(text):
    m = re.search(r"```python\s*(.*?)```", text, re.DOTALL) or \
        re.search(r"```\s*([\s\S]*?)```", text)
    if m:
        return m.group(1).strip(), (text[:m.start()] + text[m.end():]).strip()
    return "", text.strip()

def make_zip(code, setup, name="app"):
    safe = re.sub(r"[^\w]", "_", name.lower())[:40] or "app"
    reqs = "\n".join(
        ln.strip().lstrip("-*• ").strip() for ln in setup.splitlines()
        if ln.strip() and not ln.strip().startswith("#") and " " not in ln.strip()
    ) or "streamlit\ngroq"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{safe}.py", code)
        z.writestr("requirements.txt", reqs)
        z.writestr("README.md", f"# {name}\n\nGenerated by LogicForge AI.\n\n## Quick start\n"
                   f"```bash\npip install -r requirements.txt\nstreamlit run {safe}.py\n```\n")
    return buf.getvalue()

# ══════════════════════════════════════════════
# 8. SYSTEM PROMPTS
# ══════════════════════════════════════════════
def SYS_BUILD(fw):
    return (f"You are a Senior Python Developer. Write COMPLETE, FUNCTIONAL, PRODUCTION-READY {fw} code.\n\n"
            "RULES:\n1. Include ALL imports.\n2. No stubs or TODOs.\n3. Type hints & docstrings.\n\n"
            "OUTPUT FORMAT:\n### SECTION 1: THE CODE\n```python\n<code>\n```\n\n"
            "### SECTION 2: EXPLANATION\n<explanation>\n\n### SECTION 3: SETUP\n<pip packages, one per line>")

SYS_DEBUG    = ("You are a Senior Python Developer specializing in debugging.\nReturn COMPLETE fixed code then list every fix.\n\nFORMAT:\n```python\n<fixed code>\n```\n\n### FIXES\n- Fix 1: ...")
SYS_REFACTOR = ("You are a Senior Python Developer focused on code quality.\nRefactor for PEP 8, type hints, docstrings, DRY, performance.\nReturn COMPLETE refactored code then changelog.\n\nFORMAT:\n```python\n<code>\n```\n\n### CHANGES\n- Change 1: ...")
SYS_TESTS    = ("Write comprehensive pytest tests. Return ONLY a python code block.\n```python\n<test file>\n```")
SYS_CHAT     = ("You are a Senior Python Developer with 15 years experience. Help with code reviews, debugging, architecture. Use ```python blocks for all code.")
SYS_DOCS     = ("You are a Technical Writer. Write professional Markdown documentation. Include shields.io badges, code examples. Publish-ready for GitHub.")

# ══════════════════════════════════════════════
# 9. DESKTOP HEADER  (hidden on mobile by CSS)
# ══════════════════════════════════════════════
st.markdown('<div class="desk-header-row">', unsafe_allow_html=True)
h_btn, h_txt, h_bdg = st.columns([0.055, 0.785, 0.16])

with h_btn:
    st.markdown('<div class="sb-toggle-wrap">', unsafe_allow_html=True)
    icon = "✕" if st.session_state.sidebar_open else "☰"
    if st.button(icon, key="sb_toggle"):
        st.session_state.sidebar_open = not st.session_state.sidebar_open
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with h_txt:
    st.markdown("""<div class="desk-header-box">
      <div style="font-size:clamp(18px,2.8vw,26px);font-weight:800;color:white;margin:0">⚡ LogicForge AI Architect</div>
      <div style="font-size:13px;color:rgba(255,255,255,0.78);margin-top:4px">Build · Debug · Refactor · Test · Document — all in one place</div>
    </div>""", unsafe_allow_html=True)

with h_bdg:
    st.markdown("""<div style="background:linear-gradient(135deg,#4f46e5,#2563eb);border-radius:14px;
                padding:14px 8px;text-align:center;color:white;
                display:flex;flex-direction:column;align-items:center;justify-content:center;
                gap:4px;box-shadow:0 4px 14px rgba(79,70,229,0.3);min-height:76px;">
      <div style="font-size:20px">⚡</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700">v2.0</div>
      <div style="font-size:10px;opacity:.75">AI Powered</div>
    </div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 10. MOBILE HEADER  (hidden on desktop by CSS)
# ══════════════════════════════════════════════
st.markdown("""<div class="mob-header">
  <div>
    <div class="mob-h-title">⚡ LogicForge</div>
    <div class="mob-h-sub">AI Code Architect · v2.0</div>
  </div>
  <span class="mob-badge">v2.0</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 11. API WARNING
# ══════════════════════════════════════════════
if not api_key:
    st.warning("⚠️ **No API key.** Open ⋮ (mobile) or click ☰ (desktop) to add your key.")

# ══════════════════════════════════════════════
# 12. MOBILE DRAWER
# ══════════════════════════════════════════════
_builds  = st.session_state.total_builds
_tok     = st.session_state.total_tokens
_tok_str = f"{_tok/1000:.1f}k" if _tok >= 1000 else str(_tok)
_key_ok  = bool(api_key)
_k_lbl   = "✅ API key active" if _key_ok else "⚠️ No API key"
_k_color = "#059669" if _key_ok else "#d97706"
_k_bg    = "#ecfdf5" if _key_ok else "#fffbeb"
_k_bord  = "1px solid #a7f3d0" if _key_ok else "1px solid #fde68a"

_model_opts = "".join(
    f'<option value="{k}" {"selected" if i==0 else ""}>{v}</option>'
    for i,(k,v) in enumerate(MODEL_MAP.items()))
_fw_opts = "".join(
    f'<option value="{fw}" {"selected" if fw==FRAMEWORKS[0] else ""}>{fw}</option>'
    for fw in FRAMEWORKS)

st.markdown(f"""
<input type="checkbox" id="lf-drawer-toggle">

<label for="lf-drawer-toggle" id="lf-drawer-trigger" title="Menu">
  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
</label>

<label for="lf-drawer-toggle" id="lf-drawer-backdrop"></label>

<div id="lf-drawer-panel">
  <div id="lf-panel-hdr">
    <div>
      <div style="font-size:18px;font-weight:800;color:white">⚡ LogicForge</div>
      <div style="font-size:11px;color:rgba(255,255,255,0.7);margin-top:1px">AI Code Architect · v2.0</div>
    </div>
    <label for="lf-drawer-toggle" id="lf-drawer-close">✕</label>
  </div>

  <div class="p-body">
    <div class="p-status" style="background:{_k_bg};border:{_k_bord};color:{_k_color};">{_k_lbl}</div>
    <hr class="p-divider">

    <span class="p-label">🤖 Model</span>
    <select class="p-select">{_model_opts}</select>

    <span class="p-label">🔧 Framework</span>
    <select class="p-select">{_fw_opts}</select>

    <div style="font-size:11px;color:#94a3b8;margin-bottom:14px;background:#f8faff;
                border:1px solid #e2e8f0;border-radius:8px;padding:8px 10px;line-height:1.5">
      ℹ️ Shown for reference — to apply, change via sidebar on desktop.
    </div>

    <hr class="p-divider">
    <span class="p-label">📊 Session Stats</span>
    <div class="p-stat-row">
      <div class="p-stat"><div class="p-stat-val">{_builds}</div><div class="p-stat-lbl">Builds</div></div>
      <div class="p-stat"><div class="p-stat-val">{_tok_str}</div><div class="p-stat-lbl">Tokens</div></div>
    </div>

    <div class="p-tip">💡 For temperature &amp; max tokens, open on <strong>desktop</strong></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 13. TABS
# ══════════════════════════════════════════════
tab_build, tab_debug, tab_refactor, tab_tests, tab_chat, tab_docs, tab_history = st.tabs([
    "🏗️ Builder", "🐛 Debugger", "♻️ Refactor", "🧪 Tests", "💬 Chat", "📄 Docs", "🕓 History",
])

# ═══════════════════════ TAB 1 — BUILDER ═══════════════════════
with tab_build:
    st.markdown('<div class="sec-title">🏗️ App Builder</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sec-sub">Describe your app — get complete, runnable {framework} code instantly.</div>', unsafe_allow_html=True)

    bl, br = st.columns([1,1], gap="large")
    with bl:
        user_req = st.text_area("Describe your app", height=150,
            placeholder="E.g. A Streamlit dashboard with live crypto prices, candlestick charts, and P&L tracker.")
        extra = st.text_area("Extra constraints (optional)", height=65,
            placeholder="E.g. Use plotly. Add caching. Support CSV export.")
        with st.expander("⚙️ Extra options"):
            also_tests  = st.checkbox("Also generate unit tests")
            also_readme = st.checkbox("Also generate README")
        build_btn = st.button("⚡ Generate Full Code", type="primary", use_container_width=True)

    with br:
        if st.session_state.active_code:
            ct, ce, cs = st.tabs(["📋 Code","📖 Explanation","📦 Setup"])
            with ct:
                st.code(st.session_state.active_code, language="python")
                dc1, dc2 = st.columns(2)
                dc1.download_button("⬇️ .py", data=st.session_state.active_code,
                    file_name="app.py", mime="text/plain", use_container_width=True)
                dc2.download_button("📦 .zip",
                    data=make_zip(st.session_state.active_code, st.session_state.active_setup,
                                  user_req[:40] if user_req else "app"),
                    file_name="logicforge_app.zip", mime="application/zip", use_container_width=True)
            with ce: st.markdown(st.session_state.active_explanation or "_No explanation._")
            with cs:
                st.markdown(st.session_state.active_setup) if st.session_state.active_setup else st.info("No setup info.")
        else:
            st.markdown("""<div class="empty-state">
              <div style="font-size:36px;margin-bottom:8px">🏗️</div>
              <div style="font-weight:600;color:#475569;margin-bottom:4px">No code yet</div>
              <div>Describe your app and hit <strong>Generate Full Code</strong></div>
            </div>""", unsafe_allow_html=True)

    if build_btn:
        if not user_req.strip(): st.warning("Please describe your app idea.")
        elif not api_key: st.error("Add your API key first.")
        else:
            prompt = f"Framework: {framework}\nTask: {user_req}"
            if extra.strip(): prompt += f"\nConstraints: {extra}"
            with st.spinner("⚡ Building your app…"):
                try:
                    full_res, tokens = call_groq(
                        [{"role":"system","content":SYS_BUILD(framework)},{"role":"user","content":prompt}])
                    code, rest = parse_code(full_res)
                    exp_m = re.search(r"(?:SECTION 2|EXPLANATION)[:\s]*(.*?)(?=###\s*SECTION 3|\Z)", rest, re.DOTALL|re.IGNORECASE)
                    explanation = exp_m.group(1).strip() if exp_m else rest
                    set_m = re.search(r"(?:SECTION 3|SETUP)[:\s]*(.*?)$", full_res, re.DOTALL|re.IGNORECASE)
                    setup = set_m.group(1).strip() if set_m else ""
                    st.session_state.active_code        = code or full_res
                    st.session_state.active_explanation = explanation
                    st.session_state.active_setup       = setup
                    st.session_state.total_builds      += 1
                    st.session_state.total_tokens      += tokens
                    st.session_state.build_history.append({
                        "id":st.session_state.total_builds,"prompt":user_req[:150],
                        "code":code or full_res,"explanation":explanation,"setup":setup,
                        "ts":datetime.now().strftime("%d %b %Y, %H:%M"),
                        "model":model,"tokens":tokens,"framework":framework,
                    })
                    if also_tests:
                        tr, _ = call_groq([{"role":"system","content":SYS_TESTS},
                            {"role":"user","content":f"Write pytest tests:\n```python\n{(code or full_res)[:4000]}\n```"}],
                            max_tok=3000, temp=0.05)
                        tc, _ = parse_code(tr)
                        st.session_state.test_code = tc or tr
                    if also_readme:
                        dr, _ = call_groq([{"role":"system","content":SYS_DOCS},
                            {"role":"user","content":f"Write a GitHub README for: {user_req}\nFramework: {framework}"}],
                            max_tok=2000, temp=0.3)
                        st.session_state.doc_result = dr
                    st.success(f"✅ Done! {tokens:,} tokens used.")
                    st.rerun()
                except Exception as e: st.error(f"Build failed: {e}")

# ═══════════════════════ TAB 2 — DEBUGGER ═══════════════════════
with tab_debug:
    st.markdown('<div class="sec-title">🐛 Bug Fixer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Paste broken code + optional traceback → get the fully fixed version.</div>', unsafe_allow_html=True)

    dl, dr = st.columns([1,1], gap="large")
    with dl:
        buggy = st.text_area("Paste buggy code", height=200, placeholder="def greet(name):\n    print('Hello ' + naam)  # NameError!")
        tb = st.text_area("Error / Traceback (optional)", height=80, placeholder="NameError: name 'naam' is not defined")
        col_d1, col_d2 = st.columns(2)
        debug_btn = col_d1.button("🔍 Fix My Code", type="primary", use_container_width=True)
        if col_d2.button("📥 Load from Builder", use_container_width=True, key="dbg_load"):
            if st.session_state.active_code: st.session_state["_dbg_pre"]=st.session_state.active_code; st.rerun()
            else: st.warning("No active code in Builder yet.")
        if "_dbg_pre" in st.session_state: buggy = st.session_state.pop("_dbg_pre")
    with dr:
        if st.session_state.debug_code:
            st.markdown('<div class="card-green"><strong>✅ Fixed Code</strong></div>', unsafe_allow_html=True)
            st.code(st.session_state.debug_code, language="python")
            st.download_button("⬇️ Download Fixed .py", data=st.session_state.debug_code, file_name="fixed_app.py", mime="text/plain", use_container_width=True)
            if st.session_state.debug_explanation:
                with st.expander("📋 What was fixed", expanded=True): st.markdown(st.session_state.debug_explanation)
        else:
            st.markdown("""<div class="empty-state"><div style="font-size:36px;margin-bottom:8px">🐛</div>
              <div style="font-weight:600;color:#475569;margin-bottom:4px">No fixes yet</div>
              <div>Paste buggy code and click <strong>Fix My Code</strong></div></div>""", unsafe_allow_html=True)

    if debug_btn:
        src = buggy.strip()
        if not src: st.warning("Paste some code first.")
        elif not api_key: st.error("Add your API key.")
        else:
            content = f"Buggy code:\n```python\n{src}\n```"
            if tb.strip(): content += f"\n\nTraceback:\n```\n{tb.strip()}\n```"
            with st.spinner("🔍 Analysing bugs…"):
                try:
                    res, tok = call_groq([{"role":"system","content":SYS_DEBUG},{"role":"user","content":content}], temp=0.05)
                    fc, expl = parse_code(res)
                    st.session_state.debug_code=fc or res; st.session_state.debug_explanation=expl; st.session_state.total_tokens+=tok; st.rerun()
                except Exception as e: st.error(f"Debug failed: {e}")

# ═══════════════════════ TAB 3 — REFACTOR ═══════════════════════
with tab_refactor:
    st.markdown('<div class="sec-title">♻️ Code Refactorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Clean up messy code — PEP 8, type hints, docstrings, performance.</div>', unsafe_allow_html=True)

    rl, rr = st.columns([1,1], gap="large")
    with rl:
        raw_code = st.text_area("Paste code to refactor", height=200, placeholder="x=1\ndef f(a,b):\n  return a+b")
        goals = st.multiselect("Refactoring goals",
            ["PEP 8 compliance","Type hints","Docstrings","Performance","DRY principle","Error handling","Add logging"],
            default=["PEP 8 compliance","Type hints","Docstrings"])
        rc1, rc2 = st.columns(2)
        ref_btn = rc1.button("♻️ Refactor Code", type="primary", use_container_width=True)
        if rc2.button("📥 Load from Builder", use_container_width=True, key="ref_load"):
            if st.session_state.active_code: st.session_state["_ref_pre"]=st.session_state.active_code; st.rerun()
            else: st.warning("No active code in Builder yet.")
        if "_ref_pre" in st.session_state: raw_code = st.session_state.pop("_ref_pre")
    with rr:
        if st.session_state.refactor_code:
            st.markdown('<div class="card-blue"><strong>✅ Refactored Code</strong></div>', unsafe_allow_html=True)
            st.code(st.session_state.refactor_code, language="python")
            st.download_button("⬇️ Download Refactored .py", data=st.session_state.refactor_code, file_name="refactored.py", mime="text/plain", use_container_width=True)
            if st.session_state.refactor_explanation:
                with st.expander("📋 Changes made", expanded=True): st.markdown(st.session_state.refactor_explanation)
        else:
            st.markdown("""<div class="empty-state"><div style="font-size:36px;margin-bottom:8px">♻️</div>
              <div style="font-weight:600;color:#475569;margin-bottom:4px">No refactoring yet</div>
              <div>Paste your code and click <strong>Refactor Code</strong></div></div>""", unsafe_allow_html=True)

    if ref_btn:
        src = raw_code.strip()
        if not src: st.warning("Paste some code first.")
        elif not api_key: st.error("Add your API key.")
        else:
            goals_str = ", ".join(goals) if goals else "general improvements"
            with st.spinner("♻️ Refactoring…"):
                try:
                    res, tok = call_groq([{"role":"system","content":SYS_REFACTOR},
                        {"role":"user","content":f"Focus on: {goals_str}\n\n```python\n{src}\n```"}], temp=0.1)
                    rc_code, expl = parse_code(res)
                    st.session_state.refactor_code=rc_code or res; st.session_state.refactor_explanation=expl; st.session_state.total_tokens+=tok; st.rerun()
                except Exception as e: st.error(f"Refactor failed: {e}")

# ═══════════════════════ TAB 4 — TESTS ═══════════════════════
with tab_tests:
    st.markdown('<div class="sec-title">🧪 Test Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Auto-generate pytest tests — happy paths, edge cases, error handling.</div>', unsafe_allow_html=True)

    tl, tr = st.columns([1,1], gap="large")
    with tl:
        test_src = st.text_area("Paste code to test", height=200, placeholder="def add(a: int, b: int) -> int:\n    return a + b")
        test_style = st.radio("Test framework", ["pytest","unittest"], horizontal=True)
        tc1, tc2 = st.columns(2)
        test_btn = tc1.button("🧪 Generate Tests", type="primary", use_container_width=True)
        if tc2.button("📥 Load from Builder", use_container_width=True, key="tst_load"):
            if st.session_state.active_code: st.session_state["_tst_pre"]=st.session_state.active_code; st.rerun()
            else: st.warning("No active code in Builder yet.")
        if "_tst_pre" in st.session_state: test_src = st.session_state.pop("_tst_pre")
    with tr:
        if st.session_state.test_code:
            st.markdown('<div class="card-amber"><strong>✅ Tests Generated</strong></div>', unsafe_allow_html=True)
            st.code(st.session_state.test_code, language="python")
            st.download_button("⬇️ Download test_app.py", data=st.session_state.test_code, file_name="test_app.py", mime="text/plain", use_container_width=True)
            st.markdown('<div class="card-blue" style="margin-top:10px"><strong>▶ Run:</strong> <code>pip install pytest &amp;&amp; pytest test_app.py -v</code></div>', unsafe_allow_html=True)
        else:
            st.markdown("""<div class="empty-state"><div style="font-size:36px;margin-bottom:8px">🧪</div>
              <div style="font-weight:600;color:#475569;margin-bottom:4px">No tests yet</div>
              <div>Paste code and click <strong>Generate Tests</strong></div></div>""", unsafe_allow_html=True)

    if test_btn:
        src = test_src.strip() or st.session_state.active_code
        if not src: st.warning("Paste code or load from Builder first.")
        elif not api_key: st.error("Add your API key.")
        else:
            with st.spinner("🧪 Writing tests…"):
                try:
                    res, tok = call_groq([{"role":"system","content":SYS_TESTS},
                        {"role":"user","content":f"Write comprehensive {test_style} tests:\n```python\n{src[:5000]}\n```"}],
                        max_tok=4000, temp=0.05)
                    tc_code, _ = parse_code(res)
                    st.session_state.test_code=tc_code or res; st.session_state.total_tokens+=tok; st.rerun()
                except Exception as e: st.error(f"Test generation failed: {e}")

# ═══════════════════════ TAB 5 — CHAT ═══════════════════════
with tab_chat:
    st.markdown('<div class="sec-title">💬 Senior Dev Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Ask anything — code reviews, architecture, debugging, best practices.</div>', unsafe_allow_html=True)

    qa1, qa2, qa3, qa4 = st.columns(4)

    def _chat_send(msg):
        if not api_key: st.error("Add your API key."); return
        st.session_state.chat_history.append({"role":"user","content":msg})
        try:
            msgs = [{"role":"system","content":SYS_CHAT}] + \
                   [{"role":m["role"],"content":m["content"]} for m in st.session_state.chat_history[-20:]]
            reply, tok = call_groq(msgs, max_tok=4000, temp=0.3)
            st.session_state.chat_history.append({"role":"assistant","content":reply})
            st.session_state.total_tokens += tok
        except Exception as e:
            st.session_state.chat_history.append({"role":"assistant","content":f"⚠️ Error: {e}"})
        st.rerun()

    if qa1.button("📋 Review code",   use_container_width=True):
        if st.session_state.active_code: _chat_send(f"Review this code:\n```python\n{st.session_state.active_code[:3000]}\n```")
        else: st.warning("Generate code in Builder first.")
    if qa2.button("📦 Best libs",     use_container_width=True): _chat_send("Best Python libraries for data science & ML in 2025?")
    if qa3.button("⚡ Perf tips",     use_container_width=True): _chat_send("Top 5 Python performance optimisation tips with code examples.")
    if qa4.button("🔒 Security",      use_container_width=True):
        if st.session_state.active_code: _chat_send(f"Security review:\n```python\n{st.session_state.active_code[:3000]}\n```")
        else: st.warning("Generate code in Builder first.")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if user_input := st.chat_input("Ask anything…"):
        if not api_key: st.error("Add your API key.")
        else:
            st.session_state.chat_history.append({"role":"user","content":user_input})
            with st.chat_message("user"): st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        msgs = [{"role":"system","content":SYS_CHAT}] + \
                               [{"role":m["role"],"content":m["content"]} for m in st.session_state.chat_history[-20:]]
                        reply, tok = call_groq(msgs, max_tok=4000, temp=0.3)
                        st.markdown(reply)
                        st.session_state.chat_history.append({"role":"assistant","content":reply})
                        st.session_state.total_tokens += tok
                    except Exception as e: st.error(f"Chat error: {e}")

    if len(st.session_state.chat_history) > 1:
        if st.button("🗑️ Clear chat"):
            st.session_state.chat_history = [{"role":"assistant","content":"Chat cleared. Ask me anything!"}]
            st.rerun()

# ═══════════════════════ TAB 6 — DOCS ═══════════════════════
with tab_docs:
    st.markdown('<div class="sec-title">📄 Docs Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Generate professional GitHub READMEs, API refs, and developer guides.</div>', unsafe_allow_html=True)

    dol, dor = st.columns([1,1], gap="large")
    with dol:
        doc_name  = st.text_input("Project name", placeholder="e.g. DataViz Pro")
        doc_desc  = st.text_area("Project description", height=100, placeholder="Describe the app, features, and tech stack.")
        doc_code  = st.text_area("Source code (optional)", height=80, placeholder="Paste source code for more accurate docs…")
        doc_types = st.multiselect("What to generate",
            ["GitHub README","API Reference","Developer Guide","User Manual","Changelog Template"],
            default=["GitHub README"])
        docb1, docb2 = st.columns(2)
        doc_btn = docb1.button("📄 Generate Docs", type="primary", use_container_width=True)
        if docb2.button("📥 Load from Builder", use_container_width=True, key="doc_load"):
            if st.session_state.active_code: st.session_state["_doc_pre"]=st.session_state.active_code; st.rerun()
            else: st.warning("No active code in Builder yet.")
        if "_doc_pre" in st.session_state: doc_code = st.session_state.pop("_doc_pre")
    with dor:
        if st.session_state.doc_result:
            st.success("✅ Documentation ready:")
            st.markdown(st.session_state.doc_result)
            st.download_button("⬇️ Download README.md", data=st.session_state.doc_result, file_name="README.md", mime="text/markdown", use_container_width=True)
        else:
            st.markdown("""<div class="empty-state"><div style="font-size:36px;margin-bottom:8px">📄</div>
              <div style="font-weight:600;color:#475569;margin-bottom:4px">No docs yet</div>
              <div>Fill in details and click <strong>Generate Docs</strong></div></div>""", unsafe_allow_html=True)

    if doc_btn:
        if not doc_desc.strip(): st.warning("Provide at least a description.")
        elif not api_key: st.error("Add your API key.")
        else:
            parts = [f"Project: {doc_name or 'My App'}", f"Description: {doc_desc}"]
            if doc_code.strip(): parts.append(f"Source code:\n```python\n{doc_code[:3000]}\n```")
            parts.append(f"Generate: {', '.join(doc_types) if doc_types else 'GitHub README'}")
            parts.append("Use Markdown. Be professional. Include shields.io badges.")
            with st.spinner("📝 Writing documentation…"):
                try:
                    res, tok = call_groq([{"role":"system","content":SYS_DOCS},{"role":"user","content":"\n\n".join(parts)}], max_tok=4000, temp=0.3)
                    st.session_state.doc_result=res; st.session_state.total_tokens+=tok; st.rerun()
                except Exception as e: st.error(f"Docs failed: {e}")

# ═══════════════════════ TAB 7 — HISTORY ═══════════════════════
with tab_history:
    st.markdown('<div class="sec-title">🕓 Build History</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-sub">Every build from this session — reload, download, or review.</div>', unsafe_allow_html=True)

    if not st.session_state.build_history:
        st.markdown("""<div class="empty-state"><div style="font-size:36px;margin-bottom:8px">🕓</div>
          <div style="font-weight:600;color:#475569;margin-bottom:4px">No builds yet</div>
          <div>Go to <strong>Builder</strong> to generate your first app</div></div>""", unsafe_allow_html=True)
    else:
        total_tok = sum(b.get("tokens",0) for b in st.session_state.build_history)
        hm1, hm2, hm3 = st.columns(3)
        hm1.metric("Total Builds", len(st.session_state.build_history))
        hm2.metric("Total Tokens", f"{total_tok:,}")
        hm3.metric("Models Used",  len({b["model"] for b in st.session_state.build_history}))
        st.divider()

        for _idx, item in enumerate(reversed(st.session_state.build_history)):
            bid   = item.get("id", len(st.session_state.build_history) - _idx)
            label = item["prompt"][:80] + ("…" if len(item["prompt"]) > 80 else "")
            with st.expander(f"**#{bid}** — {label}"):
                st.markdown(f'<div class="hist-meta">🕐 {item["ts"]} &nbsp;·&nbsp; 🤖 {item["model"]} &nbsp;·&nbsp; 🔧 {item["framework"]} &nbsp;·&nbsp; 🔤 {item["tokens"]:,} tokens</div>', unsafe_allow_html=True)
                st.markdown(f"**Prompt:** {item['prompt']}")
                st.divider()
                hct, het = st.tabs(["📋 Code","📖 Explanation"])
                with hct:
                    st.code(item["code"], language="python")
                    hc1, hc2, hc3 = st.columns(3)
                    hc1.download_button("⬇️ .py", data=item["code"], file_name=f"build_{bid}.py", mime="text/plain", key=f"dl_py_{bid}", use_container_width=True)
                    hc2.download_button("📦 .zip", data=make_zip(item["code"],item.get("setup",""),item["prompt"][:30]), file_name=f"build_{bid}.zip", mime="application/zip", key=f"dl_zip_{bid}", use_container_width=True)
                    if hc3.button("📥 Load as Active", key=f"load_h_{bid}", use_container_width=True):
                        st.session_state.active_code=item["code"]; st.session_state.active_explanation=item.get("explanation",""); st.session_state.active_setup=item.get("setup",""); st.success(f"✅ Build #{bid} loaded!")
                with het: st.markdown(item.get("explanation") or "_No explanation recorded._")
