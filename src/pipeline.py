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

    def run(self, image_path):
        """
        Complete backend pipeline:
        1. Preprocess image
        2. Run OCR
        3. Extract _1_ pattern
        Returns dictionary:
        {
            "processed_image_path": "...",
            "ocr_output": [...],
            "target_line": "...",
            "confidence": 0.95
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
            # STEP 1 — Preprocess
            processed = self.preprocessor.preprocess(image_path)
            if processed is None:
                result["error"] = "Preprocessing failed"
                return result

            processed_path = "processed_for_pipeline.jpg"
            cv2.imwrite(processed_path, processed)
            result["processed_image_path"] = processed_path

            # STEP 2 — OCR on processed image
            ocr_output = self.ocr_engine.extract_text(processed_path)
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
