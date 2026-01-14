import streamlit as st
from groq import Groq
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Groq Architect (Adaptive)",
    page_icon="🧠",
    layout="wide"
)

# --- 2. API KEY MANAGEMENT ---
api_key = None
try:
    api_key = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError):
    pass 

# --- 3. THE NEW "ADAPTIVE" BRAIN ---
SYSTEM_LOGIC = """
[ROLE]
You are an Expert Streamlit Developer. Your goal is to build the *perfect* app for the user's specific request.

[ADAPTIVE ARCHITECTURE RULES - READ CAREFULLY]
1. **Analyze the Request**: 
   - IF the user asks for a simple tool (e.g., "calculator", "CSV viewer", "basic dashboard"), build a **Standalone Streamlit App**. DO NOT use Supabase, Auth, or XP unless explicitly asked.
   - IF the user asks for a complex app (e.g., "user login", "save data", "study buddy", "tracker"), THEN use the **PWA Stack** (Supabase + Gamification).

2. **Technology Stack (Conditional)**:
   - **Simple Apps**: Use `streamlit`, `pandas`, `numpy`. Use `st.session_state` for temporary data.
   - **Complex Apps**: Use `streamlit`, `supabase` (for auth/db), `groq` (for AI features).

3. **Coding Standards (Always Apply)**:
   - Use `st.set_page_config` at the very top.
   - Use modular functions (e.g., `def calculate():`, `def show_graph():`).
   - Use `st.secrets` for API keys if external services are used.
   - Always include error handling (try/except blocks).

[OUTPUT FORMAT]
You must provide the response in THREE distinct sections:

---
### SECTION 1: THE CODE
(Provide the FULL Python code here. Ensure it runs immediately.)

---
### SECTION 2: EXPLANATION
(Briefly explain what the code does.)

---
### SECTION 3: SETUP INSTRUCTIONS
(Tell the user what libraries to install in `requirements.txt`. IF you used Supabase/API keys, tell them exactly what to put in `.streamlit/secrets.toml`. If not, just say "No secrets needed.")
"""

# --- 4. HELPER: IMAGE ENCODER ---
def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 5. APP INTERFACE ---
st.title("🧠 Groq Architect (Smart & Adaptive)")
st.markdown("Builds exactly what you ask for—simple scripts or complex PWAs.")

with st.sidebar:
    st.header("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password")
    else:
        st.success("API Key Connected ✅")
    
    # Model Selector
    model = st.selectbox("Select Model", [
        "llama-3.3-70b-versatile",      # Smartest (Text/Code)
        "llama-3.2-11b-vision-preview", # Vision (Images)
    ], index=0)

if not api_key:
    st.warning("⚠️ Enter key to proceed")
    st.stop()

client = Groq(api_key=api_key)

tab_build, tab_debug = st.tabs(["🏗️ Build App", "🔧 Debugger"])

# === TAB 1: BUILDER ===
with tab_build:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_requirement = st.text_area("App Description:", height=150, placeholder="E.g., 'Make a simple BMI calculator' OR 'Make a full study app with login'")
        uploaded_sketch = st.file_uploader("Upload UI Sketch (Optional)", type=["png", "jpg", "jpeg"])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Build It", type="primary", use_container_width=True)

    if generate_btn and (user_requirement or uploaded_sketch):
        with st.spinner("Analyzing complexity and architecting code..."):
            try:
                messages = [{"role": "system", "content": SYSTEM_LOGIC}]
                
                user_content = []
                if user_requirement:
                    user_content.append({"type": "text", "text": f"Task: {user_requirement}"})
                
                if uploaded_sketch:
                    base64_image = encode_image(uploaded_sketch)
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    })
                
                messages.append({"role": "user", "content": user_content})

                completion = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=7000
                )
                
                full_response = completion.choices[0].message.content
                
                # --- PARSE RESPONSE ---
                if "```python" in full_response:
                    parts = full_response.split("```python")
                    code_part = parts[1].split("```")[0]
                    # Everything after the code block is explanation
                    explanation_part = parts[1].split("```")[1]
                    
                    st.success("✨ Code Generated!")
                    st.code(code_part, language='python')
                    st.download_button("📥 Download .py", code_part, "generated_app.py", "text/x-python")
                    
                    st.markdown("---")
                    st.subheader("📚 Explanation & Setup")
                    st.markdown(explanation_part)
                else:
                    st.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {e}")

# === TAB 2: DEBUGGER ===
with tab_debug:
    st.info("Paste any error here, and I will fix it.")
    user_query = st.chat_input("Paste error message...")
    
    if user_query:
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.chat_message("assistant"):
            with st.spinner("Fixing..."):
                try:
                    debug_response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {"role": "system", "content": "You are a Python Debugger. Fix the code or explain the error concisely."},
                            {"role": "user", "content": user_query}
                        ]
                    )
                    st.write(debug_response.choices[0].message.content)
                except Exception as e:
                    st.error(f"Error: {e}")
