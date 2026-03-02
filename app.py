import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import plotly.graph_objects as go
import re

# --- 1. Connection Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel: Blue Edition", page_icon="🛡️", layout="centered")

# --- 2. Modern Blue & White UI (The 60-30-10 Rule) ---
st.markdown("""
    <style>
    /* Main Background - Soft Off-White */
    .stApp { background-color: #f0f4f8; color: #1e3a8a; }
    
    /* Input Areas - Clean White with Blue Borders */
    .stTextArea textarea { 
        background-color: #ffffff !important; 
        color: #1e293b !important; 
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px;
    }
    .stTextArea textarea:focus { border-color: #3b82f6 !important; }

    /* File Uploader Styling */
    [data-testid="stFileUploadDropzone"] {
        background-color: #ffffff !important;
        border: 2px dashed #60a5fa !important;
        border-radius: 12px;
    }

    /* Buttons - Deep Blue to Sky Blue Gradient */
    .stButton>button {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        border-radius: 10px;
        font-weight: bold;
        border: none;
        height: 3.5em;
        width: 100%;
        transition: 0.3s;
    }
    .stButton>button:hover { opacity: 0.9; transform: translateY(-2px); }

    /* Report Card - Professional White/Blue Card */
    .report-card {
        background: #ffffff;
        padding: 30px;
        border-radius: 15px;
        border-top: 6px solid #1e3a8a;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        color: #334155;
    }

    h1, h2, h3 { color: #1e3a8a; font-family: 'Segoe UI', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Robust File Extractor ---
def extract_file_content(file):
    if file is None: return ""
    try:
        if file.type == "application/pdf":
            reader = PdfReader(file)
            return " ".join([p.extract_text() for p in reader.pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(file)
            return " ".join([p.text for p in doc.paragraphs])
        else:
            # For .py, .js, .txt, etc.
            return file.read().decode("utf-8")
    except Exception as e:
        return f"File Error: {str(e)}"

# --- 4. Main App Flow ---
st.markdown("<h1 style='text-align:center;'>🛡️ AI Sentinel Auditor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#64748b;'>Professional Forensic Analysis in Blue & White</p>", unsafe_allow_html=True)

# STEP 1: Code Paste (Uper)
st.markdown("### ⌨️ Step 1: Paste Your Content")
manual_input = st.text_area("Input Code or Text", height=250, placeholder="Paste your data here...", label_visibility="collapsed")

# STEP 2: File Upload (Neeche)
st.markdown("### 📂 Step 2: Or Upload a File")
uploaded_file = st.file_uploader("Drop PDF, DOCX, or Code files (.py, .js, .txt)", type=["pdf", "docx", "txt", "py", "js", "html"])

# Process input priority
final_content = ""
if uploaded_file:
    final_content = extract_file_content(uploaded_file)
    st.success(f"Successfully loaded: {uploaded_file.name}")
else:
    final_content = manual_input

st.write("---")
analyze_btn = st.button("🚀 EXECUTE FORENSIC AUDIT")

# STEP 3 & 4: Visualization & Report
if analyze_btn and final_content:
    with st.spinner("Analyzing Linguistic Signatures..."):
        try:
            # Strict Prompting
            prompt = (
                "Audit this text. Be precise. Return exactly in this format:\n"
                "AI_SCORE: [0-100]\nHUMAN_SCORE: [0-100]\nSOURCE: [ChatGPT/Gemini/Llama/Claude/Human]\n"
                "REPORT: [One solid technical paragraph in English summarizing the findings.]"
            )
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"{prompt}\n\nContent:\n{final_content[:4000]}"}]
            )
            
            raw_text = response.choices[0].message.content
            
            # Parsing Scores
            ai_score = int(re.search(r"AI_SCORE:\s*(\d+)", raw_text).group(1)) if re.search(r"AI_SCORE:\s*(\d+)", raw_text) else 50
            human_score = 100 - ai_score
            source_found = re.search(r"SOURCE:\s*(.*)", raw_text).group(1).split('\n')[0] if re.search(r"SOURCE:\s*(.*)", raw_text) else "Undetermined"
            final_report = re.search(r"REPORT:\s*(.*)", raw_text, re.DOTALL).group(1) if re.search(r"REPORT:\s*(.*)", raw_text, re.DOTALL) else "Analysis complete."

            # --- Audit Visualization (The Circle Graph) ---
            st.markdown("### 📊 Step 3: Audit Visualization")
            
            fig = go.Figure(data=[go.Pie(
                labels=['AI Detection', 'Human Logic'], 
                values=[ai_score, human_score], 
                hole=.7,
                marker_colors=['#1e3a8a', '#60a5fa'], # Dark Blue for AI, Light Blue for Human
                textinfo='percent'
            )])
            fig.update_layout(
                showlegend=True,
                margin=dict(t=20, b=20, l=0, r=0),
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation="h", xanchor="center", x=0.5, y=-0.1)
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- Audit Report (End) ---
            st.markdown(f"**Potential Source:** `{source_found}`")
            st.markdown("### 📝 Step 4: Forensic Report")
            st.markdown(f"<div class='report-card'>{final_report}</div>", unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Audit Error: {e}")
elif analyze_btn:
    st.warning("Please provide some text or a file first!")

st.write("---")
st.caption("AI Sentinel v5.0 | Blue Modern Edition | Powered by Groq Llama 3")
