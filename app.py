import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import InvalidArgument

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Gemini Code Architect",
    page_icon="💎",
    layout="wide"
)

# --- 2. SECURITY CHECK ---
# This looks for the key in your secrets file
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except FileNotFoundError:
    st.error("Secrets file not found. Please create a .streamlit/secrets.toml file.")
    st.stop()
except KeyError:
    st.error("Key 'GEMINI_API_KEY' not found in secrets.toml.")
    st.stop()

# Configure Gemini securely
genai.configure(api_key=api_key)

# --- 3. THE BRAIN (Your Architecture Logic) ---
SYSTEM_LOGIC = """
[ROLE]
You are a Senior Streamlit Developer. You do not write simple scripts. 
You build "PWA-Style" Streamlit apps using Supabase for backend and Google Gemini for AI.

[STRICT ARCHITECTURE RULES]
1. **Tech Stack**: Use `streamlit`, `supabase` (for auth/db), `google-generativeai` (for AI), and `graphviz` (if needed).
2. **AI Helper**: ALWAYS define a helper function `ask_ai(prompt)` that uses `model.generate_content(prompt)`.
   - Initialize model: `model = genai.GenerativeModel('gemini-1.5-flash')`
3. **Session State**: Initialize a dictionary in `st.session_state` for: 'user', 'xp', 'streak', 'feature' (navigation), and 'chat_history'.
4. **Navigation**: Do NOT use `st.sidebar.selectbox`. Use a Custom Navigation System:
   - Define a function `go_to(page)`.
   - In the sidebar, use `st.button("Page Name", on_click=go_to, args=("Page Name",))`.
   - In `main()`, use `if st.session_state.feature == "Page Name": render_page_function()`.
5. **Gamification**: Every user action (quiz, summary, chat) must trigger an `add_xp(amount, label)` function that updates Supabase.
6. **PWA Style**: Always include the `make_pwa_ready()` function with the specific `<meta>` tags to hide the footer and make it look like a mobile app.
7. **Modular Functions**: Every feature (e.g., Home, Quiz, Chat) must be in its own function (e.g., `render_home()`, `render_quiz()`).

[OUTPUT FORMAT]
- Provide the FULL Python code in one block.
- Include the `st.secrets` error handling block at the start.
- Ensure the `main()` function handles the routing logic.
"""

# --- 4. APP INTERFACE ---
st.title("💎 Gemini Code Architect")
st.markdown("Generates **perfect** apps based on your custom PWA architecture.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Status")
    st.success("API Key Connected ✅")
    st.info("Using Model: **gemini-1.5-flash**")

# Main Input
col1, col2 = st.columns([2, 1])

with col1:
    user_requirement = st.text_area("Describe the App you want to build:", height=200, placeholder="E.g., A Finance Tracker PWA that logs expenses to Supabase and uses AI to give budget advice...")

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Build It Now", type="primary", use_container_width=True)

# --- 5. GENERATION ENGINE ---
if generate_btn:
    if not user_requirement:
        st.warning("Please describe what you want to build.")
        st.stop()

    with st.spinner("Consulting the architecture charts and writing code..."):
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_LOGIC
            )

            response = model.generate_content(
                f"Task: {user_requirement}\n\nStrictly follow the Architecture Rules provided."
            )
            
            generated_code = response.text
            
            # Clean up markdown
            if generated_code.startswith("```python"):
                generated_code = generated_code.split("```python")[1]
            if generated_code.endswith("```"):
                generated_code = generated_code[:-3]
            
            st.success("✨ Code Generated Successfully!")
            st.code(generated_code, language='python')
            
            st.download_button(
                label="📥 Download .py File",
                data=generated_code,
                file_name="generated_app.py",
                mime="text/x-python"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
