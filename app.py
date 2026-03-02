import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import re

# --- 1. Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel Pro", page_icon="🛡️", layout="wide")

# --- 2. Advanced UI Styling (Modern Dark Dashboard) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0b0e14; color: #e1e4e8; }
    
    /* Input Box styling */
    .stTextArea textarea { 
        background-color: #161b22 !important; 
        color: #58a6ff !important; 
        border: 1px solid #30363d !important;
        border-radius: 12px;
    }
    
    /* Report Card */
    .report-box {
        background: #1c2128;
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #238636;
        margin-top: 20px;
        line-height: 1.6;
        color: #adbac7;
    }
    
    .metric-card {
        background: #22272e;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #444c56;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Helper Functions ---
def extract_text(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return " ".join([p.text for p in Document(file).paragraphs])
        return file.getvalue().decode("utf-8")
    except: return ""

# --- 4. Main UI ---
st.markdown("<h1 style='text-align: center; color: #2ea043;'>🛡️ AI Sentinel Auditor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8b949e;'>Detect AI Patterns in Text & Code</p>", unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📥 Input Content")
    uploaded_file = st.file_uploader("Upload Document (PDF, DOCX, TXT):", type=["pdf", "docx", "txt", "py", "js"])
    manual_text = st.text_area("Or Paste Content Here:", height=350, placeholder="Paste text or code...")
    
    audit_btn = st.button("🚀 START SCANNING", use_container_width=True)

with col2:
    st.subheader("📊 Analysis Results")
    
    input_data = extract_text(uploaded_file) if uploaded_file else manual_text

    if audit_btn and input_data:
        with st.spinner("Analyzing linguistic structures..."):
            try:
                # Prompt for specific metrics
                prompt = (
                    "Analyze this content. Provide a JSON-like short summary first: "
                    "AI_PERCENT: [0-100], HUMAN_PERCENT: [0-100]. "
                    "Then provide a single professional paragraph auditing the content's origin, "
                    "logic, and authenticity. No Urdu. Pure Technical English."
                )
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are a forensic content analyst."},
                              {"role": "user", "content": f"{prompt}\n\nContent:\n{input_data[:3000]}"}]
                )
                
                res_text = response.choices[0].message.content
                
                # Simple logic to extract percentages for the graph
                # (Assuming AI returns something like AI_PERCENT: 70)
                ai_val = 50 # Default
                match = re.search(r"AI_PERCENT:\s*(\d+)", res_text)
                if match: ai_val = int(match.group(1))
                hu_val = 100 - ai_val

                # --- Visual Graphs ---
                m1, m2 = st.columns(2)
                with m1:
                    st.markdown(f"<div class='metric-card'><b>🤖 AI Probability</b><br><h2 style='color:#f85149;'>{ai_val}%</h2></div>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<div class='metric-card'><b>🧑 Human Probability</b><br><h2 style='color:#2ea043;'>{hu_val}%</h2></div>", unsafe_allow_html=True)
                
                st.write("---")
                st.write("**Detection Confidence:**")
                st.progress(ai_val / 100)
                
                # --- Final Report ---
                st.markdown("### 📝 Forensic Audit Report")
                # Cleaning the text for display
                clean_report = re.sub(r"AI_PERCENT:.*HUMAN_PERCENT:.*", "", res_text, flags=re.DOTALL).strip()
                st.markdown(f"<div class='report-box'>{clean_report}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Scan interrupted: {e}")
    else:
        st.info("System ready. Please provide input to start the audit.")

# --- 5. Footer ---
st.write("---")
st.caption("AI Sentinel v2.5 | Enterprise Grade Content Forensics")
