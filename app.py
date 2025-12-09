import streamlit as st
from PIL import Image
import easyocr
from pdf2image import convert_from_bytes
import PyPDF2
from io import BytesIO
from fpdf import FPDF
import json
import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud

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

def ocr_image(img):
    # Use EasyOCR to extract text from PIL Image
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    result = reader.readtext(img_bytes.getvalue(), detail=0)
    return "\n".join(result)

def ocr_pdf(pdf_file):
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        if not text.strip():
            images = convert_from_bytes(pdf_file.read())
            for img in images:
                text += ocr_image(img) + "\n"
        return text.strip()
    except Exception as e:
        return f"ERROR: {e}"

# -----------------------------
# Initialize EasyOCR
# -----------------------------
reader = easyocr.Reader(['en'])

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(page_title="AI Essay Checker + OCR", page_icon="📘", layout="wide")

st.title("📘 AI Essay Evaluation System")
st.subheader("Grammar • Spelling • Vocabulary • Coherence • Structure")

# -----------------------------
# Input Methods
# -----------------------------
mode = st.radio("Choose Input Method:", ["📄 Paste Text", "📷 Upload Image", "📸 Camera Scan", "📑 Upload PDF / Scan"])
essay_text = ""

if mode == "📄 Paste Text":
    essay_text = st.text_area("Paste or type your essay below:", height=250)

elif mode == "📷 Upload Image":
    uploaded_image = st.file_uploader("Upload image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])
    if uploaded_image:
        img = Image.open(uploaded_image)
        st.image(img, caption="Uploaded Image", use_column_width=True)
        # Optional: crop selection
        crop = st.checkbox("Crop Image before OCR")
        if crop:
            st.warning("Cropping feature: select the area (placeholder, integrate advanced cropping if needed)")
        essay_text = ocr_image(img)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

elif mode == "📸 Camera Scan":
    camera_image = st.camera_input("Take a photo of your essay")
    if camera_image:
        img = Image.open(camera_image)
        st.image(img, caption="Camera Image", use_column_width=True)
        crop = st.checkbox("Crop Camera Image before OCR")
        if crop:
            st.warning("Cropping feature: select the area to scan (like Google Lens) - placeholder for UI")
        essay_text = ocr_image(img)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

else:  # PDF
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        essay_text = ocr_pdf(uploaded_pdf)
        st.subheader("📄 Extracted Text")
        st.write(essay_text)

# -----------------------------
# Evaluate Essay
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text.strip():
        st.error("Please provide essay text via paste, image, camera, or PDF.")
    else:
        # Placeholder for scoring
        st.subheader("✔ Corrected Essay")
        st.markdown(f"<div style='background-color:#d4edda; padding:10px; border-radius:5px'>{essay_text}</div>", unsafe_allow_html=True)

        st.subheader("📊 Criteria Scores (Placeholder)")
        st.write({
            "Grammar": "85/100",
            "Spelling": "90/100",
            "Vocabulary": "80/100",
            "Coherence": "75/100",
            "Structure": "88/100"
        })

        st.subheader("📑 Summary Analysis (Placeholder)")
        st.markdown(f"<div style='background-color:#fff3cd; padding:10px; border-radius:5px'>This is a placeholder summary analysis.</div>", unsafe_allow_html=True)

        # Download corrected essay
        st.download_button(
            label="💾 Download Corrected Essay",
            data=essay_text,
            file_name="corrected_essay.txt",
            mime="text/plain"
        )
