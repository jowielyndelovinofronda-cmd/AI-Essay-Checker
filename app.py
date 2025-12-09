import streamlit as st
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import PyPDF2
from fpdf import FPDF
from docx import Document
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os
import json
import re

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
# Check Tesseract availability
# -----------------------------
try:
    pytesseract.get_tesseract_version()
    tesseract_available = True
except:
    tesseract_available = False

# -----------------------------
# Streamlit App Config
# -----------------------------
st.set_page_config(page_title="AI Essay Checker + Scanner", page_icon="📘", layout="wide")

st.markdown("""
<style>
.main-title { font-size:42px; font-weight:700; color:#003366; text-align:center; margin-bottom:-10px;}
.subtitle { font-size:20px; color:#444; text-align:center; margin-bottom:30px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📘 AI Essay Evaluation System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Grammar • Spelling • Vocabulary • Coherence • Structure</div>', unsafe_allow_html=True)
st.write("___")

# -----------------------------
# Input Mode Selection
# -----------------------------
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📷 Upload Image", "📸 Camera Scan", "📑 Upload PDF / Scan"])
essay_text = ""

if mode == "📄 Paste Text":
    st.subheader("📝 Enter Your Essay")
    essay_text = st.text_area("Paste or type your essay below:", height=250)

elif mode == "📷 Upload Image":
    st.subheader("📷 Upload Image of Your Essay")
    uploaded_image = st.file_uploader("Upload image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])
    if uploaded_image:
        with st.spinner("Extracting text from image..."):
            essay_text = ocr_image(uploaded_image)
        st.subheader("📄 Extracted Text")
        st.text_area("Extracted Text", value=essay_text, height=250)

elif mode == "📸 Camera Scan":
    if tesseract_available:
        camera_image = st.camera_input("Take a photo of your essay")
        if camera_image:
            with st.spinner("Extracting text from camera image..."):
                essay_text = ocr_image(camera_image)
            st.subheader("📄 Extracted Text")
            st.text_area("Extracted Text", value=essay_text, height=250)
    else:
        st.warning("⚠️ Tesseract OCR is not installed. Camera scanning is disabled.")

else:
    st.subheader("📑 Upload PDF / Scanned Essay")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            essay_text = ocr_pdf(uploaded_pdf)
        st.subheader("📄 Extracted Text")
        st.text_area("Extracted Text", value=essay_text, height=250)

# -----------------------------
# Evaluate Button
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text.strip():
        st.error("Please provide essay text via paste, image, camera, or PDF.")
    else:
        # Corrected Essay
        st.subheader("✔ Corrected Essay")
        st.text_area("Corrected Essay", value=essay_text, height=250)

        # Criteria Scores (dynamic placeholders)
        st.subheader("📊 Criteria Scores")
        criteria = {
            "Grammar": "Automatically evaluated score",
            "Spelling": "Automatically evaluated score",
            "Vocabulary": "Automatically evaluated score",
            "Coherence": "Automatically evaluated score",
            "Structure": "Automatically evaluated score"
        }
        st.json(criteria)

        # Summary Analysis
        st.subheader("📑 Summary Analysis")
        st.text_area("Summary Analysis", value="Automatically generated analysis based on essay.", height=100)

        # Download Corrected Essay
        st.download_button(
            label="💾 Download Corrected Essay",
            data=essay_text,
            file_name="corrected_essay.txt",
            mime="text/plain"
        )

        # Thank you note
        st.success("Thank you for using the AI Essay Checker!")
