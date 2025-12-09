import streamlit as st
import easyocr
from PIL import Image
import io

st.set_page_config(page_title="Camera OCR Test", page_icon="📷", layout="wide")
st.title("📸 Camera OCR Test")

# Initialize EasyOCR reader for English
reader = easyocr.Reader(['en'])

# Camera input
camera_image = st.camera_input("Take a photo of your essay")

if camera_image:
    st.image(camera_image, caption="Captured Image", use_column_width=True)
    
    with st.spinner("Extracting text..."):
        # Convert Streamlit image to PIL
        img = Image.open(camera_image)
        # Convert to bytes for EasyOCR
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        # OCR
        result = reader.readtext(img_bytes.getvalue(), detail=0)
        extracted_text = "\n".join(result)

    st.subheader("📄 Extracted Text")
    st.write(extracted_text)
