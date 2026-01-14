import streamlit as st
import openai

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Ultra-Accurate Code Generator",
    page_icon="💎",
    layout="wide"
)

# --- 2. YOUR SECRET "CHART" LOGIC ---
# This is the most important part. 
# Paste the text from your charts/Gemini chat inside the triple quotes below.
# This acts as the "Constitution" for the AI.
SYSTEM_LOGIC = """
[ROLE]
You are a Senior Streamlit Developer. You do not write simple scripts. 
You build "PWA-Style" Streamlit apps using Supabase for backend and Groq for AI.

[STRICT ARCHITECTURE RULES]
1. **Tech Stack**: Use `streamlit`, `supabase` (for auth/db), `groq` (for AI), and `graphviz` (if needed).
2. **AI Helper**: ALWAYS define a helper function `ask_ai(prompt)` that uses `groq_client.chat.completions.create` with model `llama-3.1-8b-instant`.
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

# --- 3. APP INTERFACE ---
st.markdown("""
    <style>
    .main-header {font-size: 3em; color: #4A90E2; text-align: center; margin-bottom: 0px;}
    .sub-header {font-size: 1.2em; color: #666; text-align: center; margin-bottom: 30px;}
    .stTextArea textarea {background-color: #f4f7f6; border-radius: 10px;}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="main-header">💎 Perfect Code Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by your Custom Chart Logic</div>', unsafe_allow_html=True)

# Sidebar for API Key
with st.sidebar:
    st.header("🔑 AI Settings")
    api_key = st.text_input("OpenAI API Key", type="password")
    model = st.selectbox("Select Model", ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"], index=0)
    st.info("This app uses your hidden 'Chart' logic to ensure code perfection.")

# Main Input
col1, col2 = st.columns([3, 1])

with col1:
    user_requirement = st.text_area("What app/program do you want to create?", height=200, placeholder="Describe the functionality here...")

with col2:
    st.write("###")
    st.write("###")
    generate_btn = st.button("🚀 Generate Perfect Code", type="primary", use_container_width=True)

# --- 4. GENERATION ENGINE ---
if generate_btn:
    if not api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        st.stop()
    
    if not user_requirement:
        st.warning("Please describe what you want to build.")
        st.stop()

    client = openai.OpenAI(api_key=api_key)

    with st.spinner("Consulting your Charts and drafting code..."):
        try:
            # We combine your Chart Logic (System) with the User Request
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_LOGIC},
                    {"role": "user", "content": f"Task: {user_requirement}\n\nStrictly follow the Chart Logic provided."}
                ],
                temperature=0.1  # Low temperature = strict adherence to your charts (High Accuracy)
            )
            
            generated_code = response.choices[0].message.content
            
            st.success("✨ Code generated successfully following your rules!")
            st.code(generated_code, language='python')
            
            # Option to download
            st.download_button(
                label="📥 Download Code",
                data=generated_code,
                file_name="generated_app.py",
                mime="text/x-python"
            )
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
