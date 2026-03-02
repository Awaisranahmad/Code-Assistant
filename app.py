import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re
import textstat

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="AI Sentinel Ultra", page_icon="🛡️", layout="wide")

# ---------------- UI STYLE ----------------
st.markdown("""
<style>

.stApp{
background:#f8fafc;
}

.title{
font-size:36px;
font-weight:700;
text-align:center;
color:#1e3a8a;
}

.card{
background:white;
padding:20px;
border-radius:14px;
box-shadow:0 10px 20px rgba(0,0,0,0.05);
margin-bottom:20px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- FILE READER ----------------
def read_file(file):

    name = file.name.lower()

    if name.endswith("pdf"):
        pdf = PdfReader(file)
        text = ""
        for p in pdf.pages:
            text += p.extract_text()
        return text

    if name.endswith("docx"):
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    if name.endswith("csv"):
        df = pd.read_csv(file)
        return df.to_string()

    if name.endswith("xlsx"):
        df = pd.read_excel(file)
        return df.to_string()

    return file.read().decode()


# ---------------- STYLE ANALYSIS ----------------
def style_metrics(text):

    sentences = re.split(r'[.!?]', text)
    words = text.split()

    sentence_lengths = [len(s.split()) for s in sentences if s]

    avg_sentence = np.mean(sentence_lengths)
    variance = np.var(sentence_lengths)

    vocab = len(set(words))
    total = len(words)

    diversity = vocab / total if total else 0

    readability = textstat.flesch_reading_ease(text)

    return {
        "avg_sentence": avg_sentence,
        "variance": variance,
        "diversity": diversity,
        "readability": readability
    }


# ---------------- SENTENCE SCAN ----------------
def sentence_scan(text):

    sentences = re.split(r'[.!?]', text)

    scores = []

    for s in sentences:
        length = len(s.split())

        if length > 25:
            scores.append(0.8)
        elif length > 15:
            scores.append(0.6)
        else:
            scores.append(0.3)

    return sentences, scores


# ---------------- HEADER ----------------
st.markdown("<div class='title'>🛡️ AI Sentinel Ultra</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    text_input = st.text_area("Paste text or code", height=250)

with col2:
    file = st.file_uploader("Upload document")

content = ""

if file:
    content = read_file(file)
else:
    content = text_input

run = st.button("Run Full Forensic Scan")

# ---------------- MAIN ANALYSIS ----------------
if run and content:

    with st.spinner("Analyzing linguistic signals..."):

        metrics = style_metrics(content)

        sentences, scores = sentence_scan(content)

        prompt = f"""
You are an AI forensic expert.

Estimate probability text is AI generated.

Return format:

AI_PERCENT:
ENGINE:
CONFIDENCE:
REPORT:

TEXT:
{content[:3500]}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        out = response.choices[0].message.content

        ai = int(re.search(r"AI_PERCENT:\s*(\d+)", out).group(1))
        human = 100 - ai

        engine = re.search(r"ENGINE:\s*(.*)", out).group(1)
        conf = re.search(r"CONFIDENCE:\s*(.*)", out).group(1)
        report = re.search(r"REPORT:\s*(.*)", out, re.S).group(1)

        # -------- CHART 1 --------

        st.subheader("AI Probability")

        fig = go.Figure(data=[go.Pie(
            labels=["AI", "Human"],
            values=[ai, human],
            hole=.65
        )])

        st.plotly_chart(fig, use_container_width=True)

        # -------- CHART 2 --------

        st.subheader("Writing Pattern Analysis")

        fig2 = go.Figure()

        fig2.add_bar(
            x=["Sentence Variance", "Vocabulary Diversity", "Readability"],
            y=[
                metrics["variance"],
                metrics["diversity"] * 100,
                metrics["readability"]
            ]
        )

        st.plotly_chart(fig2, use_container_width=True)

        # -------- SENTENCE LEVEL --------

        st.subheader("Suspicious Sentences")

        data = {
            "Sentence": sentences[:20],
            "AI Suspicion": scores[:20]
        }

        df = pd.DataFrame(data)

        st.dataframe(df)

        # -------- WORD STATS --------

        words = content.split()

        st.subheader("Text Statistics")

        c1, c2, c3 = st.columns(3)

        c1.metric("Words", len(words))
        c2.metric("Unique Words", len(set(words)))
        c3.metric("Avg Sentence", round(metrics["avg_sentence"], 2))

        # -------- ENGINE --------

        st.subheader("Model Guess")

        st.info(engine)

        st.write("Confidence:", conf)

        # -------- REPORT --------

        st.subheader("Forensic Report")

        st.markdown(f"<div class='card'>{report}</div>", unsafe_allow_html=True)

elif run:
    st.warning("Provide text or upload file")
