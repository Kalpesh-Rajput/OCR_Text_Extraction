# app.py
import streamlit as st
import cv2
import numpy as np
from src.pipeline import OCRPipeline

pipeline = OCRPipeline()

st.set_page_config(page_title="OCR Extractor", layout="wide")
st.title("🔍 OCR Text Extractor")

uploaded = st.file_uploader("Upload image", type=["jpg","jpeg","png"])
if uploaded:
    bytes_arr = np.asarray(bytearray(uploaded.read()), dtype=np.uint8)
    img = cv2.imdecode(bytes_arr, cv2.IMREAD_COLOR)
    st.subheader("Original")
    st.image(img[:,:,::-1], use_column_width=True)

    # save temp
    tmp = "uploaded_tmp.jpg"
    cv2.imwrite(tmp, img)

    if st.button("Run OCR"):
        with st.spinner("Running..."):
            res = pipeline.run(tmp)

        if res.get("processed_image_path"):
            st.subheader("Processed (deskewed + threshold)")
            proc = cv2.imread(res["processed_image_path"])
            if proc is not None:
                st.image(proc[:,:,::-1], use_column_width=True)

        st.subheader("Result")
        if res.get("target_line"):
            st.success(f"Extracted: `{res['target_line']}`  (conf: {round(float(res['confidence']),3)})")
        else:
            st.error(res.get("error"))

        st.subheader("OCR Outputs (top 30)")
        st.json(res.get("ocr_output")[:30])

        st.subheader("Diagnostics")
        st.json(res.get("diagnostics"))
