import streamlit as st
from groq import Groq
import json
import time
import re
import zipfile
import io
from datetime import datetime

# ─────────────────────────────────────────────
# 1. PAGE CONFIG  (must be FIRST st command)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="LogicForge AI Architect",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# 2. GLOBAL CSS — dark industrial theme
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@400;700;800&display=swap');

:root {
    --bg:       #0d0f14;
    --surface:  #141720;
    --border:   #252a38;
    --accent:   #f0c040;
    --accent2:  #3b82f6;
    --green:    #22c55e;
    --red:      #ef4444;
    --text:     #e2e8f0;
    --muted:    #64748b;
    --radius:   10px;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Syne', sans-serif;
    color: var(--text);
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

h1, h2, h3, h4 { font-family: 'Syne', sans-serif; font-weight: 800; }

.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: var(--surface);
    border-radius: var(--radius);
    padding: 4px;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: var(--muted);
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 13px;
    padding: 8px 18px;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: var(--accent) !important;
    color: #000 !important;
}

.stButton > button {
    background: var(--accent) !important;
    color: #000 !important;
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    border: none;
    border-radius: var(--radius);
    font-size: 14px;
    transition: opacity .15s;
}
.stButton > button:hover { opacity: .85; }

.stTextArea textarea, .stTextInput input, .stSelectbox select {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    font-family: 'JetBrains Mono', monospace !important;
    border-radius: var(--radius) !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px rgba(240,192,64,.2) !important;
}

.stCodeBlock, pre, code {
    font-family: 'JetBrains Mono', monospace !important;
    background: #0a0c10 !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 20px;
    text-align: center;
}
.stat-card .val { font-size: 28px; font-weight: 800; color: var(--accent); font-family: 'Syne', sans-serif; }
.stat-card .lbl { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }

.tag-badge {
    display: inline-block;
    background: rgba(59,130,246,.15);
    color: var(--accent2);
    border: 1px solid rgba(59,130,246,.3);
    border-radius: 20px;
    padding: 2px 10px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    margin: 2px;
}

.history-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius);
    padding: 12px 16px;
    margin-bottom: 8px;
    cursor: pointer;
}
.history-item:hover { border-color: var(--accent2); }

.chat-bubble-user {
    background: rgba(240,192,64,.1);
    border: 1px solid rgba(240,192,64,.2);
    border-radius: 12px 12px 2px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 14px;
}
.chat-bubble-ai {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 2px 12px 12px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    font-size: 14px;
}

div[data-testid="stMetricValue"] {
    color: var(--accent) !important;
    font-family: 'Syne', sans-serif !important;
}
div[data-testid="stMetricLabel"] { color: var(--muted) !important; }

.stAlert { border-radius: var(--radius) !important; }
.stSpinner > div { border-color: var(--accent) transparent transparent transparent !important; }

/* hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3. API KEY  (secrets → sidebar fallback)
# ─────────────────────────────────────────────
api_key = None
try:
    api_key = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError):
    pass

# ─────────────────────────────────────────────
# 4. SESSION STATE DEFAULTS
# ─────────────────────────────────────────────
defaults = {
    "chat_history": [{"role": "assistant", "content": "👋 Hey! I'm your Senior Python Dev. Paste code, errors, or ask anything."}],
    "build_history": [],         # list of {prompt, code, explanation, ts, model}
    "active_code": "",
    "active_explanation": "",
    "active_setup": "",
    "total_builds": 0,
    "total_tokens": 0,
    "chat_tokens": 0,
    "debug_result": "",
    "refactor_result": "",
    "test_result": "",
    "doc_result": "",
    "api_key_input": "",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# 5. SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚡ LogicForge")
    st.markdown("<small style='color:var(--muted)'>AI Code Architect</small>", unsafe_allow_html=True)
    st.divider()

    # API Key input if not in secrets
    if not api_key:
        st.markdown("**🔑 Groq API Key**")
        api_key_input = st.text_input("Paste key here", type="password", key="api_key_input", label_visibility="collapsed")
        if api_key_input:
            api_key = api_key_input
        if not api_key:
            st.warning("API key required to use the app.")

    st.markdown("**🤖 Model**")
    MODEL_OPTIONS = {
        "llama-3.3-70b-versatile":  "Llama 3.3 70B  — Best quality",
        "llama-3.1-8b-instant":     "Llama 3.1 8B   — Fastest",
        "mixtral-8x7b-32768":       "Mixtral 8×7B   — Long context",
        "gemma2-9b-it":             "Gemma 2 9B     — Balanced",
    }
    model = st.selectbox(
        "model", list(MODEL_OPTIONS.keys()),
        format_func=lambda x: MODEL_OPTIONS[x],
        index=0, label_visibility="collapsed"
    )

    st.markdown("**🌡️ Temperature**")
    temperature = st.slider("temp", 0.0, 1.0, 0.1, 0.05, label_visibility="collapsed")

    st.markdown("**📏 Max Tokens**")
    max_tokens = st.select_slider(
        "max_tok", options=[2000, 4000, 6000, 8000, 12000, 16000],
        value=8000, label_visibility="collapsed"
    )

    st.markdown("**🎨 Code Framework**")
    framework = st.selectbox(
        "fw", ["Streamlit", "FastAPI", "Flask", "Pure Python", "Django", "CLI Tool"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**📊 Session Stats**")
    c1, c2 = st.columns(2)
    c1.metric("Builds", st.session_state.total_builds)
    c2.metric("Tokens", f"{(st.session_state.total_tokens + st.session_state.chat_tokens):,}")

    st.divider()
    if st.button("🗑️ Clear All History", use_container_width=True):
        st.session_state.chat_history = [{"role": "assistant", "content": "Session cleared. How can I help?"}]
        st.session_state.build_history = []
        st.session_state.total_builds = 0
        st.session_state.total_tokens = 0
        st.session_state.chat_tokens = 0
        st.session_state.active_code = ""
        st.session_state.active_explanation = ""
        st.session_state.active_setup = ""
        st.rerun()

# ─────────────────────────────────────────────
# 6. HELPER: Groq client + call
# ─────────────────────────────────────────────
def get_client():
    if not api_key:
        st.error("⚠️ No API key. Add it in the sidebar.")
        st.stop()
    return Groq(api_key=api_key)

def groq_call(messages: list, max_tok: int = None, temp: float = None) -> tuple[str, int]:
    """Returns (content, tokens_used)."""
    client = get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temp if temp is not None else temperature,
        max_tokens=max_tok or max_tokens,
    )
    content = resp.choices[0].message.content
    tokens = resp.usage.total_tokens if resp.usage else 0
    return content, tokens

# ─────────────────────────────────────────────
# 7. HELPERS: parse + download
# ─────────────────────────────────────────────
def parse_response(full_res: str) -> tuple[str, str, str]:
    """Extract (code, explanation, setup) from model response."""
    code, explanation, setup = "", "", ""

    # Extract python code block
    match = re.search(r"```python(.*?)```", full_res, re.DOTALL)
    if match:
        code = match.group(1).strip()

    # Extract SECTION 2 (explanation)
    m2 = re.search(r"(?:SECTION 2|EXPLANATION)[:\s]+(.*?)(?=---|\Z|SECTION 3)", full_res, re.DOTALL | re.IGNORECASE)
    if m2:
        explanation = m2.group(1).strip()
    elif "```" in full_res and not m2:
        after_code = full_res.split("```")[-1]
        explanation = after_code.strip()

    # Extract SECTION 3 (setup/requirements)
    m3 = re.search(r"(?:SECTION 3|SETUP|requirements\.txt)[:\s]+(.*?)(?=\Z|---)", full_res, re.DOTALL | re.IGNORECASE)
    if m3:
        setup = m3.group(1).strip()

    return code, explanation, setup

def build_download_zip(code: str, setup_text: str, app_name: str = "app") -> bytes:
    """Package code + requirements into a .zip in memory."""
    buf = io.BytesIO()
    safe_name = re.sub(r"[^a-z0-9_]", "_", app_name.lower())[:40] or "app"
    # Extract requirements lines
    req_lines = []
    for line in setup_text.split("\n"):
        line = line.strip().lstrip("-*•").strip()
        if line and not line.startswith("#") and " " not in line:
            req_lines.append(line)
    req_text = "\n".join(req_lines) if req_lines else "streamlit\ngroq"

    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"{safe_name}.py", code)
        z.writestr("requirements.txt", req_text)
        z.writestr("README.md", f"# {app_name}\n\nGenerated by LogicForge AI Architect.\n\n## Run\n```bash\npip install -r requirements.txt\nstreamlit run {safe_name}.py\n```\n")
    return buf.getvalue()

# ─────────────────────────────────────────────
# 8. SYSTEM PROMPTS
# ─────────────────────────────────────────────
def build_system_prompt(fw: str) -> str:
    return f"""[ROLE]
You are a Senior Python Developer. You write COMPLETE, FUNCTIONAL, PRODUCTION-READY code using {fw}.

[STRICT RULES]
1. Completeness: Code runs immediately with zero errors. Include ALL imports.
2. Complexity: Implement ACTUAL logic — no stubs, no placeholders, no "TODO" comments.
3. Style: Clean code, docstrings, type hints, meaningful variable names.
4. For {fw}: follow all framework best practices and conventions.
5. Session state for all interactive variables (if applicable).

[OUTPUT FORMAT — DO NOT DEVIATE]
### SECTION 1: THE CODE
```python
<full working code here>
```

---
### SECTION 2: EXPLANATION
<explain key functions and architecture decisions>

---
### SECTION 3: SETUP
<list exact package names for requirements.txt, one per line>
"""

DEBUG_SYSTEM = """You are a Senior Python Developer specializing in debugging.
Given buggy code and/or an error traceback, you:
1. Identify ALL bugs (logical, runtime, syntax).
2. Return the COMPLETE fixed code in a ```python block.
3. List each fix with a brief explanation.
Format:
### Fixed Code
```python
<complete fixed code>
```
### What Was Fixed
- Bug 1: ...
- Bug 2: ...
"""

REFACTOR_SYSTEM = """You are a Senior Python Developer specializing in code quality.
Refactor the given code for:
- Readability (PEP 8, type hints, docstrings)
- Performance (remove redundancy, use efficient stdlib)
- Maintainability (single responsibility, DRY principle)
Return the FULL refactored code in a ```python block, then a brief changelog.
"""

TEST_SYSTEM = """You are a Senior Python Developer and QA engineer.
Write comprehensive pytest unit tests for the given code.
Cover: happy paths, edge cases, error handling, boundary values.
Use pytest fixtures where applicable. Return only a ```python code block.
"""

# ─────────────────────────────────────────────
# 9. HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div style='padding:24px 0 8px'>
  <span style='font-family:Syne,sans-serif;font-size:32px;font-weight:800;color:#f0c040'>⚡ LogicForge</span>
  <span style='font-family:JetBrains Mono,monospace;font-size:13px;color:#64748b;margin-left:12px'>AI Code Architect · v2.0</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 10. TABS
# ─────────────────────────────────────────────
tab_build, tab_debug, tab_refactor, tab_tests, tab_chat, tab_docs, tab_history = st.tabs([
    "🏗️ Builder",
    "🐛 Debugger",
    "♻️ Refactor",
    "🧪 Tests",
    "💬 Chat",
    "📄 Docs",
    "🕓 History",
])

# ══════════════════════════════════════════════
# TAB 1 — BUILDER
# ══════════════════════════════════════════════
with tab_build:
    st.markdown("### 🏗️ App Builder")
    st.caption(f"Framework: **{framework}** · Model: **{model}**")

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        user_req = st.text_area(
            "Describe your app in detail:",
            height=180,
            placeholder="E.g. A Streamlit dashboard that fetches live crypto prices, shows candlestick charts, and has a portfolio tracker with P&L calculations.",
        )

        extra_context = st.text_area(
            "Additional constraints / libraries (optional):",
            height=80,
            placeholder="E.g. Use plotly for charts. Must support dark mode. Include caching.",
        )

        with st.expander("⚙️ Advanced Options"):
            include_tests = st.checkbox("Also generate unit tests", value=False)
            include_readme = st.checkbox("Also generate README", value=True)
            streaming_mode = st.checkbox("Stream output (progressive display)", value=True)

        build_btn = st.button("⚡ Generate Full Code", type="primary", use_container_width=True)

    with col_right:
        if st.session_state.active_code:
            st.markdown("**📋 Active Code**")
            tab_code, tab_exp, tab_setup = st.tabs(["Code", "Explanation", "Setup"])
            with tab_code:
                st.code(st.session_state.active_code, language="python")
                zip_bytes = build_download_zip(
                    st.session_state.active_code,
                    st.session_state.active_setup,
                    user_req[:40] if user_req else "app"
                )
                st.download_button(
                    "⬇️ Download .zip (code + requirements)",
                    data=zip_bytes,
                    file_name="logicforge_app.zip",
                    mime="application/zip",
                    use_container_width=True,
                )
                st.download_button(
                    "⬇️ Download .py only",
                    data=st.session_state.active_code,
                    file_name="app.py",
                    mime="text/plain",
                    use_container_width=True,
                )
            with tab_exp:
                st.markdown(st.session_state.active_explanation or "_No explanation extracted._")
            with tab_setup:
                st.markdown(st.session_state.active_setup or "_No setup info extracted._")
        else:
            st.info("Your generated code will appear here.")

    # ── Build action ──
    if build_btn:
        if not user_req.strip():
            st.warning("Please describe your app first.")
        else:
            full_prompt = f"Framework: {framework}\nTask: {user_req}"
            if extra_context.strip():
                full_prompt += f"\nAdditional constraints: {extra_context}"

            messages = [
                {"role": "system", "content": build_system_prompt(framework)},
                {"role": "user", "content": full_prompt},
            ]

            with st.spinner("⚡ Architecting your app…"):
                try:
                    full_res, tokens = groq_call(messages)
                    code, explanation, setup = parse_response(full_res)

                    st.session_state.active_code = code or full_res
                    st.session_state.active_explanation = explanation
                    st.session_state.active_setup = setup
                    st.session_state.total_builds += 1
                    st.session_state.total_tokens += tokens

                    # Save to history
                    st.session_state.build_history.append({
                        "prompt": user_req[:120],
                        "code": code or full_res,
                        "explanation": explanation,
                        "setup": setup,
                        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "model": model,
                        "tokens": tokens,
                        "framework": framework,
                    })

                    # Optionally generate tests
                    if include_tests and code:
                        test_msgs = [
                            {"role": "system", "content": TEST_SYSTEM},
                            {"role": "user", "content": f"Write tests for:\n```python\n{code}\n```"},
                        ]
                        test_res, _ = groq_call(test_msgs, max_tok=3000)
                        st.session_state.test_result = test_res

                    st.success(f"✅ Built! {tokens:,} tokens used.")
                    st.rerun()

                except Exception as e:
                    st.error(f"Build failed: {e}")

# ══════════════════════════════════════════════
# TAB 2 — DEBUGGER
# ══════════════════════════════════════════════
with tab_debug:
    st.markdown("### 🐛 Bug Fixer & Error Analyser")

    d_col1, d_col2 = st.columns([1, 1], gap="large")

    with d_col1:
        buggy_code = st.text_area("Paste your buggy code:", height=250, placeholder="Paste Python code here…")
        error_msg  = st.text_area("Paste the error / traceback (optional):", height=100,
                                  placeholder="Traceback (most recent call last):\n  ...")
        if st.button("🔍 Fix My Code", type="primary", use_container_width=True):
            if buggy_code.strip():
                content = f"Buggy code:\n```python\n{buggy_code}\n```"
                if error_msg.strip():
                    content += f"\n\nError traceback:\n```\n{error_msg}\n```"
                with st.spinner("Analysing bugs…"):
                    try:
                        res, tok = groq_call(
                            [{"role": "system", "content": DEBUG_SYSTEM}, {"role": "user", "content": content}],
                            temp=0.05
                        )
                        st.session_state.debug_result = res
                        st.session_state.total_tokens += tok
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            else:
                st.warning("Paste some code first.")

    with d_col2:
        if st.session_state.debug_result:
            fixed_code, fix_exp, _ = parse_response(st.session_state.debug_result)
            if fixed_code:
                st.success("✅ Fixed code:")
                st.code(fixed_code, language="python")
