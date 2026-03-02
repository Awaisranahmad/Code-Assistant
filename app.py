import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import plotly.graph_objects as go
import re

# --- 1. Connection & Page Config ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel: Professional Audit", page_icon="🛡️", layout="centered")

# --- 2. Professional 60-30-10 UI (Blue/White/Grey) ---
st.markdown("""
    <style>
    /* Main Background - Very Light Grey/White */
    .stApp { background-color: #f4f7f9; color: #1e3a8a; }
    
    /* Headers */
    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    /* Text Area - Modern White */
    .stTextArea textarea { 
        background-color: #ffffff !important; 
        color: #334155 !important; 
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px;
    }

    /* File Uploader Box */
    [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #3b82f6 !important;
        border-radius: 12px;
    }

    /* Buttons - Solid Professional Blue */
    .stButton>button {
        background-color: #1e3a8a !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3.5em;
        width: 100%;
        transition: 0.3s ease;
    }
    .stButton>button:hover { background-color: #3b82f6 !important; box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2); }

    /* Status Message */
    .status-msg {
        padding: 10px;
        border-radius: 8px;
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
        margin-top: 5px;
        font-weight: bold;
    }

    /* Report Card */
    .report-card {
        background: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-top: 5px solid #1e3a8a;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        color: #475569;
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
            return file.read().decode("utf-8")
    except Exception as e:
        return f"Error: {str(e)}"

# --- 4. App Layout ---
st.markdown("<h1 style='text-align:center;'>🛡️ AI Sentinel Auditor</h1>", unsafe_allow_html=True)
st.write("---")

# SECTION 1: Paste Code (Hamesha Nazar Ayega)
st.markdown("### ⌨️ Paste Your Content")
manual_input = st.text_area("Input Code or Text", height=200, placeholder="Paste your content here...", label_visibility="collapsed")

# SECTION 2: File Upload
st.markdown("### 📂 Upload Document")
uploaded_file = st.file_uploader("Upload PDF, DOCX, or Code files", type=["pdf", "docx", "txt", "py", "js"])

# Status Check Logic
final_content = ""
if uploaded_file:
    final_content = read_file(uploaded_file)
    st.markdown(f"<div class='status-msg'>✅ System using data from: {uploaded_file.name}</div>", unsafe_allow_html=True)
else:
    final_content = manual_input
    if manual_input:
        st.markdown("<div class='status-msg'>📝 System using pasted text.</div>", unsafe_allow_html=True)

st.write("---")
analyze_btn = st.button("🚀 RUN FORENSIC AUDIT")

# SECTION 3 & 4: Visualization & Report
if analyze_btn and final_content:
    with st.spinner("Analyzing linguistic fingerprints..."):
        try:
            # Deep Audit Prompt
            prompt = (
                "Audit this text. Return: AI_SCORE: [0-100], HUMAN_SCORE: [0-100], SOURCE: [Name]. "
                "Then one professional paragraph report in English."
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{prompt}\n\n{final_content[:4000]}"}]
            )
            
            res_text = response.choices[0].message.content
            
            # Parsing Data
            ai_p = int(re.search(r"AI_SCORE:\s*(\d+)", res_text).group(1)) if re.search(r"AI_SCORE:\s*(\d+)", res_text) else 50
            hu_p = 100 - ai_p
            src = re.search(r"SOURCE:\s*(.*)", res_text).group(1).split('\n')[0] if re.search(r"SOURCE:\s*(.*)", res_text) else "Undetermined"
            report = re.sub(r".*SOURCE:.*", "", res_text, flags=re.DOTALL).strip()

            # --- Visualization (The Donut Circle) ---
            st.markdown("### 📊 Audit Visualization")
            
            fig = go.Figure(data=[go.Pie(
                labels=['AI Detection', 'Human Variance'], 
                values=[ai_p, hu_p], 
                hole=.7,
                marker_colors=['#1e3a8a', '#60a5fa'], # Dark Blue for AI, Light Blue for Human
                textinfo='percent+label'
            )])
            fig.update_layout(margin=dict(t=20, b=20, l=10, r=10), height=350, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # --- Forensic Report ---
            st.markdown(f"**Potential Source Identity:** `{src}`")
            st.markdown("### 📝 Forensic Audit Report")
            st.markdown(f"<div class='report-card'>{report}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Audit Error: {e}")
elif analyze_btn:
    st.warning("Please provide input data!")

st.write("---")
st.caption("AI Sentinel v6.0 | Modern Blue Design | Powered by Groq Cloud")
