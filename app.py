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
from docx import Document
import matplotlib.pyplot as plt
from io import BytesIO

# -----------------------------
# Load API key
# -----------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# Tesseract Path (OCR) - adjust if needed
# -----------------------------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# -----------------------------
# Helper Functions
# -----------------------------
def extract_json_from_text(text):
    """Try to extract a JSON object from text and parse it."""
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
            text += (page.extract_text() or "") + "\n"
        # If extraction returned nothing (scanned PDF), use image OCR
        if not text.strip():
            images = convert_from_bytes(pdf_file.read())
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
        return text.strip()
    except Exception as e:
        return f"ERROR: {e}"

def safe_text(text):
    """Convert text to latin-1 friendly format by replacing unsupported chars.
       Use when falling back to non-Unicode PDF fonts."""
    return text.encode("latin-1", "replace").decode("latin-1")

def try_add_unicode_font(pdf_obj, ttf_name="NotoSans-Regular.ttf", font_key="NotoSans"):
    """If a TTF file exists in the project, register it with FPDF for unicode support.
       Returns True if added, False otherwise."""
    if os.path.exists(ttf_name):
        try:
            pdf_obj.add_page()  # ensure page already exists will be fine
            pdf_obj.add_font(font_key, "", ttf_name, uni=True)
            pdf_obj.set_font(font_key, size=12)
            return True
        except Exception:
            return False
    return False

# -----------------------------
# AI detection (OpenAI-based)
# -----------------------------
def detect_ai_openai(essay_text):
    """Ask the model to produce an AI-likelihood percentage and short explanation in JSON."""
    detect_prompt = f"""
You are an AI writing detector. Analyze the following essay and return JSON with:
- "ai_likelihood": integer 0-100 (percentage that the essay was written by an AI)
- "explanation": brief (1-2 sentence) rationale for the score.

Return ONLY JSON. Essay below:

{essay_text}
"""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":detect_prompt}],
            max_tokens=300
        )
        raw = resp.choices[0].message.content
        parsed = extract_json_from_text(raw)
        return parsed, raw
    except Exception as e:
        return None, str(e)

# -----------------------------
# Streamlit App Config & Styles
# -----------------------------
st.set_page_config(page_title="AI Essay Checker + Scanner", page_icon="📘", layout="wide")

