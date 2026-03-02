import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import plotly.graph_objects as go
import re

# --- 1. Connection Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel Auditor", page_icon="🛡️", layout="wide")

# --- 2. Professional Light UI (No Black) ---
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; color: #333; }
    [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #eee; }
    
    .stTextArea textarea { 
        background-color: #ffffff !important; 
        color: #222 !important; 
        border: 1px solid #ddd !important;
        border-radius: 10px;
        font-size: 15px;
    }

    .stButton>button {
        background-color: #2ecc71 !important;
        color: white !important;
        border-radius: 8px;
        font-weight: bold;
        border: none;
        height: 3em;
    }

    .report-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border-top: 4px solid #2ecc71;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        color: #444;
        margin-top: 10px;
    }
    
    .source-badge {
        background: #e8f5e9;
        color: #2e7d32;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        border: 1px solid #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Better File Extractor (Supports Code & Docs) ---
def extract_all_files(file):
    try:
        if file.type == "application/pdf":
            return " ".join([p.extract_text() for p in PdfReader(file).pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return " ".join([p.text for p in Document(file).paragraphs])
        else:
            return file.getvalue().decode("utf-8")
    except Exception as e:
        return f"Error: {str(e)}"

# --- 4. Main UI ---
st.markdown("<h1 style='text-align:center; color:#2c3e50;'>🛡️ AI Content Auditor Pro</h1>", unsafe_allow_html=True)

col_in, col_out = st.columns([1.1, 1], gap="large")

with col_in:
    st.subheader("📥 Data Input")
    # Multiple file types supported
    uploaded_file = st.file_uploader("Upload Doc (PDF, DOCX, TXT, PY, JS):", type=["pdf", "docx", "txt", "py", "js", "html"])
    manual_text = st.text_area("Or Paste Content Here:", height=380, placeholder="Paste text or code for forensic scan...")
    
    input_text = extract_all_files(uploaded_file) if uploaded_file else manual_text
    analyze_btn = st.button("🚀 EXECUTE FORENSIC SCAN")

with col_out:
    st.subheader("📊 Audit Visualization")
    if analyze_btn and input_text:
        with st.spinner("Analyzing linguistic patterns..."):
            try:
                # Optimized Prompt for strict parsing
                prompt = (
                    "Act as a forensic AI expert. Analyze this content for AI signatures. "
                    "You MUST provide the output in this EXACT format:\n"
                    "SCORE_AI: [number]\nSCORE_HUMAN: [number]\nSOURCE: [ChatGPT/Gemini/Claude/Human/Llama]\n"
                    "EXPLANATION: [One solid technical paragraph in English summarizing the audit.]"
                )
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"{prompt}\n\nCONTENT:\n{input_text[:4000]}"}]
                )
                
                raw_res = response.choices[0].message.content
                
                # --- Parsing Logic (RegEx) ---
                ai_val = int(re.search(r"SCORE_AI:\s*(\d+)", raw_res).group(1)) if re.search(r"SCORE_AI:\s*(\d+)", raw_res) else 50
                hu_val = 100 - ai_val
                # Source detection fix
                src_match = re.search(r"SOURCE:\s*([\w\s/]+)", raw_res)
                source_name = src_match.group(1).strip() if src_match else "Undetermined"
                # Explanation fix
                exp_match = re.search(r"EXPLANATION:\s*(.*)", raw_res, re.DOTALL)
                report_text = exp_match.group(1).strip() if exp_match else "Analysis complete. No detailed report generated."

                # --- 📊 Donut Circle Graph ---
                fig = go.Figure(data=[go.Pie(
                    labels=['AI Patterns', 'Human Variance'], 
                    values=[ai_val, hu_val], 
                    hole=.6,
                    marker_colors=['#34495e', '#2ecc71'], # Dark Grey for AI, Green for Human
                    textinfo='percent+label',
                    pull=[0.05, 0] # Slightly pull the AI slice
                )])
                fig.update_layout(
                    showlegend=False, 
                    margin=dict(t=10, b=10, l=10, r=10),
                    paper_bgcolor='rgba(0,0,0,0)',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)

                # --- 📝 Forensic Report ---
                st.markdown(f"**Identified Source Fingerprint:** <span class='source-badge'>{source_name}</span>", unsafe_allow_html=True)
                st.markdown("### 📝 Forensic Audit Report")
                st.markdown(f"<div class='report-card'>{report_text}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Audit System Error: {str(e)}")
    else:
        st.info("System Ready. Provide input to begin forensic audit.")

st.write("---")
st.caption("AI Sentinel v4.5 | High-Precision Forensics | Groq Llama 3 Powered")
