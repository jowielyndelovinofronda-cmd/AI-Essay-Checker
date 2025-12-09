import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import PyPDF2
from fpdf import FPDF
from docx import Document
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# -----------------------------
# Tesseract OCR setup
# -----------------------------

if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    tesseract_available = True
else:
    tesseract_available = False

# -----------------------------
# Helper functions
# -----------------------------
def ocr_image(img_file):
    if tesseract_available:
        try:
            img = Image.open(img_file)
            return pytesseract.image_to_string(img).strip()
        except Exception as e:
            return f"ERROR: {e}"
    else:
        return "Tesseract OCR not installed. Cannot scan image."

def ocr_pdf(pdf_file):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        if not text.strip() and tesseract_available:
            pdf_file.seek(0)
            images = convert_from_bytes(pdf_file.read())
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
    except Exception as e:
        text = f"ERROR: {e}"
    return text.strip()

# -----------------------------
# Streamlit config
# -----------------------------
st.set_page_config(page_title="AI Essay Checker", page_icon="📘", layout="wide")
st.title("📘 Essay Checker & Scanner")
st.write("Grammar • Spelling • Vocabulary • Coherence • Structure")
st.write("---")

# -----------------------------
# Input selection
# -----------------------------
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📑 Upload PDF", "📷 Scan with Camera"])
essay_text = ""

if mode == "📄 Paste Text":
    essay_text = st.text_area("Paste or type your essay:", height=250)

elif mode == "📑 Upload PDF":
    uploaded_pdf = st.file_uploader("Upload PDF file", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            essay_text = ocr_pdf(uploaded_pdf)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

elif mode == "📷 Scan with Camera":
    if tesseract_available:
        camera_image = st.camera_input("Take a photo of your essay")
        if camera_image:
            with st.spinner("Scanning image..."):
                essay_text = ocr_image(camera_image)
            st.subheader("📄 Extracted Text")
            st.write(essay_text)
    else:
        st.warning("Tesseract OCR is not installed. Camera scanning is disabled.")

# -----------------------------
# Evaluate Button
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text.strip():
        st.error("Please provide essay text.")
    else:
        # Fake evaluation (placeholder)
        st.subheader("📊 Evaluation Scores")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Grammar", 8)
        col2.metric("Vocabulary", 7)
        col3.metric("Coherence", 8)
        col4.metric("Structure", 9)

        st.write("---")
        st.subheader("✔ Corrected Essay")
        corrected_essay = essay_text  # No AI, just placeholder
        st.write(corrected_essay)

        st.subheader("📑 Summary Analysis")
        summary = "This is a placeholder summary."
        st.write(summary)

        st.subheader("☁️ Word Cloud")
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(essay_text)
        fig, ax = plt.subplots(figsize=(10,5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # -----------------------------
        # PDF Download
        # -----------------------------
        pdf_file_name = "Essay_Report.pdf"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 8, f"Original Essay:\n{essay_text}\n\nCorrected Essay:\n{corrected_essay}\n\nSummary:\n{summary}")
        pdf.output(pdf_file_name)
        with open(pdf_file_name, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name=pdf_file_name)

        # -----------------------------
        # Word Doc Download
        # -----------------------------
        doc_file_name = "Essay_Report.docx"
        doc = Document()
        doc.add_heading("Essay Report", 0)
        doc.add_heading("Original Essay", level=1)
        doc.add_paragraph(essay_text)
        doc.add_heading("Corrected Essay", level=1)
        doc.add_paragraph(corrected_essay)
        doc.add_heading("Summary", level=1)
        doc.add_paragraph(summary)
        doc.save(doc_file_name)
        with open(doc_file_name, "rb") as f:
            st.download_button("⬇️ Download Word Doc", f, file_name=doc_file_name)

        st.success("Thank you for using the checker!")
