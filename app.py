import streamlit as st
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Groq Code Architect",
    page_icon="⚡",
    layout="wide"
)

# --- 2. API KEY MANAGEMENT ---
# Try to get key from secrets, otherwise ask in sidebar
api_key = None
try:
    api_key = st.secrets["GROQ_API_KEY"]
except (FileNotFoundError, KeyError):
    pass # We will handle this in the sidebar

# --- 3. YOUR "CHART" LOGIC (The Brain) ---
# This ruleset forces the AI to build apps exactly like your "Study Buddy"
SYSTEM_LOGIC = """
[ROLE]
You are a Senior Streamlit Developer. You do not write simple scripts. 
You build "PWA-Style" Streamlit apps using Supabase for backend and Groq (Llama 3) for AI.

[STRICT ARCHITECTURE RULES]
1. **Tech Stack**: Use `streamlit`, `supabase` (for auth/db), `groq` (for AI), and `graphviz` (if needed).
2. **AI Helper**: ALWAYS define a helper function `ask_ai(prompt)` that uses `groq_client.chat.completions.create`.
   - Model: `llama-3.3-70b-versatile` (or `llama-3.1-8b-instant` for speed).
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
st.title("⚡ Groq Code Architect")
st.markdown("Generates **perfect** apps based on your custom PWA architecture using **Llama 3.3**.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # If key wasn't in secrets, show input box
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password", help="Get it free at console.groq.com")
        if not api_key:
            st.warning("⚠️ Please enter a key to proceed")
    else:
        st.success("API Key Connected (Securely) ✅")
    
    model = st.selectbox("Select Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], index=0)
    st.info("Tip: '70b' is smarter for writing code.")

# Main Input
col1, col2 = st.columns([2, 1])

with col1:
    user_requirement = st.text_area("Describe the App you want to build:", height=200, placeholder="E.g., A Finance Tracker PWA that logs expenses to Supabase and uses AI to give budget advice...")

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    generate_btn = st.button("🚀 Build It Now", type="primary", use_container_width=True)

# --- 5. GENERATION ENGINE ---
if generate_btn:
    if not api_key:
        st.error("Please provide an API Key (in Secrets or Sidebar).")
        st.stop()
        
    if not user_requirement:
        st.warning("Please describe what you want to build.")
        st.stop()

    client = Groq(api_key=api_key)

    with st.spinner("Consulting the architecture charts and writing code..."):
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_LOGIC},
                    {"role": "user", "content": f"Task: {user_requirement}\n\nStrictly follow the Architecture Rules provided."}
                ],
                temperature=0.1, # Low temp for precise code
                max_tokens=7000, 
                stream=False
            )
            
            generated_code = completion.choices[0].message.content
            
            # Clean up output
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
            st.error(f"Groq Error: {e}")
