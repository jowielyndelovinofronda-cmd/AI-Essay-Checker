import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import PyPDF2
from wordcloud import WordCloud
from fpdf import FPDF
from docx import Document
import matplotlib.pyplot as plt
import random

# -----------------------------
# Tesseract Path (OCR)
# -----------------------------
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

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(page_title="Essay Checker + Scanner", page_icon="📘", layout="wide")

st.markdown("""
<style>
.main-title { font-size:42px; font-weight:700; color:#003366; text-align:center; margin-bottom:-10px;}
.subtitle { font-size:20px; color:#444; text-align:center; margin-bottom:30px;}
.score-box { padding:15px; border-radius:10px; background:#eef2ff; text-align:center; font-size:22px; font-weight:600; margin:10px;}
.corrected { background-color:#d4edda; padding:5px; border-radius:5px; }
.summary { background-color:#fff3cd; padding:5px; border-radius:5px; }
.footer { text-align:center; font-size:14px; color:#888; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📘 Essay Evaluation System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grammar • Spelling • Vocabulary • Coherence • Structure</div>', unsafe_allow_html=True)
st.write("___")

# -----------------------------
# Input Mode
# -----------------------------
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📷 Upload Image", "📸 Camera Scan", "📑 Upload PDF"])
essay_text = ""

if mode == "📄 Paste Text":
    essay_text = st.text_area("Paste or type your essay here:", height=250)
elif mode == "📷 Upload Image":
    uploaded_image = st.file_uploader("Upload image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])
    if uploaded_image:
        essay_text = ocr_image(uploaded_image)
elif mode == "📸 Camera Scan":
    camera_image = st.camera_input("Take a photo of your essay")
    if camera_image:
        st.info("📖 Extracting text from camera scan...")
        essay_text = ocr_image(camera_image)
        st.subheader("📄 Extracted Text from Camera")
        st.text_area("Extracted Text", essay_text, height=200)
elif mode == "📑 Upload PDF":
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        essay_text = extract_text_from_pdf(uploaded_pdf)

if essay_text and mode != "📸 Camera Scan":
    st.subheader("📄 Extracted / Entered Text")
    st.text_area("Essay Text", essay_text, height=200)

# -----------------------------
# Evaluate Button (Mock)
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text.strip():
        st.error("Please provide essay text first.")
    else:
        # -----------------------------
        # Fake Evaluation (Random Scores)
        # -----------------------------
        st.subheader("📊 Evaluation Scores (Sample)")
        scores = {k: random.randint(6, 10) for k in ["Grammar","Vocabulary","Coherence","Structure"]}
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='score-box'>Grammar<br>{scores['Grammar']}/10</div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='score-box'>Vocabulary<br>{scores['Vocabulary']}/10</div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='score-box'>Coherence<br>{scores['Coherence']}/10</div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='score-box'>Structure<br>{scores['Structure']}/10</div>", unsafe_allow_html=True)
        st.write("---")

        corrected_essay = essay_text  # Placeholder
        summary = "This is a summary analysis placeholder."

        st.subheader("✔ Corrected Essay")
        st.markdown(f"<div class='corrected'>{corrected_essay}</div>", unsafe_allow_html=True)

        st.subheader("📑 Summary Analysis")
        st.markdown(f"<div class='summary'>{summary}</div>", unsafe_allow_html=True)

        # Word Cloud
        st.subheader("☁️ Essay Word Cloud")
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(essay_text)
        fig, ax = plt.subplots(figsize=(10,5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # PDF Download
        pdf_file_name = "Essay_Report.pdf"
        pdf = FPDF()
        pdf.add_page()
        try:
            pdf.add_font('NotoSans', '', 'fonts/NotoSans-Regular.ttf', uni=True)
            pdf.set_font("NotoSans", "", 12)
        except:
            pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 8, f"Original Essay:\n{essay_text}\n")
        pdf.multi_cell(0, 8, f"Corrected Essay:\n{corrected_essay}\n")
        pdf.multi_cell(0, 8, f"Summary Analysis:\n{summary}\n")
        pdf.output(pdf_file_name)
        with open(pdf_file_name, "rb") as f:
            st.download_button("⬇️ Download PDF", f, file_name=pdf_file_name)

        # Word Doc Download
        doc_file_name = "Essay_Report.docx"
        doc = Document()
        doc.add_heading("Essay Evaluation Report", 0)
        doc.add_heading("Original Essay", level=1)
        doc.add_paragraph(essay_text)
        doc.add_heading("Corrected Essay", level=1)
        doc.add_paragraph(corrected_essay)
        doc.add_heading("Summary Analysis", level=1)
        doc.add_paragraph(summary)
        doc.save(doc_file_name)
        with open(doc_file_name, "rb") as f:
            st.download_button("⬇️ Download Word Doc", f, file_name=doc_file_name)

        st.success("✅ Analysis Complete!")
        st.markdown('<div class="footer">Thank you for using the checker!</div>', unsafe_allow_html=True)