st.markdown("""
<style>
.main-title { font-size:42px; font-weight:700; color:#003366; text-align:center; margin-bottom:-8px;}
.subtitle { font-size:18px; color:#444; text-align:center; margin-bottom:18px;}
.score-box { padding:12px; border-radius:10px; background:#eef2ff; text-align:center; font-size:20px; font-weight:600; margin:6px;}
.corrected { background-color:#d4edda; padding:12px; border-radius:6px; white-space:pre-wrap; }
.summary { background-color:#fff3cd; padding:12px; border-radius:6px; white-space:pre-wrap; }
.small-muted { color:#666; font-size:12px; }
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

if mode == "📄 Paste Text":
    st.subheader("📝 Enter Your Essay")
    essay_text = st.text_area("Paste or type your essay below:", height=260)

elif mode == "📷 Upload Image":
    st.subheader("📷 Upload or Take a Photo of Your Essay")
    uploaded_image = st.file_uploader("Upload image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])
    camera_image = st.camera_input("Or take a photo")
    img_source = uploaded_image if uploaded_image else camera_image
    if img_source:
        with st.spinner("Extracting text from image..."):
            essay_text = ocr_image(img_source)
        st.subheader("📄 Extracted Text")
        st.code(essay_text, language=None)

else:
    st.subheader("📑 Upload PDF / Scanned Essay")
    uploaded_pdf = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_pdf:
        with st.spinner("Extracting text from PDF..."):
            essay_text = ocr_pdf(uploaded_pdf)
        st.subheader("📄 Extracted Text")
        st.code(essay_text, language=None)

# -----------------------------
# Optional AI Detection checkbox
# -----------------------------
detect_ai = st.checkbox("Check if essay is AI-generated (OpenAI-based)")

# -----------------------------
# Evaluate Button
# -----------------------------
if st.button("🔍 Evaluate Essay"):
    if not essay_text or not essay_text.strip():
        st.error("Please provide essay text via paste, image, or PDF.")
    else:
        with st.spinner("Analyzing essay with AI..."):
            # Main evaluation prompt (returns JSON)
            eval_prompt = f"""
You are a professional essay evaluator.

Evaluate the following essay for:
- Grammar
- Spelling
- Vocabulary
- Coherence
- Structure

Provide a corrected essay, a short summary analysis, and sentence-by-sentence explanations.

Return ONLY JSON exactly in this format:
{{
  "grammar": <int 1-10>,
  "vocabulary": <int 1-10>,
  "coherence": <int 1-10>,
  "structure": <int 1-10>,
  "corrected_essay": "<corrected essay text>",
  "summary": "<brief summary>",
  "explanations": "<sentence-by-sentence explanations>"
}}

Essay:
{essay_text}
"""
            try:
                eval_resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":eval_prompt}],
                    max_tokens=1200
                )
                raw_eval = eval_resp.choices[0].message.content
                data = extract_json_from_text(raw_eval)
            except Exception as e:
                st.error("Error calling evaluation model:")
                st.exception(e)
                data = None
                raw_eval = None

        # If evaluation failed or returned non-JSON, show raw response
        if data is None:
            st.error("⚠️ Unexpected AI output (evaluation). Showing raw output:")
            if raw_eval:
                st.code(raw_eval)
            st.stop()

        # --- SHOW SCORES & RESULTS ---
        st.subheader("📊 Evaluation Scores")
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<div class='score-box'>Grammar<br>{data.get('grammar','N/A')}/10</div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='score-box'>Vocabulary<br>{data.get('vocabulary','N/A')}/10</div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='score-box'>Coherence<br>{data.get('coherence','N/A')}/10</div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='score-box'>Structure<br>{data.get('structure','N/A')}/10</div>", unsafe_allow_html=True)

        st.write("---")

        st.subheader("✔ Corrected Essay")
        st.markdown(f"<div class='corrected'>{data.get('corrected_essay','')}</div>", unsafe_allow_html=True)

        st.subheader("📑 Summary Analysis")
        st.markdown(f"<div class='summary'>{data.get('summary','')}</div>", unsafe_allow_html=True)

        st.subheader("📘 Teaching Mode — Explanations")
        st.write(data.get('explanations',''))

        # Overall numeric average
        try:
            scores = [int(data.get('grammar',0)), int(data.get('vocabulary',0)),
                      int(data.get('coherence',0)), int(data.get('structure',0))]
            overall = round(sum(scores)/len(scores), 1)
        except:
            overall = "N/A"
        st.subheader("🏆 Overall Score")
        st.metric("Overall Score (out of 10)", overall)

        # Word cloud
        st.subheader("☁️ Essay Word Cloud")
        try:
            wc = WordCloud(width=800, height=300, background_color='white').generate(essay_text)
            fig, ax = plt.subplots(figsize=(10,4))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        except Exception as e:
            st.warning("Word cloud generation failed.")
            st.exception(e)

        # -----------------------------
        # AI Detection (OpenAI-based)
        # -----------------------------
        ai_result = None
        if detect_ai:
            with st.spinner("Running AI-likelihood detector..."):
                parsed_ai, raw_ai = detect_ai_openai(essay_text)
                if parsed_ai and isinstance(parsed_ai, dict) and "ai_likelihood" in parsed_ai:
                    # normalize likelihood to int
                    try:
                        ai_score = int(parsed_ai.get("ai_likelihood", 0))
                        ai_explanation = parsed_ai.get("explanation", "")
                        ai_result = {"score": ai_score, "explanation": ai_explanation}
                    except:
                        ai_result = None
                else:
                    # fallback: attempt simple parsing if the model returned a different format
                    ai_result = None

            if ai_result:
                st.subheader("🤖 AI Detection")
                st.metric("AI-written likelihood (%)", ai_result["score"])
                st.write(ai_result["explanation"])
            else:
                st.warning("AI detection did not return a valid result. Showing raw output:")
                if raw_ai:
                    st.code(raw_ai)

        # -----------------------------
        # DOWNLOADS: PDF and DOCX
        # -----------------------------
        st.write("---")
        st.subheader("📄 Download Report")

        # Prepare PDF in-memory (preferable to writing files)
        pdf = FPDF()
        pdf.add_page()

        # Try to register NotoSans if available; if not, use Helvetica and safe_text
        unicode_font_added = False
        if os.path.exists("NotoSans-Regular.ttf"):
            try:
                pdf.add_font("NotoSans", "", "NotoSans-Regular.ttf", uni=True)
                pdf.set_font("NotoSans", size=12)
                unicode_font_added = True
            except Exception:
                unicode_font_added = False

        if not unicode_font_added:
            pdf.set_font("Helvetica", size=12)

        # Content blocks
        def write_pdf_block(title, content):
            pdf.set_font(pdf.font_family, style="B", size=12)
            pdf.cell(0, 8, title, ln=True)
            pdf.ln(1)
            pdf.set_font(pdf.font_family, size=11)
            if unicode_font_added:
                pdf.multi_cell(0, 8, content)
            else:
                pdf.multi_cell(0, 8, safe_text(content))
            pdf.ln(4)

        write_pdf_block("Original Essay:", essay_text)
        write_pdf_block("Corrected Essay:", data.get("corrected_essay",""))
        write_pdf_block("Summary Analysis:", data.get("summary",""))
        scores_text = (
            f"Grammar: {data.get('grammar','N/A')}/10\n"
            f"Vocabulary: {data.get('vocabulary','N/A')}/10\n"
            f"Coherence: {data.get('coherence','N/A')}/10\n"
            f"Structure: {data.get('structure','N/A')}/10\n"
            f"Overall Score: {overall}/10\n"
        )
        write_pdf_block("Scores:", scores_text)
        write_pdf_block("Teaching Mode — Explanations:", data.get("explanations",""))
        if ai_result:
            write_pdf_block("AI Detection:", f"AI-written likelihood: {ai_result['score']}%\n{ai_result['explanation']}")

        # Get PDF bytes
        pdf_bytes = pdf.output(dest="S").encode("latin-1", "replace")
        st.download_button("⬇️ Download PDF Report", data=pdf_bytes, file_name="Essay_Evaluation_Report.pdf", mime="application/pdf")

        # Prepare DOCX in-memory
        doc = Document()
        doc.add_heading("AI Essay Evaluation Report", level=0)
        doc.add_heading("Original Essay", level=1)
        doc.add_paragraph(essay_text)
        doc.add_heading("Corrected Essay", level=1)
        doc.add_paragraph(data.get("corrected_essay",""))
        doc.add_heading("Summary Analysis", level=1)
        doc.add_paragraph(data.get("summary",""))
        doc.add_heading("Scores", level=1)
        doc.add_paragraph(scores_text)
        doc.add_heading("Teaching Mode — Explanations", level=1)
        doc.add_paragraph(data.get("explanations",""))
        if ai_result:
            doc.add_heading("AI Detection", level=1)
            doc.add_paragraph(f"AI-written likelihood: {ai_result['score']}%")
            doc.add_paragraph(ai_result['explanation'])

        # Save DOCX to bytes
        doc_stream = BytesIO()
        doc.save(doc_stream)
        doc_stream.seek(0)
        st.download_button("⬇️ Download Word Document", data=doc_stream, file_name="Essay_Evaluation_Report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        # -----------------------------
        # Final footer / thank you message
        # -----------------------------
        st.write("")  # spacing
        st.success("Thank you for using the checker!")
