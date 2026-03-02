import streamlit as st
from groq import Groq

# --- 1. Global Configuration ---
st.set_page_config(page_title="CodeMaster Pro AI", page_icon="💻", layout="wide")

# Connection via Streamlit Secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 2. Advanced Professional UI (Dark Mode) ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    
    /* Customizing Text Area to look like an IDE */
    .stTextArea textarea { 
        font-family: 'Fira Code', 'Source Code Pro', monospace; 
        background-color: #161b22 !important; 
        color: #58a6ff !important; 
        border: 1px solid #30363d !important;
        border-radius: 8px;
    }
    
    /* Header Styling */
    .main-header { 
        text-align: center; 
        color: #238636; 
        font-size: 32px; 
        font-weight: 800;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background-color: #238636;
        color: white;
        border-radius: 6px;
        border: none;
        height: 3em;
        font-weight: bold;
    }
    .stButton>button:hover { background-color: #2ea043; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='main-header'>💻 AI CODE ANALYZER PRO</div>", unsafe_allow_html=True)

# --- 3. Sidebar Setup ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/606/606204.png", width=100)
    st.title("Dev Engine Settings")
    
    analysis_mode = st.selectbox("Select Task:", [
        "Debug & Fix", 
        "Code Explanation", 
        "Optimization",
        "Refactor Code",
        "Generate Documentation"
    ])
    
    lang = st.selectbox("Language:", ["Python", "JavaScript", "TypeScript", "C++", "Java", "Go", "SQL"])
    
    model_name = st.radio("Intelligence Level:", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"])
    
    if st.button("🗑️ Clear Workspace"):
        st.session_state.clear()
        st.rerun()

# --- 4. Main Interface (Editor & Console) ---
col1, col2 = st.columns([1, 1], gap="medium")

with col1:
    st.markdown("### ⌨️ Source Code")
    raw_code = st.text_area(
        label="Code Input",
        height=500,
        placeholder=f"// Paste your {lang} code here...",
        label_visibility="collapsed"
    )
    process_trigger = st.button("🚀 EXECUTE ANALYSIS")

with col2:
    st.markdown("### 🖥️ Output Console")
    if process_trigger and raw_code:
        with st.spinner("Analyzing codebase..."):
            try:
                # Optimized System Prompt (Strictly Technical)
                system_message = (
                    "You are an elite software engineer. Provide technical analysis, "
                    "refactored code, and architectural advice. Keep descriptions "
                    "concise and strictly in English. Use Markdown for all code blocks."
                )
                
                user_prompt = f"Task: {analysis_mode}\nLanguage: {lang}\n\nCode to process:\n{raw_code}"
                
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.2 # Lower temperature for better code accuracy
                )
                
                output_content = response.choices[0].message.content
                st.markdown(output_content)
                
            except Exception as e:
                st.error(f"Execution Error: {str(e)}")
    else:
        st.info("System ready. Input code to begin analysis.")

# --- 5. Footer ---
st.write("---")
st.caption("Engine: Groq Llama-3 | Environment: Streamlit Cloud | Status: Online")
