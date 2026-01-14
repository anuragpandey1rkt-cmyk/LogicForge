import streamlit as st
from groq import Groq

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Groq Code Architect & Debugger",
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

# --- 3. THE "ARCHITECT" LOGIC (For Building Apps) ---
SYSTEM_LOGIC = """
[ROLE]
You are a Senior Streamlit Developer. You do not write simple scripts. 
You build "PWA-Style" Streamlit apps using Supabase for backend and Groq (Llama 3) for AI.

[STRICT ARCHITECTURE RULES]
1. **Tech Stack**: Use `streamlit`, `supabase` (for auth/db), `groq` (for AI), and `graphviz` (if needed).
2. **AI Helper**: ALWAYS define a helper function `ask_ai(prompt)` that uses `groq_client.chat.completions.create`.
   - Model: `llama-3.3-70b-versatile`.
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
st.title("⚡ Groq Code Architect & Debugger")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password", help="Get it free at console.groq.com")
        if not api_key:
            st.warning("⚠️ Please enter a key to proceed")
    else:
        st.success("API Key Connected (Securely) ✅")
    
    model = st.selectbox("Select Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], index=0)
    st.info("Tip: Use '70b' for complex coding and debugging.")

if not api_key:
    st.stop()

client = Groq(api_key=api_key)

# --- 5. MAIN TABS ---
tab_build, tab_debug = st.tabs(["🏗️ Build App", "🔧 Debugger / Chat"])

# === TAB 1: BUILDER ===
with tab_build:
    st.markdown("### Describe the PWA you want to build")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_requirement = st.text_area("App Description:", height=150, placeholder="E.g., A Finance Tracker PWA that logs expenses to Supabase...")
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Build It Now", type="primary", use_container_width=True)

    if generate_btn and user_requirement:
        with st.spinner("Consulting the architecture charts and writing code..."):
            try:
                completion = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_LOGIC},
                        {"role": "user", "content": f"Task: {user_requirement}\n\nStrictly follow the Architecture Rules provided."}
                    ],
                    temperature=0.1,
                    max_tokens=7000
                )
                
                generated_code = completion.choices[0].message.content
                
                # Clean up
                if generated_code.startswith("```python"):
                    generated_code = generated_code.split("```python")[1]
                if generated_code.endswith("```"):
                    generated_code = generated_code[:-3]
                
                st.success("✨ Code Generated Successfully!")
                st.code(generated_code, language='python')
                
                st.download_button("📥 Download .py File", generated_code, "generated_app.py", "text/x-python")
                
            except Exception as e:
                st.error(f"Groq Error: {e}")

# === TAB 2: DEBUGGER / CHAT ===
with tab_debug:
    st.markdown("### 🔧 Chat with the Error Fixer")
    st.info("Paste your error message or broken code below. The AI will fix it.")

    # Initialize Chat History
    if "debug_history" not in st.session_state:
        st.session_state.debug_history = [
            {"role": "assistant", "content": "Hello! I am your Senior Developer. Paste any error or code snippet here, and I'll help you fix it."}
        ]

    # Display History
    for msg in st.session_state.debug_history:
        st.chat_message(msg["role"]).write(msg["content"])

    # User Input
    if user_query := st.chat_input("Paste error here..."):
        # Add to history
        st.session_state.debug_history.append({"role": "user", "content": user_query})
        st.chat_message("user").write(user_query)

        # AI Response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing error..."):
                try:
                    debug_response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are an expert Python/Streamlit Debugger. Your goal is to provide specific, fixable code solutions. If the user pastes an error, explain WHY it happened and providing the FIXED code block immediately."},
                            *st.session_state.debug_history
                        ],
                        temperature=0.3
                    )
                    reply = debug_response.choices[0].message.content
                    st.markdown(reply)
                    st.session_state.debug_history.append({"role": "assistant", "content": reply})
                except Exception as e:
                    st.error(f"Error: {e}")
