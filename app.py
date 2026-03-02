import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import plotly.graph_objects as go
import re

# --- 1. Connection Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel: Smart Auditor", page_icon="🛡️", layout="centered")

# --- 2. Modern Blue & White UI ---
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; color: #1e3a8a; }
    
    /* Input Area */
    .stTextArea textarea { 
        background-color: #ffffff !important; 
        color: #334155 !important; 
        border: 2px solid #e2e8f0 !important;
        border-radius: 12px;
    }

    /* Success Message for File */
    .file-success {
        padding: 20px;
        background-color: #e0f2fe;
        border: 2px solid #3b82f6;
        border-radius: 12px;
        color: #0369a1;
        text-align: center;
        margin-bottom: 20px;
        font-weight: bold;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        height: 3.5em;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3); }

    /* Report Card */
    .report-card {
        background: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border-left: 8px solid #1e3a8a;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        color: #475569;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Robust File Extractor ---
def extract_file_content(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return " ".join([p.text for p in Document(file).paragraphs])
        else:
            return file.read().decode("utf-8")
    except Exception as e:
        return f"Error: {str(e)}"

# --- 4. Main App Flow ---
st.markdown("<h1 style='text-align:center;'>🛡️ AI Sentinel Auditor</h1>", unsafe_allow_html=True)
st.write("---")

# STEP 1: File Upload (Ab ye decide karega ke niche kya dikhana hai)
st.markdown("### 📂 Step 1: Upload Your File")
uploaded_file = st.file_uploader("Drop PDF, DOCX, or Code files", type=["pdf", "docx", "txt", "py", "js"])

final_content = ""

# Logic: Agar file upload ho gayi to paste box nahi dikhana
if uploaded_file:
    final_content = extract_file_content(uploaded_file)
    st.markdown(f"""
        <div class="file-success">
            ✅ File Loaded: {uploaded_file.name} <br>
            <span style="font-weight:normal; font-size:0.9em;">(System is now using file content for audit)</span>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("### ⌨️ Step 1 (Alternative): Paste Your Content")
    manual_input = st.text_area("Input Code or Text", height=250, placeholder="Paste your data here...", label_visibility="collapsed")
    final_content = manual_input

st.write("---")
analyze_btn = st.button("🚀 EXECUTE FORENSIC AUDIT")

# STEP 2 & 3: Visualization & Report
if analyze_btn and final_content:
    with st.spinner("Analyzing linguistic signatures..."):
        try:
            prompt = (
                "Audit this text for AI content. Return exactly: "
                "AI_SCORE: [0-100], HUMAN_SCORE: [0-100], SOURCE: [Name]. "
                "Then one professional paragraph report in English."
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{prompt}\n\n{final_content[:4000]}"}]
            )
            
            raw_res = response.choices[0].message.content
            
            # Parsing
            ai_score = int(re.search(r"AI_SCORE:\s*(\d+)", raw_res).group(1)) if re.search(r"AI_SCORE:\s*(\d+)", raw_res) else 50
            hu_score = 100 - ai_score
            src = re.search(r"SOURCE:\s*(.*)", raw_res).group(1).split('\n')[0] if re.search(r"SOURCE:\s*(.*)", raw_res) else "Unknown"
            report_body = re.sub(r".*SOURCE:.*", "", raw_res, flags=re.DOTALL).strip()

            # --- Audit Visualization (Donut Chart) ---
            st.markdown("### 📊 Step 2: Audit Visualization")
            
            fig = go.Figure(data=[go.Pie(
                labels=['AI Detection', 'Human Logic'], 
                values=[ai_score, hu_score], 
                hole=.7,
                marker_colors=['#1e3a8a', '#60a5fa'],
                textinfo='percent'
            )])
            fig.update_layout(margin=dict(t=20, b=20, l=0, r=0), height=350, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)

            # --- Forensic Report ---
            st.markdown(f"**Potential Source Identity:** `{src}`")
            st.markdown("### 📝 Step 3: Forensic Audit Report")
            st.markdown(f"<div class='report-card'>{report_body}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Audit Error: {e}")
elif analyze_btn:
    st.warning("Please provide input data!")

st.write("---")
st.caption("AI Sentinel v5.5 | Smart UI Edition | Powered by Groq Cloud")
