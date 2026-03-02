import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import plotly.graph_objects as go
import re

# --- 1. Connection ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel: Final Audit", page_icon="🛡️", layout="centered")

# --- 2. Professional Modern Blue UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e3a8a; }
    .stTextArea textarea { border: 2px solid #cbd5e1 !important; border-radius: 12px; }
    [data-testid="stFileUploadDropzone"] { border: 2px dashed #3b82f6 !important; border-radius: 12px; background: white; }
    
    .stButton>button {
        background: #1e3a8a !important;
        color: white !important;
        font-weight: bold;
        border-radius: 10px;
        height: 3.5em;
        width: 100%;
    }

    .report-card {
        background: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #1e3a8a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        color: #334155;
        line-height: 1.6;
    }

    .status-msg {
        padding: 10px;
        border-radius: 8px;
        background-color: #dbeafe;
        color: #1e40af;
        margin-bottom: 15px;
        font-weight: bold;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Robust File Reader ---
def read_file(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return " ".join([p.text for p in Document(file).paragraphs])
        else:
            # Code files ya text files ke liye
            content = file.read()
            return content.decode("utf-8")
    except Exception as e:
        return f"File Error: {str(e)}"

# --- 4. Main UI Layout ---
st.markdown("<h1 style='text-align:center;'>🛡️ AI Sentinel Auditor</h1>", unsafe_allow_html=True)
st.write("---")

# Section 1: Paste Code
st.markdown("### ⌨️ Step 1: Paste Content")
manual_input = st.text_area("Paste text or code here", height=200, label_visibility="collapsed")

# Section 2: File Upload
st.markdown("### 📂 Step 2: Upload Document")
uploaded_file = st.file_uploader("Upload PDF, DOCX, PY, JS, TXT", type=["pdf", "docx", "txt", "py", "js"])

# Content Selection Logic
final_content = ""
if uploaded_file:
    final_content = read_file(uploaded_file)
    st.markdown(f"<div class='status-msg'>✅ File Detected: {uploaded_file.name}</div>", unsafe_allow_html=True)
else:
    final_content = manual_input
    if manual_input:
        st.markdown("<div class='status-msg'>📝 Using Pasted Content</div>", unsafe_allow_html=True)

st.write("---")
analyze_btn = st.button("🚀 RUN FORENSIC AUDIT")

# Section 3 & 4: Results
if analyze_btn and final_content:
    with st.spinner("AI is analyzing fingerprints..."):
        try:
            # Strict Prompting but Flexible Parsing
            prompt = (
                "Audit this text for AI content. You MUST include these markers in your response: "
                "AI_SCORE: [0-100], HUMAN_SCORE: [0-100], SOURCE: [Name]. "
                "Then provide a professional paragraph starting with the word 'REPORT:' "
                f"\n\nCONTENT:\n{final_content[:3500]}"
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            raw_res = response.choices[0].message.content

            # --- SMART EXTRACTION (Regex) ---
            ai_score = 50 # Default
            ai_match = re.search(r"AI_SCORE:\s*(\d+)", raw_res)
            if ai_match: ai_score = int(ai_match.group(1))
            
            hu_score = 100 - ai_score
            
            source_match = re.search(r"SOURCE:\s*(.*)", raw_res)
            source_name = source_match.group(1).split('\n')[0] if source_match else "Unknown"

            # Report nikalne ka naya tareeka (Ab khali nahi rahega)
            report_match = re.search(r"REPORT:\s*(.*)", raw_res, re.DOTALL)
            if report_match:
                report_body = report_match.group(1).strip()
            else:
                # Agar AI 'REPORT:' likhna bhool jaye to sara text le lo jo scores ke baad hai
                report_body = raw_res.split("SOURCE:")[-1].split("\n", 1)[-1].strip()

            # --- Visualization (Circle Chart) ---
            st.markdown("### 📊 Step 3: Audit Visualization")
            fig = go.Figure(data=[go.Pie(
                labels=['AI Detection', 'Human Logic'], 
                values=[ai_score, hu_score], 
                hole=.7,
                marker_colors=['#1e3a8a', '#60a5fa'], # Dark Blue & Sky Blue
                textinfo='percent'
            )])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # --- Final Report ---
            st.markdown(f"**Potential Source:** `{source_name}`")
            st.markdown("### 📝 Step 4: Forensic Audit Report")
            st.markdown(f"<div class='report-card'>{report_body}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Audit Error: {e}")
elif analyze_btn:
    st.warning("Please provide input data!")

st.write("---")
st.caption("AI Sentinel v6.5 | Blue Edition | Fix: Report Extraction")
