import streamlit as st
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
from docx import Document
import matplotlib.pyplot as plt

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

# -----------------------------
# Tesseract OCR Configuration
# -----------------------------
tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

try:
    pytesseract.get_tesseract_version()
    tesseract_available = True
except:
    tesseract_available = False

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
.corrected { background-color:#d4edda; padding:5px; border-radius:5px; }
.summary { background-color:#fff3cd; padding:5px; border-radius:5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📘 AI Essay Evaluation System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grammar • Spelling • Vocabulary • Coherence • Structure</div>', unsafe_allow_html=True)
st.write("___")

# -----------------------------
# Input Mode Selection
# -----------------------------
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📷 Camera Scan", "📑 Upload PDF"])
essay_text = ""

if mode == "📄 Paste Text":
    st.subheader("📝 Enter Your Essay")
    essay_text = st.text_area("Paste or type your essay below:", height=250)

elif mode == "📷 Camera Scan":
    if not tesseract_available:
        st.warning("⚠️ Tesseract OCR is not installed. Camera scanning is disabled.")
    else:
        camera_image = st.camera_input("Take a photo of your essay")
        if camera_image:
            with st.spinner("Extracting text from camera image..."):
                essay_text = ocr_image(camera_image)
            st.subheader("📄 Extracted Text")
            st.write(essay_text)

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
        st.error("Please provide essay text via paste, camera scan, or PDF.")
    else:
        # For simplicity, this version only demonstrates local corrections.
        # You can integrate your AI evaluation logic here.
        corrected_essay = essay_text  # Replace with actual corrected text if AI is used
        summary_analysis = "This is a placeholder summary of the essay."
        grammar_score = 8
        vocabulary_score = 8
        coherence_score = 8
        structure_score = 8
        overall = round((grammar_score + vocabulary_score + coherence_score + structure_score)/4, 2)

        # --- Evaluation Scores ---
        st.subheader("📊 Evaluation Scores")
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='score-box'>Grammar<br>{grammar_score}/10</div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='score-box'>Vocabulary<br>{vocabulary_score}/10</div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='score-box'>Coherence<br>{coherence_score}/10</div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='score-box'>Structure<br>{structure_score}/10</div>", unsafe_allow_html=True)

        st.write("---")

        # --- Corrected Essay ---
        st.subheader("✔ Corrected Essay")
        st.markdown(f"<div class='corrected'>{corrected_essay}</div>", unsafe_allow_html=True)

        # --- Summary Analysis ---
        st.subheader("📑 Summary Analysis")
        st.markdown(f"<div class='summary'>{summary_analysis}</div>", unsafe_allow_html=True)

        # --- Overall Score ---
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
        pdf_file_name = "Essay_Evaluation_Report.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 8, f"Original Essay:\n{essay_text}\n")
        pdf.multi_cell(0, 8, f"Corrected Essay:\n{corrected_essay}\n")
        pdf.multi_cell(0, 8, f"Summary Analysis:\n{summary_analysis}\n")
        pdf.multi_cell(0, 8, f"Scores:\nGrammar: {grammar_score}/10\nVocabulary: {vocabulary_score}/10\nCoherence: {coherence_score}/10\nStructure: {structure_score}/10\nOverall: {overall}/10\n")
        pdf.output(pdf_file_name)
        with open(pdf_file_name, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name=pdf_file_name)

        # --- Word Document Option ---
        doc_file_name = "Essay_Evaluation_Report.docx"
        doc = Document()
        doc.add_heading("AI Essay Evaluation Report", 0)
        doc.add_heading("Original Essay", level=1)
        doc.add_paragraph(essay_text)
        doc.add_heading("Corrected Essay", level=1)
        doc.add_paragraph(corrected_essay)
        doc.add_heading("Summary Analysis", level=1)
        doc.add_paragraph(summary_analysis)
        doc.add_heading("Scores", level=1)
        doc.add_paragraph(f"Grammar: {grammar_score}/10\nVocabulary: {vocabulary_score}/10\nCoherence: {coherence_score}/10\nStructure: {structure_score}/10\nOverall: {overall}/10")
        doc.save(doc_file_name)
        with open(doc_file_name, "rb") as f:
            st.download_button("⬇️ Download Word Doc", f, file_name=doc_file_name)

        st.success("🙏 Thank you for using the checker!")
