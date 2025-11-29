import streamlit as st
import cv2
import numpy as np
from src.pipeline import OCRPipeline

# Initialize pipeline once
pipeline = OCRPipeline()

st.set_page_config(page_title="OCR Text Extraction App", layout="wide")

st.title("📄 AI OCR Text Extraction")
st.write("Upload a waybill image to extract the `_1_` pattern with confidence.")


# ==========================
# File Upload
# ==========================
uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])

if uploaded_file is not None:

    # Show original uploaded image
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, 1)

    st.subheader("📌 Original Image")
    st.image(img, channels="BGR", use_column_width=True)

    # Save uploaded image temporarily
    temp_path = "uploaded_image.jpg"
    cv2.imwrite(temp_path, img)

    # Run OCR Pipeline Button
    if st.button("🔍 Run OCR"):

        with st.spinner("Processing..."):
            result = pipeline.run(temp_path)

        # ==========================
        # Display Processed Image
        # ==========================
        if result["processed_image_path"]:
            st.subheader("🖼️ Preprocessed Image")
            processed_img = cv2.imread(result["processed_image_path"])
            st.image(processed_img, channels="BGR", use_column_width=True)

        # ==========================
        # Display Extracted `_1_` Pattern
        # ==========================
        st.subheader("📌 Extracted Pattern")

        if result["target_line"]:
            st.success(f"**Extracted Line:** `{result['target_line']}`")
            st.info(f"**Confidence:** {round(float(result['confidence']), 3)}")
        else:
            st.error(result["error"])

        # ==========================
        # Show OCR Output Table
        # ==========================
        st.subheader("📄 Full OCR Output")
        st.json(result["ocr_output"])
