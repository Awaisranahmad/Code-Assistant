import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import plotly.graph_objects as go
import re

# --- 1. Connection ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel: Deep Forensic", page_icon="🛡️", layout="centered")

# --- 2. Professional Blue & White UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e3a8a; }
    .stTextArea textarea { border: 2px solid #cbd5e1 !important; border-radius: 12px; background: white; font-size: 16px; }
    [data-testid="stFileUploadDropzone"] { border: 2px dashed #3b82f6 !important; border-radius: 12px; background: white; }
    
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important; font-weight: bold; border-radius: 10px; height: 3.5em; width: 100%; border: none;
    }
    .report-card {
        background: #ffffff; padding: 25px; border-radius: 15px; border-left: 8px solid #1e3a8a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); color: #334155; line-height: 1.7;
    }
    .source-label {
        background: #e0f2fe; color: #0369a1; padding: 5px 15px; border-radius: 8px;
        font-weight: bold; border: 1px solid #bae6fd; display: inline-block; margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Universal File Reader ---
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
            return file.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return f"File Error: {str(e)}"

# --- 4. Main UI ---
st.markdown("<h1 style='text-align:center;'>🛡️ Deep AI Forensic Auditor</h1>", unsafe_allow_html=True)
st.write("---")

# STEP 1: Paste Code
st.markdown("### ⌨️ Step 1: Paste Your Content")
manual_input = st.text_area("Paste text or code here", height=200, label_visibility="collapsed")

# STEP 2: File Upload
st.markdown("### 📂 Step 2: Or Upload Any File")
uploaded_file = st.file_uploader("Upload Any Document", type=None)

final_content = ""
if uploaded_file:
    final_content = read_any_file(uploaded_file)
    st.info(f"📁 Loaded: {uploaded_file.name}")
else:
    final_content = manual_input

st.write("---")
analyze_btn = st.button("🚀 EXECUTE DEEP SCAN")

# STEP 3 & 4: Analysis
if analyze_btn and final_content:
    with st.spinner("Decoding AI Signatures (Identifying Engine Name)..."):
        try:
            # Aggressive Prompt for Name Detection
            prompt = (
                "You are a high-level Forensic AI Linguistic Expert. Analyze this content for specific AI signatures. "
                "Be bold and name the likely AI engine (e.g., GPT-4, GPT-3.5, Claude 3, Gemini, Llama 3). "
                "Format your response EXACTLY like this:\n"
                "AI_PERCENT: [0-100]\nHUMAN_PERCENT: [0-100]\nENGINE_NAME: [Specific AI Name or Mix of Names]\n"
                "CONFIDENCE_SCORE: [High/Medium/Low]\n"
                "FORENSIC_REPORT: [Professional paragraph explaining WHY you think it's that specific AI.]"
                f"\n\nCONTENT:\n{final_content[:3800]}"
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1 # Accuracy ke liye low temperature
            )
            
            raw_res = response.choices[0].message.content

            # Regex Extraction
            ai_p = int(re.search(r"AI_PERCENT:\s*(\d+)", raw_res).group(1)) if re.search(r"AI_PERCENT:\s*(\d+)", raw_res) else 0
            hu_p = 100 - ai_p
            engine = re.search(r"ENGINE_NAME:\s*(.*)", raw_res).group(1).split('\n')[0] if re.search(r"ENGINE_NAME:\s*(.*)", raw_res) else "Human Logic"
            conf = re.search(r"CONFIDENCE_SCORE:\s*(\w+)", raw_res).group(1) if re.search(r"CONFIDENCE_SCORE:\s*(\w+)", raw_res) else "Medium"
            
            report_match = re.search(r"FORENSIC_REPORT:\s*(.*)", raw_res, re.DOTALL)
            report_body = report_match.group(1).strip() if report_match else "Linguistic patterns fully analyzed."

            # --- Visualization (The Donut Circle) ---
            st.markdown("### 📊 Step 3: Audit Visualization")
            fig = go.Figure(data=[go.Pie(
                labels=['AI Detection', 'Human Logic'], 
                values=[ai_p, hu_p], 
                hole=.7,
                marker_colors=['#1e3a8a', '#60a5fa'],
                textinfo='percent'
            )])
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # --- Detailed Report ---
            st.markdown(f"<div class='source-label'>Detected Engine: {engine}</div>", unsafe_allow_html=True)
            st.write(f"**Confidence Level:** `{conf}`")
            
            st.markdown("### 📝 Step 4: Forensic Audit Report")
            st.markdown(f"<div class='report-card'>{report_body}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Audit System Failure: {e}")
elif analyze_btn:
    st.warning("Please provide content to audit.")

st.write("---")
st.caption("AI Sentinel v7.5 | Specific Engine Detection | Blue Edition")
