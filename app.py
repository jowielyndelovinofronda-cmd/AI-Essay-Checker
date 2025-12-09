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
# Tesseract Path (OCR)
# -----------------------------
# Update this path if Tesseract is installed elsewhere
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------
# Helper Functions
# -----------------------------
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        if not text.strip():
            # fallback to OCR if text extraction fails
            images = convert_from_bytes(pdf_file.read())
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        return text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def ocr_image(img_file):
    try:
        img = Image.open(img_file)
        return pytesseract.image_to_string(img).strip()
    except Exception as e:
        return f"ERROR: {e}"

def sanitize_pdf_text(text):
    # Encode for PDF safely
    return text.encode('latin1', errors='replace').decode('latin1')

# -----------------------------
# Streamlit App Config
# -----------------------------
st.set_page_config(page_title="AI Essay Checker", page_icon="📘", layout="wide")

# -----------------------------
# App Title & Styling
# -----------------------------
st.markdown("""
<style>
.main-title { font-size:42px; font-weight:700; color:#003366; text-align:center; margin-bottom:-10px;}
.subtitle { font-size:20px; color:#444; text-align:center; margin-bottom:30px;}
.score-box { padding:15px; border-radius:10px; background:#eef2ff; text-align:center; font-size:22px; font-weight:600; margin:10px;}
.corrected { background-color:#d4edda; padding:5px; border-radius:5px; }
.summary { background-color:#fff3cd; padding:5px; border-radius:5px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📘 AI Essay Checker</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grammar • Spelling • Vocabulary • Coherence • Structure</div>', unsafe_allow_html=True)
st.write("___")

# -----------------------------
# Input Mode Selection
# -----------------------------
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📷 Upload Image", "📸 Scan with Camera", "📑 Upload PDF / Scan"])
essay_text = ""

if mode == "📄 Paste Text":
    st.subheader("📝 Enter Your Essay")
    essay_text = st.text_area("Paste or type your essay here:", height=250)

elif mode == "📷 Upload Image":
    st.subheader("📷 Upload Image of Essay")
    uploaded_image = st.file_uploader("Upload image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])
    if uploaded_image:
        with st.spinner("Extracting text from image..."):
            essay_text = ocr_image(uploaded_image)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

elif mode == "📸 Scan with Camera":
    st.subheader("📸 Use Your Camera")
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
            essay_text = extract_text_from_pdf(uploaded_pdf)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

# -----------------------------
# Evaluate Button
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text.strip():
        st.error("Please provide essay text via paste, image, camera, or PDF.")
    else:
        with st.spinner("Analyzing essay..."):
            # Dummy analysis logic (replace with your AI or manual rules)
            # Here we simulate evaluation
            import random
            grammar = random.randint(6,10)
            vocabulary = random.randint(6,10)
            coherence = random.randint(6,10)
            structure = random.randint(6,10)
            corrected_essay = essay_text  # For now, we just echo original
            summary = "This is a summary of your essay analysis."
            explanations = "Sentence-by-sentence explanations would appear here."

            # --- Evaluation Scores ---
            st.subheader("📊 Evaluation Scores")
            col1, col2, col3, col4 = st.columns(4)
            col1.markdown(f"<div class='score-box'>Grammar<br>{grammar}/10</div>", unsafe_allow_html=True)
            col2.markdown(f"<div class='score-box'>Vocabulary<br>{vocabulary}/10</div>", unsafe_allow_html=True)
            col3.markdown(f"<div class='score-box'>Coherence<br>{coherence}/10</div>", unsafe_allow_html=True)
            col4.markdown(f"<div class='score-box'>Structure<br>{structure}/10</div>", unsafe_allow_html=True)

            st.write("---")

            # --- Corrected Essay ---
            st.subheader("✔ Corrected Essay")
            st.markdown(f"<div class='corrected'>{corrected_essay}</div>", unsafe_allow_html=True)

            # --- Summary Analysis ---
            st.subheader("📑 Summary Analysis")
            st.markdown(f"<div class='summary'>{summary}</div>", unsafe_allow_html=True)

            # --- Teaching Mode / Explanation ---
            st.subheader("📘 Teaching Mode – Explanation")
            st.write(explanations)

            # --- Overall Score ---
            overall = (grammar + vocabulary + coherence + structure)/4
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
            # Use NotoSans if present; else fallback to default
            try:
                pdf.add_font('NotoSans', '', 'NotoSans-Regular.ttf', uni=True)
                pdf.set_font("NotoSans", "", 12)
            except:
                pdf.set_font("Helvetica", "", 12)
            pdf.multi_cell(0, 8, f"Original Essay:\n{essay_text}\n")
            pdf.multi_cell(0, 8, f"Corrected Essay:\n{corrected_essay}\n")
            pdf.multi_cell(0, 8, f"Summary Analysis:\n{summary}\n")
            pdf.multi_cell(0, 8, f"Scores:\nGrammar: {grammar}/10\nVocabulary: {vocabulary}/10\nCoherence: {coherence}/10\nStructure: {structure}/10\nOverall: {overall}/10\n")
            pdf.output(pdf_file_name)
            with open(pdf_file_name, "rb") as f:
                st.download_button("⬇️ Download PDF", f, file_name=pdf_file_name)

            # --- Word Document Download ---
            doc_file_name = "Essay_Evaluation_Report.docx"
            doc = Document()
            doc.add_heading("AI Essay Evaluation Report", 0)
            doc.add_heading("Original Essay", level=1)
            doc.add_paragraph(essay_text)
            doc.add_heading("Corrected Essay", level=1)
            doc.add_paragraph(corrected_essay)
            doc.add_heading("Summary Analysis", level=1)
            doc.add_paragraph(summary)
            doc.add_heading("Scores", level=1)
            doc.add_paragraph(f"Grammar: {grammar}/10\nVocabulary: {vocabulary}/10\nCoherence: {coherence}/10\nStructure: {structure}/10\nOverall: {overall}/10")
            doc.add_heading("Teaching Mode – Explanation", level=1)
            doc.add_paragraph(explanations)
            doc.save(doc_file_name)
            with open(doc_file_name, "rb") as f:
                st.download_button("⬇️ Download Word Doc", f, file_name=doc_file_name)

            # --- Footer ---
            st.success("✅ Thank you for using the checker!")
