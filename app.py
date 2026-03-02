import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
import textstat
import json
import xml.etree.ElementTree as ET

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(
    page_title="Universal AI Detector",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- FILE READER ----------------

def read_file(file):

    name = file.name.lower()

    try:

        # PDF
        if name.endswith(".pdf"):
            pdf = PdfReader(file)
            return " ".join(p.extract_text() or "" for p in pdf.pages)

        # DOCX
        elif name.endswith(".docx"):
            doc = Document(file)
            return "\n".join(p.text for p in doc.paragraphs)

        # CSV
        elif name.endswith(".csv"):
            df = pd.read_csv(file)
            return df.to_string()

        # Excel
        elif name.endswith(".xlsx"):
            df = pd.read_excel(file)
            return df.to_string()

        # JSON
        elif name.endswith(".json"):
            data = json.load(file)
            return json.dumps(data, indent=2)

        # XML
        elif name.endswith(".xml"):
            tree = ET.parse(file)
            root = tree.getroot()
            return ET.tostring(root, encoding="unicode")

        # Code / Text
        else:
            return file.read().decode(errors="ignore")

    except Exception as e:
        return str(e)


# ---------------- FILE TYPE DETECTION ----------------

def detect_type(filename):

    ext = filename.split(".")[-1]

    code_ext = ["py","js","cpp","java","c","php","go","ts","html","css"]

    if ext in code_ext:
        return "code"

    if ext in ["csv","xlsx","json","xml"]:
        return "data"

    return "document"


# ---------------- STYLE ANALYSIS ----------------

def style_metrics(text):

    sentences = re.split(r'[.!?]', text)
    words = text.split()

    sentence_lengths = [len(s.split()) for s in sentences if s]

    avg_sentence = np.mean(sentence_lengths) if sentence_lengths else 0
    variance = np.var(sentence_lengths) if sentence_lengths else 0

    vocab = len(set(words))
    total = len(words)

    diversity = vocab / total if total else 0

    readability = textstat.flesch_reading_ease(text) if len(text) > 50 else 0

    return avg_sentence, variance, diversity, readability


# ---------------- UI ----------------

st.title("🛡️ Universal AI Content Detector")

col1, col2 = st.columns(2)

with col1:
    text_input = st.text_area("Paste content")

with col2:
    file = st.file_uploader("Upload file")

content = ""
filetype = "text"

if file:
    content = read_file(file)
    filetype = detect_type(file.name)
else:
    content = text_input

run = st.button("Analyze")

# ---------------- ANALYSIS ----------------

if run and content:

    avg, var, div, read = style_metrics(content)

    prompt = f"""
You are an AI forensic investigator.

Detect if this content is AI generated.

Return format:

AI_PERCENT:
ENGINE:
CONFIDENCE:
REPORT:

CONTENT:
{content[:4000]}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    res = response.choices[0].message.content

    ai = int(re.search(r"AI_PERCENT:\s*(\d+)", res).group(1))
    human = 100 - ai

    engine = re.search(r"ENGINE:\s*(.*)", res).group(1)
    conf = re.search(r"CONFIDENCE:\s*(.*)", res).group(1)
    report = re.search(r"REPORT:\s*(.*)", res, re.S).group(1)

    # ---------------- CHART 1 ----------------

    fig = go.Figure(data=[go.Pie(
        labels=["AI","Human"],
        values=[ai,human],
        hole=.6
    )])

    st.plotly_chart(fig, use_container_width=True)

    # ---------------- CHART 2 ----------------

    fig2 = go.Figure()

    fig2.add_bar(
        x=["Sentence Variance","Vocabulary Diversity","Readability"],
        y=[var, div*100, read]
    )

    st.plotly_chart(fig2, use_container_width=True)

    # ---------------- FILE INFO ----------------

    st.subheader("File Information")

    st.write("Type:", filetype)
    st.write("Characters:", len(content))
    st.write("Words:", len(content.split()))

    # ---------------- ENGINE ----------------

    st.subheader("Possible AI Engine")

    st.info(engine)

    st.write("Confidence:", conf)

    # ---------------- REPORT ----------------

    st.subheader("Forensic Report")

    st.write(report)

elif run:
    st.warning("Add content or upload file")
