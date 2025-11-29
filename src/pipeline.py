import cv2
from src.preprocessing import Preprocessor
from src.ocr_engine import OCREngine
from src.text_extraction import TextExtractor

class OCRPipeline:
    def __init__(self):
        # Initialize all backend components
        self.preprocessor = Preprocessor()
        self.ocr_engine = OCREngine()
        self.extractor = TextExtractor()

    def _resize_original_for_ocr(self, image_path, max_width=1200):
        """
        Resize the original image if it's too large for EasyOCR.
        Returns path to the image that should be fed to OCR.
        """
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Cannot read image for OCR resizing: {image_path}")

        h, w = img.shape[:2]
        if w > max_width:
            scale = max_width / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            resized_original_path = "resized_original_for_ocr.jpg"
            resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            cv2.imwrite(resized_original_path, resized_img)
            return resized_original_path
        else:
            return image_path

    def run(self, image_path):
        """
        Complete backend pipeline:
        1. Preprocess image (for deskew/visualization)
        2. Resize original if needed & run OCR on original (resized)
        3. Extract _1_ pattern
        Returns dictionary:
        {
            "processed_image_path": "...",
            "ocr_output": [...],
            "target_line": "...",
            "confidence": 0.95,
            "error": None
        }
        """
        result = {
            "processed_image_path": None,
            "ocr_output": [],
            "target_line": None,
            "confidence": None,
            "error": None
        }

        try:
            # STEP 1 — Preprocess (used for deskew/visual check)
            processed = self.preprocessor.preprocess(image_path)
            if processed is None:
                result["error"] = "Preprocessing failed"
                return result

            processed_path = "processed_for_pipeline.jpg"
            cv2.imwrite(processed_path, processed)
            result["processed_image_path"] = processed_path

            # STEP 2 — Prepare OCR input (resize original if it's too large)
            try:
                ocr_input_path = self._resize_original_for_ocr(image_path, max_width=1200)
            except Exception as e:
                result["error"] = f"Failed to prepare OCR input: {e}"
                return result

            # Run OCR on the (possibly resized) original image
            ocr_output = self.ocr_engine.extract_text(ocr_input_path)
            result["ocr_output"] = ocr_output

            if not ocr_output:
                result["error"] = "OCR returned no text"
                return result

            # STEP 3 — Extract pattern _1_
            extracted = self.extractor.find_target_line(ocr_output)
            if extracted:
                result["target_line"] = extracted["text"]
                result["confidence"] = extracted["confidence"]
            else:
                result["error"] = "Pattern '_1_' not found"

            return result

        except Exception as e:
            result["error"] = str(e)
            return result
