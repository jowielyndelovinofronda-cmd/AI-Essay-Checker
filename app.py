import streamlit as st
from fpdf import FPDF
from docx import Document
from pdf2image import convert_from_bytes
from PyPDF2 import PdfReader
from wordcloud import WordCloud
from PIL import Image
import pytesseract
import io
import base64
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Streamlit UI
st.set_page_config(page_title="AI Text Originality Checker", layout="wide")

st.title("🧠 AI Text Originality Checker")

uploaded_file = st.file_uploader("Upload TXT, DOCX, or PDF", type=["txt", "docx", "pdf"])

def extract_text(file):
    if file.type == "text/plain":
        return file.read().decode("utf-8", errors="ignore")
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file.type == "application/pdf":
        text = ""
        try:
            reader = PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
        except:
            images = convert_from_bytes(file.read())
            for img in images:
                text += pytesseract.image_to_string(img)
        return text
    return ""

def create_wordcloud(text):
    wc = WordCloud(width=800, height=400, background_color="white").generate(text)
    img_bytes = io.BytesIO()
    wc.to_image().save(img_bytes, format="PNG")
    return img_bytes.getvalue()

def export_pdf(text):
    pdf = FPDF()
    pdf.add_page()

    # Use NotoSans if available
    if os.path.exists("NotoSans-Regular.ttf"):
        pdf.add_font("Noto", "", "NotoSans-Regular.ttf", uni=True)
        pdf.set_font("Noto", "", 12)
    else:
        pdf.set_font("Helvetica", "", 12)

    pdf.multi_cell(0, 10, text)
    file_path = "output.pdf"
    pdf.output(file_path)
    return file_path

def export_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    file_path = "output.docx"
    doc.save(file_path)
    return file_path

def ai_check(text):
    prompt = f"""
    Analyze the following text and detect if it is AI-generated or human-written.

    TEXT:
    {text}

    Provide the following in JSON:
    - ai_score (0–100)
    - human_score (0–100)
    - verdict (AI-generated, Human-written, or Mixed)
    - explanation (brief)
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

if uploaded_file:
    extracted_text = extract_text(uploaded_file)
    st.subheader("📄 Extracted Text")
    st.write(extracted_text)

    st.subheader("☁️ Word Cloud")
    img_data = create_wordcloud(extracted_text)
    st.image(img_data)

    st.subheader("🤖 AI Detection Result")
    result = ai_check(extracted_text)
    st.write(result)

    # Download buttons
    pdf_path = export_pdf(extracted_text)
    docx_path = export_docx(extracted_text)

    with open(pdf_path, "rb") as f:
        st.download_button("📥 Download as PDF", f, file_name="checked_output.pdf")

    with open(docx_path, "rb") as f:
        st.download_button("📥 Download as DOCX", f, file_name="checked_output.docx")

st.markdown("---")
st.markdown("### Thank you for using the checker! 💛")
