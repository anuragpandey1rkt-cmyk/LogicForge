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

# --- 3. ARCHITECT LOGIC ---
SYSTEM_LOGIC = """
[ROLE]
You are a Senior Streamlit Developer. You do not write simple scripts. 
You build "PWA-Style" Streamlit apps using Supabase for backend and Groq for AI.

[STRICT ARCHITECTURE RULES]
1. **Tech Stack**: Use `streamlit`, `supabase` (for auth/db), `groq` (for AI).
2. **AI Helper**: ALWAYS define a helper function `ask_ai(prompt)` that uses `groq_client.chat.completions.create`.
   - Model: `llama-3.3-70b-versatile`.
3. **Session State**: Initialize a dictionary in `st.session_state` for: 'user', 'xp', 'streak', 'feature' (navigation), and 'chat_history'.
4. **Navigation**: Do NOT use `st.sidebar.selectbox`. Use a Custom Navigation System:
   - Define a function `go_to(page)`.
   - In the sidebar, use `st.button("Page Name", on_click=go_to, args=("Page Name",))`.
   - In `main()`, use `if st.session_state.feature == "Page Name": render_page_function()`.
5. **Gamification**: User actions must trigger `add_xp(amount, label)`.
6. **PWA Style**: Always include `make_pwa_ready()` <meta> tags.
7. **Modular Functions**: Every feature must be in its own function.

[OUTPUT FORMAT]
- Provide the FULL Python code in one block.
- Include `st.secrets` error handling.
"""

# --- 4. HELPER: IMAGE ENCODER ---
def encode_image(uploaded_file):
    if uploaded_file is not None:
        return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    return None

# --- 5. APP INTERFACE ---
st.title("👁️ Groq Architect Pro (Vision)")

with st.sidebar:
    st.header("⚙️ Settings")
    if not api_key:
        api_key = st.text_input("Enter Groq API Key", type="password")
        if not api_key:
            st.warning("⚠️ Enter key to proceed")
    else:
        st.success("API Key Connected ✅")
    
    # ADDED VISION MODEL HERE
    model = st.selectbox("Select Model", [
        "llama-3.2-90b-vision-preview", # Best for images
        "llama-3.3-70b-versatile",      # Best for text-only logic
        "llama-3.2-11b-vision-preview"  # Faster vision
    ], index=0)
    
    st.info("Tip: Use 'Vision' models if you upload images.")

if not api_key:
    st.stop()

client = Groq(api_key=api_key)

tab_build, tab_debug = st.tabs(["🏗️ Build (Sketch-to-App)", "🔧 Debugger (Screen-Reader)"])

# === TAB 1: BUILDER ===
with tab_build:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_requirement = st.text_area("App Description:", height=150, placeholder="Describe the app OR upload a sketch/screenshot below...")
        # IMAGE UPLOAD FOR BUILDER
        uploaded_sketch = st.file_uploader("Upload UI Sketch or Screenshot (Optional)", type=["png", "jpg", "jpeg"])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        generate_btn = st.button("🚀 Build It", type="primary", use_container_width=True)

    if generate_btn and (user_requirement or uploaded_sketch):
        with st.spinner("Analyzing inputs and architecting code..."):
            try:
                messages = [{"role": "system", "content": SYSTEM_LOGIC}]
                
                user_content = []
                if user_requirement:
                    user_content.append({"type": "text", "text": f"Task: {user_requirement}\n\nStrictly follow the Architecture Rules."})
                
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
                
                generated_code = completion.choices[0].message.content
                
                # Clean up
                if generated_code.startswith("```python"):
                    generated_code = generated_code.split("```python")[1]
                if generated_code.endswith("```"):
                    generated_code = generated_code[:-3]
                
                st.success("✨ Code Generated!")
                st.code(generated_code, language='python')
                st.download_button("📥 Download .py", generated_code, "generated_app.py", "text/x-python")
                
            except Exception as e:
                st.error(f"Error: {e}")

# === TAB 2: DEBUGGER ===
with tab_debug:
    st.info("Upload a screenshot of your error or app issue, and I'll fix it.")

    if "debug_history" not in st.session_state:
        st.session_state.debug_history = []

    for msg in st.session_state.debug_history:
        role = msg["role"]
        # Handle showing images in history if needed, for now just text
        if role != "system":
            st.chat_message(role).write(msg.get("content", ""))

    # INPUTS
    col_text, col_img = st.columns([4, 1])
    with col_text:
        user_query = st.chat_input("Explain the error...")
    with col_img:
        # IMAGE UPLOAD FOR DEBUGGER
        debug_screenshot = st.file_uploader("Error Screenshot", type=["png", "jpg"], key="debug_img")

    if user_query or debug_screenshot:
        # Prepare message
        content_payload = []
        if user_query:
            content_payload.append({"type": "text", "text": user_query})
            st.chat_message("user").write(user_query)
        
        if debug_screenshot:
            img_b64 = encode_image(debug_screenshot)
            content_payload.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}
            })
            st.chat_message("user").image(debug_screenshot, caption="Uploaded Screenshot")

        # Call AI
        with st.chat_message("assistant"):
            with st.spinner("Looking at your error..."):
                try:
                    # Construct messages
                    # We only send the CURRENT interaction with image to save tokens/complexity
                    # or you can append to history if you manage the object structure carefully
                    messages_to_send = [
                        {"role": "system", "content": "You are an expert Python Debugger. Analyze the text and/or images provided. If an image shows a stack trace, fix the code. If it shows a UI bug, provide CSS/Streamlit fixes."},
                        {"role": "user", "content": content_payload}
                    ]
                    
                    debug_response = client.chat.completions.create(
                        model=model, # Must use a vision model
                        messages=messages_to_send,
                        temperature=0.3
                    )
                    reply = debug_response.choices[0].message.content
                    st.markdown(reply)
                    
                    # Add text interaction to history (skipping heavy images for simple history)
                    st.session_state.debug_history.append({"role": "user", "content": user_query if user_query else "[Uploaded Image]"})
                    st.session_state.debug_history.append({"role": "assistant", "content": reply})
                    
                except Exception as e:
                    st.error(f"Error: {e}")
