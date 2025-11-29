import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import PyPDF2
from wordcloud import WordCloud
from fpdf import FPDF
import matplotlib.pyplot as plt

# -----------------------------
# Load API key
# -----------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Tesseract Path (OCR)
# -----------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------
# Helper Functions
# -----------------------------
def extract_json_from_text(text):
    try:
        return json.loads(text)
    except:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except:
            pass
    return None

def ocr_image(img_file):
    try:
        img = Image.open(img_file)
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        return f"ERROR: {e}"

def ocr_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        if not text.strip():
            images = convert_from_bytes(pdf_file.read())
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        return text.strip()
    except Exception as e:
        return f"ERROR: {e}"

# -----------------------------
# Streamlit App Config
# -----------------------------
st.set_page_config(page_title="AI Essay Checker + Scanner", page_icon="📘", layout="wide")

st.markdown("""
<style>
.main-title { font-size:42px; font-weight:700; color:#003366; text-align:center; margin-bottom:-10px;}
.subtitle { font-size:20px; color:#444; text-align:center; margin-bottom:30px;}
.score-box { padding:15px; border-radius:10px; background:#eef2ff; text-align:center; font-size:22px; font-weight:600; margin:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📘 AI Essay Evaluation System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grammar • Spelling • Vocabulary • Coherence • Structure</div>', unsafe_allow_html=True)
st.write("___")

# -----------------------------
# Input Mode Selection
# -----------------------------
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📷 Upload Image", "📑 Upload PDF / Scan"])

essay_text = ""

# Paste Text
if mode == "📄 Paste Text":
    st.subheader("📝 Enter Your Essay")
    essay_text = st.text_area("Paste or type your essay below:", height=250)

# Upload Image / Camera
elif mode == "📷 Upload Image":
    st.subheader("📷 Upload or Take a Photo of Your Essay")
    uploaded_image = st.file_uploader("Upload image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])
    camera_image = st.camera_input("Or take a photo")
    img_source = uploaded_image if uploaded_image else camera_image
    if img_source:
        with st.spinner("Extracting text from image..."):
            essay_text = ocr_image(img_source)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

# Upload PDF
else:
    st.subheader("📑 Upload PDF / Scanned Essay")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            essay_text = ocr_pdf(uploaded_pdf)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

# -----------------------------
# Evaluate Button
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text.strip():
        st.error("Please provide essay text via paste, image, or PDF.")
    else:
        with st.spinner("Analyzing essay with AI..."):
            prompt = f"""
            You are a professional essay evaluator.

            Evaluate the following essay for:
            - Grammar
            - Spelling
            - Vocabulary
            - Coherence
            - Structure

            Output ONLY JSON:
            {{
                "grammar": 1-10,
                "vocabulary": 1-10,
                "coherence": 1-10,
                "structure": 1-10,
                "corrected_essay": "corrected essay version",
                "explanations": "sentence-by-sentence explanation"
            }}

            Essay:
            {essay_text}
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content":prompt}]
            )

            raw = response.choices[0].message.content
            data = extract_json_from_text(raw)

            if data is None:
                st.error("⚠️ Unexpected AI output. Showing raw response.")
                st.write(raw)
            else:
                # --- Evaluation Scores ---
                st.subheader("📊 Evaluation Scores")
                col1, col2, col3, col4 = st.columns(4)
                col1.markdown(f"<div class='score-box'>Grammar<br>{data['grammar']}/10</div>", unsafe_allow_html=True)
                col2.markdown(f"<div class='score-box'>Vocabulary<br>{data['vocabulary']}/10</div>", unsafe_allow_html=True)
                col3.markdown(f"<div class='score-box'>Coherence<br>{data['coherence']}/10</div>", unsafe_allow_html=True)
                col4.markdown(f"<div class='score-box'>Structure<br>{data['structure']}/10</div>", unsafe_allow_html=True)

                st.write("---")

                # --- Corrected Essay ---
                st.subheader("✔ Corrected Essay")
                st.write(data["corrected_essay"])

                st.write("---")

                # --- Teaching Mode ---
                st.subheader("📘 Teaching Mode – Explanation")
                st.write(data["explanations"])

                # --- Overall Score ---
                try:
                    scores = [int(data['grammar']), int(data['vocabulary']),
                              int(data['coherence']), int(data['structure'])]
                    overall = sum(scores)/len(scores)
                except:
                    overall = "N/A"
                st.subheader("🏆 Overall Score")
                st.metric("Overall Score (out of 10)", overall)

                # --- Word Cloud ---
                st.subheader("☁️ Essay Word Cloud")
                wordcloud = WordCloud(width=800, height=400, background_color='white').generate(essay_text)
                fig, ax = plt.subplots(figsize=(10,5))
                ax.imshow(wordcloud, interpolation='bilinear')
                ax.axis("off")
                st.pyplot(fig)

                # --- PDF Download ---
                st.subheader("📄 Download Corrected Essay & Scores as PDF")
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", "B", 16)
                pdf.cell(0, 10, "AI Essay Evaluation Report", ln=True, align="C")
                pdf.ln(10)
                pdf.set_font("Arial", "", 12)
                pdf.multi_cell(0, 8, f"Original Essay:\n{essay_text}\n")
                pdf.multi_cell(0, 8, f"Corrected Essay:\n{data['corrected_essay']}\n")
                pdf.multi_cell(0, 8, f"Scores:\nGrammar: {data['grammar']}/10\nVocabulary: {data['vocabulary']}/10\nCoherence: {data['coherence']}/10\nStructure: {data['structure']}/10\nOverall: {overall}/10\n")
                pdf.multi_cell(0, 8, f"Teaching Mode Explanation:\n{data['explanations']}\n")
                pdf_file_name = "Essay_Evaluation_Report.pdf"
                pdf.output(pdf_file_name)

                with open(pdf_file_name, "rb") as f:
                    st.download_button("⬇️ Download PDF", f, file_name=pdf_file_name)

                st.success("✅ Analysis Complete! Scroll up to see results.")
