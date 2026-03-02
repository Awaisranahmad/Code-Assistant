import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import plotly.graph_objects as go
import re

# --- 1. Connection & Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Auditor Pro", page_icon="🛡️", layout="wide")

# --- 2. 60-30-10 UI Styling (Light & Dark Professional Mix) ---
st.markdown("""
    <style>
    /* 60% - Main Background (Dark Professional) */
    .stApp { background-color: #1a1c24; color: #ffffff; }
    
    /* 30% - Secondary Elements (Light Grey) */
    [data-testid="stSidebar"] { background-color: #2d303d !important; border-right: 1px solid #3d4150; }
    
    .stTextArea textarea { 
        background-color: #f0f2f6 !important; 
        color: #1a1c24 !important; 
        border-radius: 12px;
        font-size: 16px;
    }

    /* 10% - Accent Color (Emerald Green) */
    .stButton>button {
        background-color: #2ecc71 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: scale(1.02); background-color: #27ae60 !important; }

    .report-card {
        background: #2d303d;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #2ecc71;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Functions ---
def get_content(file):
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
    uploaded_file = st.file_uploader("Upload Document", type=["pdf", "docx", "txt"])
    st.write("---")
    st.info("Uses Llama-3.3 for Deep Linguistic Analysis.")

st.markdown("<h1 style='text-align:center;'>🔍 AI Content Sentinel</h1>", unsafe_allow_html=True)

# --- 5. Main Dashboard ---
col_in, col_out = st.columns([1.2, 1], gap="large")

with col_in:
    st.markdown("### ⌨️ Content Input")
    raw_text = st.text_area("Paste text or code:", height=400, placeholder="Start typing or upload a file...")
    input_data = get_content(uploaded_file) if uploaded_file else raw_text
    analyze_btn = st.button("RUN FORENSIC ANALYSIS")

with col_out:
    st.markdown("### 📊 Audit Visualization")
    if analyze_btn and input_data:
        with st.spinner("Calculating Probabilities..."):
            try:
                # Prompt for specific scores
                prompt = (
                    "Audit this text. Return: AI_SCORE: [0-100], HUMAN_SCORE: [0-100], SOURCE: [Name]. "
                    "Then one professional paragraph report in English."
                )
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"{prompt}\n\n{input_data[:3000]}"}]
                )
                
                res = response.choices[0].message.content
                
                # Extract Scores
                ai_val = int(re.search(r"AI_SCORE:\s*(\d+)", res).group(1)) if re.search(r"AI_SCORE:\s*(\d+)", res) else 50
                hu_val = 100 - ai_val
                source = re.search(r"SOURCE:\s*(\w+)", res).group(1) if re.search(r"SOURCE:\s*(\w+)", res) else "Unknown"

                # --- Circle (Donut) Chart ---
                # Dark for AI, Emerald Green for Human
                fig = go.Figure(data=[go.Pie(
                    labels=['AI Content', 'Human Content'], 
                    values=[ai_val, hu_val], 
                    hole=.6,
                    marker_colors=['#3d4150', '#2ecc71'],
                    textinfo='label+percent'
                )])
                fig.update_layout(
                    showlegend=False, 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=0, b=0, l=0, r=0),
                    font=dict(color="white")
                )
                st.plotly_chart(fig, use_container_width=True)

                # --- Results ---
                st.markdown(f"**Identified Source:** `{source}`")
                st.markdown("### 📝 Forensic Report")
                report_text = re.sub(r".*SOURCE:.*", "", res, flags=re.DOTALL).strip()
                st.markdown(f"<div class='report-card'>{report_text}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error: {e}")
    else:
        st.info("Awaiting input for analysis.")

st.write("---")
st.caption("AI Sentinel v3.5 | Modern Design | Groq Cloud")
