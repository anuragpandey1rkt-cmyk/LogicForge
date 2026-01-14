import streamlit as st
from groq import Groq

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

# --- 3. THE BRAIN (STRICT & COMPLETE LOGIC) ---
SYSTEM_LOGIC = """
[ROLE]
You are a Senior Python Developer. You DO NOT write pseudo-code or simple examples.
You write **Complete, Functional, and Production-Ready** Streamlit applications.

[STRICT ARCHITECTURE RULES]
1. **Completeness**: The code must run immediately without errors. Include ALL imports.
2. **Complexity**: 
   - If the user asks for a game (like Candy Crush), implement the ACTUAL game logic (grid, swapping, score), not just a placeholder.
   - If the user asks for a financial app, implement dataframes, charts, and calculations.
3. **Structure**:
   - Use `st.set_page_config` first.
   - Use `if __name__ == "__main__": main()` pattern.
   - Use `st.session_state` for all interactive variables.

[OUTPUT FORMAT - DO NOT DEVIATE]
You must provide the response in THREE distinct sections:

---
### SECTION 1: THE CODE
(Provide the FULL, LONG, WORKING Python code block. Do not cut it short.)

---
### SECTION 2: EXPLANATION
(Briefly explain the key functions and how the logic works.)

---
### SECTION 3: SETUP
(List exactly what to put in `requirements.txt`. Example: `streamlit`, `pandas`, `numpy`)
"""

# --- 4. APP INTERFACE ---
st.title("🚀 LogicForge: AI Architect (Text Edition)")
st.caption("Build. Chat. Debug. Document.")

with st.sidebar:
    st.header("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password")
    else:
        st.success("API Key Connected ✅")
    
    # SIMPLIFIED MODEL SELECTOR (Text Only - Stable)
    model = st.selectbox("Select Model", [
        "llama-3.3-70b-versatile",      # Best for Logic & Code
        "llama-3.1-8b-instant"          # Faster, for simple tasks
    ], index=0)

if not api_key:
    st.warning("⚠️ Enter Groq API Key to start.")
    st.stop()

client = Groq(api_key=api_key)

# --- TABS FOR WORKFLOW ---
tab_build, tab_chat, tab_docs = st.tabs(["🏗️ Build App", "💬 AI Chat & Fixer", "📄 Write Docs"])

# === TAB 1: BUILDER (Text Only) ===
with tab_build:
    st.markdown("### Describe your App Idea")
    user_requirement = st.text_area("Be specific for better results:", height=150, placeholder="E.g. Create a fully functional Tetris game with score tracking and restart button.")
    
    if st.button("🚀 Build Full Code", type="primary", use_container_width=True):
        if user_requirement:
            with st.spinner("Architecting complex solution (this may take a moment)..."):
                try:
                    messages = [
                        {"role": "system", "content": SYSTEM_LOGIC},
                        {"role": "user", "content": f"Task: {user_requirement}"}
                    ]
                    
                    # We use a high token limit to ensure the code doesn't get cut off
                    resp = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=8000
                    )
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
                    st.error(f"Error: {e}")
        else:
            st.warning("Please describe your app first.")

# === TAB 2: AI CHAT & FIXER ===
with tab_chat:
    st.markdown("### 💬 Chat with Senior Developer")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I'm ready to help you fix bugs or explain code."}
        ]

    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    if user_input := st.chat_input("Type your message or paste error..."):
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    messages = [{"role": "system", "content": "You are a helpful Senior Python Developer."}]
                    for m in st.session_state.chat_history:
                        messages.append({"role": m["role"], "content": m["content"]})

                    response = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=0.3
                    )
                    reply = response.choices[0].message.content
                    st.markdown(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    
                except Exception as e:
                    st.error(f"Error: {e}")

# === TAB 3: DOCS GENERATOR ===
with tab_docs:
    st.markdown("### 📝 Generate Documentation")
    
    app_name = st.text_input("App Name", placeholder="e.g. Candy Crush Clone")
    app_desc = st.text_area("Description", placeholder="What features does it have?", height=100)
    
    if st.button("📄 Generate README & Report"):
        if app_desc:
            with st.spinner("Writing Professional Docs..."):
                prompt = f"""
                Create a professional GitHub README.md for '{app_name}'.
                Description: {app_desc}
                Include: Features, Installation, Usage, and a Technical Report section.
                """
                
                res = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown(res.choices[0].message.content)
