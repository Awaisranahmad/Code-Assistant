import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import plotly.graph_objects as go
import re

# --- 1. Connection Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Forensic Auditor", page_icon="🛡️", layout="wide")

# --- 2. 60-30-10 Clean UI (No Black, All Light & Professional) ---
st.markdown("""
    <style>
    /* Main Background - Clean White/Off-White */
    .stApp { 
        background-color: #f8f9fa; 
        color: #212529; 
    }
    
    /* Sidebar - Soft Grey */
    [data-testid="stSidebar"] { 
        background-color: #ffffff !important; 
        border-right: 1px solid #dee2e6; 
    }
    
    /* Input Area - Clean White with Shadow */
    .stTextArea textarea { 
        background-color: #ffffff !important; 
        color: #495057 !important; 
        border: 1px solid #ced4da !important;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Buttons - Emerald Green (Action Color) */
    .stButton>button {
        background-color: #2ecc71 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: 600;
        border: none;
        padding: 0.6rem 2rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover { 
        background-color: #27ae60 !important; 
        box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
    }

    /* Report Card - Light Grey with Green Border */
    .report-card {
        background: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-top: 5px solid #2ecc71;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        color: #495057;
    }
    
    h1, h2, h3 { color: #2c3e50; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Content Extractor ---
def extract_data(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return " ".join([p.text for p in Document(file).paragraphs])
        return file.getvalue().decode("utf-8")
    except: return ""

# --- 4. Sidebar ---
with st.sidebar:
    st.markdown("<h2 style='color:#2ecc71;'>🛡️ AUDIT PANEL</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload File (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
    st.markdown("---")
    st.write("Confidence: **Enterprise Grade**")

st.markdown("<h1 style='text-align:center;'>🔍 AI Content Sentinel</h1>", unsafe_allow_html=True)

# --- 5. Main Layout ---
col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.markdown("### 📥 Source Content")
    raw_text = st.text_area("Paste content to verify:", height=420, placeholder="Start typing or upload a document...")
    input_text = extract_data(uploaded_file) if uploaded_file else raw_text
    analyze_btn = st.button("RUN AUDIT SCAN")

with col_out:
    st.markdown("### 📊 Forensic Statistics")
    if analyze_btn and input_text:
        with st.spinner("Analyzing linguistic patterns..."):
            try:
                # Prompt for clean technical response
                prompt = (
                    "Analyze this content. Provide: AI_SCORE: [0-100], HUMAN_SCORE: [0-100]. "
                    "Mention LIKELY_SOURCE: [ChatGPT/Claude/Gemini/Human]. "
                    "Then write one professional paragraph in English about technical markers."
                )
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"{prompt}\n\nContent:\n{input_text[:3000]}"}]
                )
                
                res_body = response.choices[0].message.content
                
                # Regex for scores
                ai_val = int(re.search(r"AI_SCORE:\s*(\d+)", res_body).group(1)) if re.search(r"AI_SCORE:\s*(\d+)", res_body) else 50
                hu_val = 100 - ai_val
                src = re.search(r"LIKELY_SOURCE:\s*([\w\s]+)", res_body).group(1) if re.search(r"LIKELY_SOURCE:\s*([\w\s]+)", res_body) else "Unknown"

                # --- Circle (Donut) Chart ---
                # Dark Grey for AI, Emerald Green for Human
                fig = go.Figure(data=[go.Pie(
                    labels=['AI Content', 'Human Content'], 
                    values=[ai_val, hu_val], 
                    hole=.65,
                    marker_colors=['#495057', '#2ecc71'], # Dark Grey and Emerald Green
                    textinfo='percent',
                    hoverinfo='label'
                )])
                fig.update_layout(
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=30, b=0, l=0, r=0)
                )
                st.plotly_chart(fig, use_container_width=True)

                st.markdown(f"**Identified Fingerprint:** `{src}`")
                
                # --- Final Report ---
                st.markdown("### 📝 Analysis Report")
                final_report = re.sub(r"AI_SCORE:.*SOURCE:.*", "", res_body, flags=re.DOTALL).strip()
                st.markdown(f"<div class='report-card'>{final_report}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Audit Error: {e}")
    else:
        st.info("System ready. Input data to start forensic verification.")

st.write("---")
st.caption("AI Sentinel v4.0 | Light Modern Interface | Powered by Groq Llama 3")
