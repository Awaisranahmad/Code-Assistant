import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import re

# --- 1. Connection & Page Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel: Forensic Auditor", page_icon="🛡️", layout="wide")

# --- 2. Ultra-Modern UI Styling (Advanced CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&display=swap');
    
    .stApp { background-color: #050a0f; color: #00ff41; font-family: 'Space Mono', monospace; }
    
    /* Input Area Styling */
    .stTextArea textarea { 
        background-color: #0d1117 !important; 
        color: #00ff41 !important; 
        border: 1px solid #00ff41 !important;
        border-radius: 4px;
        box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
    }
    
    /* Neon Metric Cards */
    .metric-container {
        display: flex;
        justify-content: space-around;
        gap: 20px;
        margin-bottom: 25px;
    }
    .neon-card {
        flex: 1;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        border: 2px solid #00ff41;
        background: rgba(0, 255, 65, 0.05);
        box-shadow: 0 0 15px rgba(0, 255, 65, 0.3);
    }
    .neon-card h2 { font-size: 45px; margin: 10px 0; color: #fff; }
    
    /* Report & Source Box */
    .report-box {
        background: #111;
        padding: 25px;
        border-radius: 8px;
        border-left: 10px solid #00ff41;
        color: #ddd;
        font-size: 15px;
        line-height: 1.8;
    }
    .source-tag {
        display: inline-block;
        padding: 5px 15px;
        background: #00ff41;
        color: #000;
        font-weight: bold;
        border-radius: 20px;
        margin-bottom: 10px;
    }
    
    /* Sidebar Fix */
    [data-testid="stSidebar"] { background-color: #0a0f14 !important; border-right: 1px solid #00ff41; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Core Logic Functions ---
def get_content(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return " ".join([p.text for p in Document(file).paragraphs])
        return file.getvalue().decode("utf-8")
    except: return "Error: Unsupported File."

# --- 4. Sidebar Panel ---
with st.sidebar:
    st.markdown("<h2 style='color:#00ff41;'>🛡️ AUDIT CONTROL</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drop Files (PDF/DOCX/TXT):", type=["pdf", "docx", "txt", "py", "js"])
    precision = st.select_slider("Detection Depth:", options=["Fast", "Balanced", "Forensic"])
    st.markdown("---")
    if st.button("RESET SYSTEM"): st.rerun()

st.markdown("<h1 style='text-align:center; color:#00ff41; text-shadow: 0 0 20px #00ff41;'>SYSTEM AUDIT: AI CONTENT DETECTOR</h1>", unsafe_allow_html=True)

# --- 5. Workspace ---
col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.markdown("### 📥 DATA INPUT")
    raw_text = st.text_area("Input Console:", height=450, placeholder="SYSTEM WAITING FOR DATA...")
    final_data = get_content(uploaded_file) if uploaded_file else raw_text
    start_audit = st.button("EXECUTE FORENSIC SCAN", use_container_width=True)

with col_out:
    st.markdown("### 📊 AUDIT METRICS")
    if start_audit and final_data:
        with st.spinner("SCANNING LINGUISTIC FINGERPRINTS..."):
            try:
                # Advanced Prompt for Scores + Source + Report
                audit_prompt = (
                    "Audit this text for AI content. Return data in this STRICT format:\n"
                    "AI_PERCENT: [Value]\nHUMAN_PERCENT: [Value]\nLIKELY_SOURCE: [ChatGPT/Claude/Gemini/Human]\n"
                    "REPORT: [One professional paragraph describing technical markers, perplexity, and burstiness.]"
                )
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are a forensic AI detector specializing in linguistic variance."},
                              {"role": "user", "content": f"{audit_prompt}\n\nCONTENT:\n{final_data[:4000]}"}]
                )
                
                raw_res = response.choices[0].message.content
                
                # Parsing results using Regex
                ai_p = int(re.search(r"AI_PERCENT:\s*(\d+)", raw_res).group(1)) if re.search(r"AI_PERCENT:\s*(\d+)", raw_res) else 50
                hu_p = 100 - ai_p
                source = re.search(r"LIKELY_SOURCE:\s*(\w+)", raw_res).group(1) if re.search(r"LIKELY_SOURCE:\s*(\w+)", raw_res) else "Unknown"
                report = re.search(r"REPORT:\s*(.*)", raw_res, re.DOTALL).group(1) if re.search(r"REPORT:\s*(.*)", raw_res, re.DOTALL) else "No report generated."

                # --- Visual Graphs (Neon Cards) ---
                st.markdown(f"""
                <div class="metric-container">
                    <div class="neon-card">
                        <p style="color:#00ff41;">🤖 AI SCORE</p>
                        <h2>{ai_p}%</h2>
                    </div>
                    <div class="neon-card">
                        <p style="color:#fff;">🧑 HUMAN SCORE</p>
                        <h2>{hu_p}%</h2>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.write("**Analysis Confidence Level:**")
                st.progress(ai_p / 100)
                
                # --- Source & Forensic Report ---
                st.markdown(f"<span class='source-tag'>IDENTIFIED SOURCE: {source}</span>", unsafe_allow_html=True)
                st.markdown(f"<div class='report-box'>{report}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"SYSTEM FAILURE: {str(e)}")
    else:
        st.info("Awaiting input for forensic analysis...")

st.write("---")
st.caption("AI Sentinel v3.0 | Matrix Forensic Engine | Groq Powered")
