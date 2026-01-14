import streamlit as st
from groq import Groq
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Groq Architect Pro (Vision)",
    page_icon="👁️",
    layout="wide"
)

# --- 2. API KEY MANAGEMENT ---
api_key = None
try:
    api_key = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError):
    pass 

# --- 3. ARCHITECT LOGIC (THE BRAIN - UPDATED) ---
SYSTEM_LOGIC = """
[ROLE]
You are a Senior Streamlit Developer. You do not write simple scripts. 
You build "PWA-Style" Streamlit apps using Supabase for backend and Groq for AI.

[STRICT ARCHITECTURE RULES]
1. **Tech Stack**: Use `streamlit`, `supabase` (for auth/db), `groq` (for AI).
2. **AI Helper**: ALWAYS define a helper function `ask_ai(prompt)` that uses `groq_client.chat.completions.create`.
   - Model: `llama-3.3-70b-versatile`.
3. **Session State**: Initialize a dictionary in `st.session_state` for: 'user', 'xp', 'streak', 'feature' (navigation), and 'chat_history'.
4. **Navigation**: Use Custom Navigation (Buttons in Sidebar), NOT selectbox.
5. **Gamification**: User actions must trigger `add_xp(amount, label)`.
6. **PWA Style**: Always include `make_pwa_ready()` <meta> tags.

[OUTPUT FORMAT - STRICTLY FOLLOW THIS STRUCTURE]
You must provide the response in THREE distinct sections:

---
### SECTION 1: THE CODE
(Provide the FULL Python code here in a single block. Include `st.secrets` error handling.)

---
### SECTION 2: CODE EXPLANATION
(Explain how the code works. Bullet points describing the key functions like `render_home`, `render_quiz`, and the Auth logic.)

---
### SECTION 3: HOW TO CONNECT & SETUP
1. **Requirements**: List the libraries needed (e.g., `streamlit`, `groq`, `supabase`).
2. **Supabase Setup**: 
   - Provide the exact **SQL Table Creation Code** needed for this app.
   - Example: "Go to Supabase SQL Editor and run this: `create table user_stats (user_id uuid, xp int, ...);`"
3. **Secrets Setup**: Show exactly what to put in `.streamlit/secrets.toml`.
"""

# --- 4. HELPER: IMAGE ENCODER ---
def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 5. APP INTERFACE ---
st.title("👁️ Groq Architect Pro (Explained)")

with st.sidebar:
    st.header("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password")
    else:
        st.success("API Key Connected ✅")
    
    # UPDATED MODEL LIST (Active Models)
    model = st.selectbox("Select Model", [
        "llama-3.3-70b-versatile",      # BEST for coding (Text only)
        "llama-3.2-11b-vision-preview", # Use this for Vision/Images
        "llama-3.1-8b-instant"          # Fastest
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
        user_requirement = st.text_area("App Description:", height=150, placeholder="Describe the app OR upload a sketch...")
        uploaded_sketch = st.file_uploader("Upload UI Sketch (Optional)", type=["png", "jpg", "jpeg"])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Build It", type="primary", use_container_width=True)

    if generate_btn and (user_requirement or uploaded_sketch):
        with st.spinner("Architecting Code, Explanation, and Database Rules..."):
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
                
                # --- PARSE THE RESPONSE TO SEPARATE CODE FROM TEXT ---
                # We try to split by the code block to make the UI cleaner
                if "```python" in full_response:
                    parts = full_response.split("```python")
                    intro_text = parts[0]
                    code_part = parts[1].split("```")[0]
                    explanation_part = parts[1].split("```")[1]
                    
                    st.success("✨ Code Generated!")
                    st.code(code_part, language='python')
                    
                    st.download_button("📥 Download .py", code_part, "generated_app.py", "text/x-python")
                    
                    st.markdown("---")
                    st.subheader("📚 Explanation & Setup")
                    st.markdown(explanation_part)
                else:
                    # Fallback if AI didn't format perfectly
                    st.markdown(full_response)
                
            except Exception as e:
                st.error(f"Error: {e}")

# === TAB 2: DEBUGGER ===
with tab_debug:
    st.info("Upload a screenshot of your error or app issue, and I'll fix it.")
    # (Debugger code remains the same as previous step...)
    col_text, col_img = st.columns([4, 1])
    with col_text:
        user_query = st.chat_input("Explain the error...")
    with col_img:
        debug_screenshot = st.file_uploader("Error Screenshot", type=["png", "jpg"], key="debug_img")
        
    if user_query or debug_screenshot:
        # (Debugger logic same as previous...)
        pass
