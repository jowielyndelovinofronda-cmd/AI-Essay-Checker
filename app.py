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
# FORCE TESSERACT PATH (Windows)
# -----------------------------
# This MUST match your actual install location
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------
# Check if Tesseract works
# -----------------------------
try:
    version = pytesseract.get_tesseract_version()
    tesseract_available = True
except Exception as e:
    tesseract_available = False

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

        # Fallback to OCR if text extraction fails
        if not text.strip():
            pdf_file.seek(0)
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
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📷 Upload Image", "📸 Camera Scan", "📑 Upload PDF / Scan"])
essay_text = ""

# -----------------------------
# Paste text
# -----------------------------
if mode == "📄 Paste Text":
    st.subheader("📝 Enter Your Essay")
    essay_text = st.text_area("Paste or type your essay below:", height=250)

# -----------------------------
# Upload Image
# -----------------------------
elif mode == "📷 Upload Image":
    st.subheader("📷 Upload Image of Your Essay")
    uploaded_image = st.file_uploader("Upload image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])
    if uploaded_image:
        with st.spinner("Extracting text from image..."):
            essay_text = ocr_image(uploaded_image)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

# -----------------------------
# Camera Scan (OCR)
# -----------------------------
elif mode == "📸 Camera Scan":
    st.subheader("📸 Scan Using Your Camera")

    if not tesseract_available:
        st.error("❌ Tesseract OCR cannot be detected. Camera OCR is disabled.")
    else:
        camera_image = st.camera_input("Take a photo of your essay:")
        if camera_image:
            with st.spinner("Extracting text from camera image..."):
                essay_text = ocr_image(camera_image)
            st.subheader("📄 Extracted Text")
            st.write(essay_text)

# -----------------------------
# PDF Upload
# -----------------------------
else:
    st.subheader("📑 Upload PDF / Scanned Essay")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            essay_text = ocr_pdf(uploaded_pdf)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

# -----------------------------
# Evaluate Button (placeholder)
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text.strip():
        st.error("Please provide essay text via paste, image, camera, or PDF.")
    else:
        st.subheader("✔ Corrected Essay (Placeholder)")
        st.markdown(f"<div class='corrected'>{essay_text}</div>", unsafe_allow_html=True)

        st.subheader("📑 Summary Analysis (Placeholder)")
        st.markdown(f"<div class='summary'>This is a placeholder summary analysis.</div>", unsafe_allow_html=True)

        st.success("Thank you for using the checker!")
