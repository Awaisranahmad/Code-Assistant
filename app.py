import streamlit as st
from groq import Groq
import io
from PyPDF2 import PdfReader
from docx import Document

# --- 1. Setup & Secrets ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel Pro", page_icon="🛡️", layout="wide")

# --- 2. Advanced CSS (Cyber Security Theme) ---
st.markdown("""
    <style>
    .stApp { background-color: #050a0f; color: #00ff41; }
    .stTextArea textarea { background-color: #0d1117 !important; color: #00ff41 !important; border: 1px solid #00ff41; font-family: 'Courier New', monospace; }
    .result-card { background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; margin-top: 20px; }
    .header { text-align: center; color: #00ff41; text-shadow: 0 0 10px #00ff41; font-size: 35px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='header'>🛡️ AI SENTINEL: CONTENT & CODE AUDITOR</h1>", unsafe_allow_html=True)

# --- 3. File Processing Functions ---
def extract_text(file):
    if file.type == "application/pdf":
        reader = PdfReader(file)
        return " ".join([page.extract_text() for page in reader.pages])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return " ".join([p.text for p in doc.paragraphs])
    else:
        return file.getvalue().decode("utf-8")

# --- 4. Sidebar Options ---
with st.sidebar:
    st.title("🔍 Audit Settings")
    scan_mode = st.radio("Scan Type:", ["🤖 AI Detector", "💻 Code Auditor", "📝 Content Refiner"])
    precision = st.select_slider("Detection Precision:", options=["Standard", "Deep Scan", "Extreme"])
    st.write("---")
    uploaded_file = st.file_uploader("Upload File (PDF, DOCX, TXT, PY, JS):", type=["pdf", "docx", "txt", "py", "js"])

# --- 5. Main UI ---
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📥 Input Content")
    manual_text = st.text_area("Paste text or code to audit:", height=400)
    
    input_data = ""
    if uploaded_file:
        input_data = extract_text(uploaded_file)
        st.success(f"File '{uploaded_file.name}' loaded successfully!")
    else:
        input_data = manual_text

    analyze_btn = st.button("🚀 RUN SECURITY AUDIT")

with col2:
    st.subheader("📊 Audit Report")
    if analyze_btn and input_data:
        with st.spinner("Scanning for AI patterns..."):
            try:
                # Optimized Prompt for AI Detection
                system_prompt = (
                    "You are a forensic linguistic expert and senior code auditor. "
                    "Analyze the provided input for AI patterns, structural markers, and machine-generated logic. "
                    "Provide a technical report in English including: "
                    "1. AI vs Human Probability Percentage. "
                    "2. Key indicators of machine generation. "
                    "3. Logic/Syntax score for code."
                )
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Mode: {scan_mode}\nPrecision: {precision}\n\nInput:\n{input_data[:4000]}"}
                    ]
                )
                
                report = response.choices[0].message.content
                st.markdown(f"<div class='result-card'>{report}</div>", unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Audit Failed: {str(e)}")
    else:
        st.info("Waiting for input to audit...")

# --- 6. Footer ---
st.write("---")
st.caption("AI Sentinel Engine v2.0 | Groq Cloud | Strictly Professional Audit")
