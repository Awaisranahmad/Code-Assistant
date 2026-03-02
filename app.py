import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import plotly.graph_objects as go
import re
import io

# --- 1. Connection ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel: Universal Auditor", page_icon="🛡️", layout="centered")

# --- 2. Professional Blue UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e3a8a; }
    .stTextArea textarea { border: 2px solid #cbd5e1 !important; border-radius: 12px; background: white; }
    [data-testid="stFileUploadDropzone"] { border: 2px dashed #3b82f6 !important; border-radius: 12px; background: white; }
    
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important; font-weight: bold; border-radius: 10px; height: 3.5em; width: 100%; border: none;
    }
    .report-card {
        background: #ffffff; padding: 25px; border-radius: 15px; border-left: 8px solid #1e3a8a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); color: #334155; line-height: 1.6;
    }
    .status-msg {
        padding: 12px; border-radius: 8px; background-color: #dbeafe; color: #1e40af;
        margin-bottom: 15px; font-weight: bold; text-align: center; border: 1px solid #bfdbfe;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Universal File Reader (Handles All Types) ---
def read_any_file(file):
    try:
        fname = file.name.lower()
        if fname.endswith('.pdf'):
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif fname.endswith('.docx'):
            return " ".join([p.text for p in Document(file).paragraphs])
        elif fname.endswith(('.csv', '.xlsx')):
            df = pd.read_csv(file) if fname.endswith('.csv') else pd.read_excel(file)
            return df.to_string()
        else:
            # Code, Text, Log, etc.
            return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"File System Error: {str(e)}"

# --- 4. Main UI ---
st.markdown("<h1 style='text-align:center;'>🛡️ Universal AI Auditor</h1>", unsafe_allow_html=True)
st.write("---")

# STEP 1: Paste Code
st.markdown("### ⌨️ Step 1: Paste Your Content")
manual_input = st.text_area("Paste text, code or logs here", height=200, label_visibility="collapsed")

# STEP 2: File Upload (All types)
st.markdown("### 📂 Step 2: Or Upload Any File")
uploaded_file = st.file_uploader("Upload PDF, DOCX, XLSX, CSV, PY, JS, TXT...", type=None) # type=None allows all

final_content = ""
if uploaded_file:
    final_content = read_any_file(uploaded_file)
    st.markdown(f"<div class='status-msg'>✅ Successfully Read: {uploaded_file.name}</div>", unsafe_allow_html=True)
else:
    final_content = manual_input
    if manual_input:
        st.markdown("<div class='status-msg'>📝 Using Pasted Content</div>", unsafe_allow_html=True)

st.write("---")
analyze_btn = st.button("🚀 EXECUTE MULTI-SOURCE AUDIT")

# STEP 3 & 4: Analysis
if analyze_btn and final_content:
    with st.spinner("Analyzing cross-platform AI signatures..."):
        try:
            # Better Prompting for Accuracy and Multiple Sources
            prompt = (
                "Perform a forensic audit on the provided content. Be realistic. "
                "If it's a mix, state it. Return EXACTLY in this format:\n"
                "AI_SCORE: [0-100]\nHUMAN_SCORE: [0-100]\nSOURCES: [List likely sources like ChatGPT, Human, Gemini, etc.]\n"
                "CONFIDENCE: [Low/Medium/High]\n"
                "REPORT: [A professional technical paragraph explaining markers like burstiness and perplexity.]"
                f"\n\nCONTENT:\n{final_content[:3800]}"
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            
            raw_res = response.choices[0].message.content

            # Extraction Logic
            ai_score = int(re.search(r"AI_SCORE:\s*(\d+)", raw_res).group(1)) if re.search(r"AI_SCORE:\s*(\d+)", raw_res) else 50
            hu_score = 100 - ai_score
            sources = re.search(r"SOURCES:\s*(.*)", raw_res).group(1).split('\n')[0] if re.search(r"SOURCES:\s*(.*)", raw_res) else "Unknown"
            confidence = re.search(r"CONFIDENCE:\s*(\w+)", raw_res).group(1) if re.search(r"CONFIDENCE:\s*(\w+)", raw_res) else "N/A"
            
            report_match = re.search(r"REPORT:\s*(.*)", raw_res, re.DOTALL)
            report_body = report_match.group(1).strip() if report_match else raw_res.split("SOURCES:")[-1].split("\n", 2)[-1].strip()

            # --- Visualization (Donut Chart) ---
            st.markdown("### 📊 Step 3: Audit Visualization")
            fig = go.Figure(data=[go.Pie(
                labels=['AI Signatures', 'Human Logic'], 
                values=[ai_score, hu_score], 
                hole=.7,
                marker_colors=['#1e3a8a', '#60a5fa'],
                textinfo='percent'
            )])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # --- Forensic Report ---
            st.markdown(f"**Potential Sources:** `{sources}`")
            st.markdown(f"**Audit Confidence:** `{confidence}`")
            st.markdown("### 📝 Step 4: Forensic Audit Report")
            st.markdown(f"<div class='report-card'>{report_body}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Audit System Failure: {e}")
elif analyze_btn:
    st.warning("No data found to audit!")

st.write("---")
st.caption("AI Sentinel v7.0 | Universal Multi-Source Auditor | Blue Edition")
