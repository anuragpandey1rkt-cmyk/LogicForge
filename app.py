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
    
    # Sidebar Model Selection
    model = st.selectbox("Select Model", [
        "llama-3.3-70b-versatile",      # Best Logic
        "llama-3.2-11b-vision-preview", # Best Vision
    ], index=0)

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
        uploaded_sketch = st.file_uploader("Upload UI Sketch (Optional)", type=["png", "jpg"], key="build_img")
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Build Code", type="primary", use_container_width=True)

    if generate_btn and (user_requirement or uploaded_sketch):
        with st.spinner("Architecting Solution..."):
            try:
                # --- AUTO-SWITCH LOGIC FOR VISION ---
                active_model = model
                if uploaded_sketch and "vision" not in model:
                    st.toast("⚠️ Switching to Vision Model...", icon="👁️")
                    active_model = "llama-3.2-11b-vision-preview"

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
                st.error(f"Error: {e}")

# === TAB 2: AI CHAT & FIXER (UPDATED) ===
with tab_chat:
    st.markdown("### 💬 Chat with Senior Developer")
    st.caption("Ask questions, explain concepts, or paste errors to fix.")

    # 1. Initialize Chat History
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I'm LogicForge AI. Need help debugging code or understanding a concept?"}
        ]

    # 2. Display History
    for msg in st.session_state.chat_history:
        st.chat_message(msg["role"]).write(msg["content"])

    # 3. Chat Input & Processing
    if user_input := st.chat_input("Type your message or paste error..."):
        # Add User Message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # Generate Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Construct Prompt History
                    # We add a System Prompt at the start to define behavior
                    messages = [
                        {"role": "system", "content": "You are a helpful Senior Python Developer. You can chat normally AND fix code. If the user sends an error, provide the fix. If they say hi, chat back."}
                    ]
                    # Append session history (excluding system msgs from previous turns if any)
                    for m in st.session_state.chat_history:
                        messages.append({"role": m["role"], "content": m["content"]})

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile", # Using the smart text model for chat
                        messages=messages,
                        temperature=0.3
                    )
                    reply = response.choices[0].message.content
                    st.markdown(reply)
                    
                    # Save Assistant Message
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    
                except Exception as e:
                    st.error(f"Error: {e}")

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
        else:
            st.warning("Please describe the app first.")
