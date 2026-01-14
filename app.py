import streamlit as st
from groq import Groq
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="LogicForge: AI Architect",
    page_icon="🚀",
    layout="wide"
)

# --- 2. API KEY MANAGEMENT ---
api_key = None
try:
    api_key = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError):
    pass 

# --- 3. THE BRAIN (ADAPTIVE LOGIC) ---
SYSTEM_LOGIC = """
[ROLE]
You are an Expert Streamlit Developer. Build the *perfect* app for the user's request.

[ADAPTIVE ARCHITECTURE RULES]
1. **Analyze Request**: 
   - Simple (calc, converter) -> Standalone Streamlit (No DB).
   - Complex (login, history, study buddy) -> PWA Stack (Supabase + Gamification).
2. **Stack**: Streamlit, Supabase (if needed), Groq (if AI needed).
3. **Standards**: Modular functions, Error handling, st.secrets.

[OUTPUT FORMAT]
---
### SECTION 1: THE CODE
(Full Python code block)
---
### SECTION 2: EXPLANATION
(Brief breakdown)
---
### SECTION 3: SETUP
(requirements.txt content & secrets.toml guide)
"""

# --- 4. HELPER: IMAGE ENCODER ---
def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 5. APP INTERFACE ---
st.title("🚀 LogicForge: The AI App Architect")
st.caption("Build. Chat. Debug. Document.")

with st.sidebar:
    st.header("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password")
    else:
        st.success("API Key Connected ✅")
    
    # --- UPDATED MODEL SELECTOR (FUTURE PROOF) ---
    model_option = st.selectbox("Select Model", [
        "llama-3.3-70b-versatile",      # Best Logic (Text Only)
        "llama-3.2-90b-vision-preview", # Try this Vision model first
        "llama-3.2-11b-vision-preview", # Backup Vision
        "Custom..."                     # Failsafe
    ], index=0)
    
    if model_option == "Custom...":
        model = st.text_input("Enter Model Name", value="llama-3.2-90b-vision-preview", help="Check console.groq.com/docs/models for latest IDs")
    else:
        model = model_option

if not api_key:
    st.warning("⚠️ Enter Groq API Key to start.")
    st.stop()

client = Groq(api_key=api_key)

# --- TABS FOR WORKFLOW ---
tab_build, tab_chat, tab_docs = st.tabs(["🏗️ Build App", "💬 AI Chat & Fixer", "📄 Write Docs"])

# === TAB 1: BUILDER ===
with tab_build:
    col1, col2 = st.columns([3, 1])
    with col1:
        user_requirement = st.text_area("App Idea:", height=150, placeholder="E.g. A Student Portal with Login and Grades")
        uploaded_sketch = st.file_uploader("Upload UI Sketch (Optional)", type=["png", "jpg", "jpeg"], key="build_img")
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Build Code", type="primary", use_container_width=True)

    if generate_btn and (user_requirement or uploaded_sketch):
        with st.spinner("Architecting Solution..."):
            try:
                # --- ROBUST AUTO-SWITCH LOGIC ---
                active_model = model
                
                # If image exists BUT current model is Text-Only (70b-versatile), force a switch
                if uploaded_sketch and "vision" not in active_model:
                    st.toast("⚠️ Auto-switching to Vision model...", icon="👁️")
                    # Default to the 90b vision model as it is more likely to be active
                    active_model = "llama-3.2-90b-vision-preview"

                messages = [{"role": "system", "content": SYSTEM_LOGIC}]
                content = []
                if user_requirement: content.append({"type": "text", "text": f"Task: {user_requirement}"})
                if uploaded_sketch:
                    img = encode_image(uploaded_sketch)
                    content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img}"}})
                
                messages.append({"role": "user", "content": content})
                
                resp = client.chat.completions.create(model=active_model, messages=messages, temperature=0.1, max_tokens=7000)
                full_res = resp.choices[0].message.content
                
                if "```python" in full_res:
                    parts = full_res.split("```python")
                    code = parts[1].split("```")[0]
                    explanation = parts[1].split("```")[1]
                    st.code(code, language='python')
                    st.markdown(explanation)
                else:
                    st.markdown(full_res)
            except Exception as e:
                st.error(f"Groq Error: {e}")
                if "decommissioned" in str(e).lower():
                    st.info("💡 Tip: Select 'Custom...' in the sidebar and enter a valid model name from the Groq Console.")

# === TAB 2: DEBUGGER ===
with tab_debug:
    st.info("Paste errors here. I'll fix them instantly.")
    err_input = st.chat_input("Paste error message...")
    if err_input:
        with st.chat_message("user"): st.write(err_input)
        with st.chat_message("assistant"):
            with st.spinner("Fixing..."):
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are a Python Debugger. Provide the FIXED code block only."},
                        {"role": "user", "content": err_input}
                    ]
                )
                st.markdown(res.choices[0].message.content)

# === TAB 3: DOCS GENERATOR ===
with tab_docs:
    st.markdown("### 📝 Generate README & Reports")
    
    app_name = st.text_input("App Name", placeholder="e.g. Study Buddy")
    app_desc = st.text_area("What does the app do?", placeholder="Briefly describe features...", height=100)
    
    if st.button("📄 Generate Documentation"):
        if app_desc:
            with st.spinner("Writing Documentation..."):
                prompt = f"""
                Create a professional GitHub README.md for an app named '{app_name}'.
                Description: {app_desc}
                Tech Stack: Python, Streamlit, Supabase, Groq AI.
                Include:
                1. Project Title & Emoji
                2. Key Features (Bullet points)
                3. Installation Guide (pip install...)
                4. How to Run (streamlit run app.py)
                5. A 'Project Report' section suitable for college submission.
                """
                
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(res.choices[0].message.content)
