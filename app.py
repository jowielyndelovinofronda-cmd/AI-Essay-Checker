import streamlit as st
import os
import json
import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import PyPDF2
from wordcloud import WordCloud
from fpdf import FPDF
from docx import Document
import matplotlib.pyplot as plt

# -----------------------------
# Helper Functions
# -----------------------------
def extract_json_from_text(text):
    try:
        return json.loads(text)
    except:
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
# Tesseract OCR Check
# -----------------------------
try:
    pytesseract.get_tesseract_version()
    tesseract_available = True
except:
    tesseract_available = False

# -----------------------------
# Streamlit App Config
# -----------------------------
st.set_page_config(page_title="Essay Checker + Scanner", page_icon="📘", layout="wide")

st.markdown("""
<style>
.main-title { font-size:42px; font-weight:700; color:#003366; text-align:center; margin-bottom:-10px;}
.subtitle { font-size:20px; color:#444; text-align:center; margin-bottom:30px;}
.score-box { padding:15px; border-radius:10px; background:#eef2ff; text-align:center; font-size:22px; font-weight:600; margin:10px;}
.corrected { background-color:#d4edda; padding:5px; border-radius:5px; }
.summary { background-color:#fff3cd; padding:5px; border-radius:5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📘 Essay Evaluation System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grammar • Spelling • Vocabulary • Coherence • Structure</div>', unsafe_allow_html=True)
st.write("___")

# -----------------------------
# Input Mode Selection
# -----------------------------
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📷 Upload Image", "📑 Upload PDF / Scan"])
essay_text = ""

if mode == "📄 Paste Text":
    st.subheader("📝 Enter Your Essay")
    essay_text = st.text_area("Paste or type your essay below:", height=250)
elif mode == "📷 Upload Image":
    st.subheader("📷 Upload or Take a Photo of Your Essay")
    uploaded_image = st.file_uploader("Upload image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])
    if uploaded_image:
        with st.spinner("Extracting text from image..."):
            essay_text = ocr_image(uploaded_image)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)
elif mode == "📑 Upload PDF / Scan":
    st.subheader("📑 Upload PDF / Scanned Essay")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            essay_text = ocr_pdf(uploaded_pdf)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

# Camera scanning (only if Tesseract is available)
if tesseract_available:
    camera_image = st.camera_input("📷 Or take a photo of your essay")
    if camera_image:
        with st.spinner("Extracting text from camera image..."):
            essay_text = ocr_image(camera_image)
        st.subheader("📄 Extracted Text from Camera")
        st.write(essay_text)
else:
    st.warning("⚠️ Tesseract OCR is not installed. Camera scanning is disabled.")

# -----------------------------
# Evaluate Button (Dummy Scores)
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text.strip():
        st.error("Please provide essay text via paste, image, PDF, or camera.")
    else:
        with st.spinner("Analyzing essay..."):
            # Generate dummy scores for demonstration
            data = {
                "grammar": 8,
                "vocabulary": 7,
                "coherence": 8,
                "structure": 9,
                "corrected_essay": essay_text,  # Just echoing original text
                "summary": "Your essay is well-structured and coherent. Minor vocabulary improvements suggested.",
                "explanations": "Each sentence is grammatically correct with slight vocabulary improvements recommended."
            }

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
            st.markdown(f"<div class='corrected'>{data['corrected_essay']}</div>", unsafe_allow_html=True)

            # --- Summary Analysis ---
            st.subheader("📑 Summary Analysis")
            st.markdown(f"<div class='summary'>{data.get('summary','No summary')}</div>", unsafe_allow_html=True)

            # --- Teaching Mode ---
            st.subheader("📘 Teaching Mode – Explanation")
            st.write(data["explanations"])

            # --- Overall Score ---
            scores = [int(data['grammar']), int(data['vocabulary']), int(data['coherence']), int(data['structure'])]
            overall = sum(scores)/len(scores)
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
            st.subheader("📄 Download Corrected Essay & Summary")
            pdf_file_name = "Essay_Evaluation_Report.pdf"
            pdf = FPDF()
            pdf.add_page()
            # Use NotoSans for Unicode support if available
            font_path = "NotoSans-Regular.ttf"
            if os.path.exists(font_path):
                pdf.add_font("NotoSans", "", font_path, uni=True)
                pdf.set_font("NotoSans", "", 12)
            else:
                pdf.set_font("Helvetica", "", 12)
            pdf.multi_cell(0, 8, f"Original Essay:\n{essay_text}\n")
            pdf.multi_cell(0, 8, f"Corrected Essay:\n{data['corrected_essay']}\n")
            pdf.multi_cell(0, 8, f"Summary Analysis:\n{data.get('summary','No summary')}\n")
            pdf.multi_cell(0, 8, f"Scores:\nGrammar: {data['grammar']}/10\nVocabulary: {data['vocabulary']}/10\nCoherence: {data['coherence']}/10\nStructure: {data['structure']}/10\nOverall: {overall}/10\n")
            pdf.output(pdf_file_name)
            with open(pdf_file_name, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name=pdf_file_name)

            # --- Word Document Option ---
            doc_file_name = "Essay_Evaluation_Report.docx"
            doc = Document()
            doc.add_heading("Essay Evaluation Report", 0)
            doc.add_heading("Original Essay", level=1)
            doc.add_paragraph(essay_text)
            doc.add_heading("Corrected Essay", level=1)
            doc.add_paragraph(data['corrected_essay'])
            doc.add_heading("Summary Analysis", level=1)
            doc.add_paragraph(data.get('summary','No summary'))
            doc.add_heading("Scores", level=1)
            doc.add_paragraph(f"Grammar: {data['grammar']}/10\nVocabulary: {data['vocabulary']}/10\nCoherence: {data['coherence']}/10\nStructure: {data['structure']}/10\nOverall: {overall}/10")
            doc.add_heading("Teaching Mode – Explanation", level=1)
            doc.add_paragraph(data["explanations"])
            doc.save(doc_file_name)
            with open(doc_file_name, "rb") as f:
                st.download_button("⬇️ Download Word Doc", f, file_name=doc_file_name)

            st.success("🙏 Thank you for using the checker!")
