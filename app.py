import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(
    page_title="AI Sentinel Pro",
    page_icon="🛡️",
    layout="centered"
)

# ---------- STYLE ----------
st.markdown("""
<style>

.stApp{
background:#f1f5f9;
}

.big-title{
text-align:center;
font-size:34px;
font-weight:700;
color:#1e3a8a;
}

.report{
background:white;
padding:25px;
border-radius:14px;
border-left:6px solid #2563eb;
box-shadow:0 10px 25px rgba(0,0,0,0.05);
}

</style>
""", unsafe_allow_html=True)

# ---------- FILE READER ----------
def read_file(file):

    name = file.name.lower()

    try:
        if name.endswith("pdf"):
            pdf = PdfReader(file)
            text = ""
            for p in pdf.pages:
                text += p.extract_text()
            return text

        elif name.endswith("docx"):
            doc = Document(file)
            return "\n".join(p.text for p in doc.paragraphs)

        elif name.endswith("csv"):
            df = pd.read_csv(file)
            return df.to_string()

        elif name.endswith("xlsx"):
            df = pd.read_excel(file)
            return df.to_string()

        else:
            return file.read().decode()

    except:
        return "Error reading file"


# ---------- BASIC STYLERY ----------
def analyze_style(text):

    sentences = re.split(r'[.!?]', text)
    words = text.split()

    avg_sentence = np.mean([len(s.split()) for s in sentences if s.strip() != ""])
    variance = np.var([len(s.split()) for s in sentences if s.strip() != ""])

    vocab = len(set(words))
    total = len(words)

    diversity = vocab / total if total else 0

    repetition = 1 - diversity

    return {
        "avg_sentence": avg_sentence,
        "variance": variance,
        "diversity": diversity,
        "repetition": repetition
    }


# ---------- UI ----------
st.markdown("<div class='big-title'>🛡️ AI Sentinel Pro Detector</div>", unsafe_allow_html=True)

st.write("")

text_input = st.text_area("Paste text or code", height=220)

file = st.file_uploader("or upload document")

content = ""

if file:
    content = read_file(file)
else:
    content = text_input

analyze = st.button("Run Deep Forensic Scan")


# ---------- ANALYSIS ----------
if analyze and content:

    with st.spinner("Running forensic analysis..."):

        style = analyze_style(content)

        prompt = f"""
You are an AI forensic investigator.

Determine probability text is AI generated.

Return EXACT format:

AI_PERCENT: number
HUMAN_PERCENT: number
ENGINE_GUESS: model name
CONFIDENCE: High Medium or Low
REPORT: explanation

TEXT:
{content[:3500]}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        res = response.choices[0].message.content

        ai = int(re.search(r"AI_PERCENT:\s*(\d+)", res).group(1))
        human = 100 - ai

        engine = re.search(r"ENGINE_GUESS:\s*(.*)", res).group(1)
        conf = re.search(r"CONFIDENCE:\s*(.*)", res).group(1)

        report = re.search(r"REPORT:\s*(.*)", res, re.S).group(1)

        # -------- DONUT CHART --------

        fig = go.Figure(data=[go.Pie(
            labels=["AI Probability", "Human Probability"],
            values=[ai, human],
            hole=.65
        )])

        fig.update_layout(height=320)

        st.plotly_chart(fig, use_container_width=True)

        # -------- BAR CHART --------

        fig2 = go.Figure()

        fig2.add_bar(
            x=["Sentence Variance", "Vocabulary Diversity", "Repetition"],
            y=[
                style["variance"],
                style["diversity"] * 100,
                style["repetition"] * 100
            ]
        )

        st.plotly_chart(fig2, use_container_width=True)

        # -------- RESULTS --------

        st.write("### Engine Guess")
        st.info(engine)

        st.write("Confidence:", conf)

        st.write("### Forensic Report")

        st.markdown(f"<div class='report'>{report}</div>", unsafe_allow_html=True)

elif analyze:
    st.warning("Provide content first")
