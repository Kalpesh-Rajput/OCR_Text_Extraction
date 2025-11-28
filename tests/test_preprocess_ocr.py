import sys
import os
import cv2

# Fix Python import path so it can find src/ folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

from src.preprocessing import Preprocessor
from src.ocr_engine import OCREngine


# ---- SET YOUR IMAGE PATH ----
# Place any sample image from your dataset in PROJECT ROOT as test.jpg
IMAGE_PATH = "reverseWaybill-156387426414724544_1.jpg"


print("\n=== STEP 1: TESTING PREPROCESSING ===")
pre = Preprocessor()
processed = pre.preprocess(IMAGE_PATH)

if processed is None:
    print("❌ Preprocessing failed. Check image path or preprocessing code.")
else:
    print("✅ Preprocessing successful:", processed.shape)

    # Save processed image to inspect visually
    cv2.imwrite("processed_output.jpg", processed)
    print("📁 Preprocessed image saved as processed_output.jpg")


print("\n=== STEP 2: TESTING EASYOCR ENGINE ===")
try:
    ocr = OCREngine()
except Exception as e:
    print(f"❌ Failed to initialize OCR engine: {e}")
    exit()

cv2.imwrite("processed_for_ocr.jpg", processed)
result = ocr.extract_text("processed_for_ocr.jpg")


if not result:
    print("❌ OCR returned NO text")
else:
    print("✅ OCR Output (text + confidence):\n")
    for line in result:
        print(f"Text: {line['text']} | Confidence: {line['confidence']}")
