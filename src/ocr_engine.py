# src/ocr_engine.py
import os
import cv2
import pytesseract
import easyocr
import numpy as np

class OCREngine:
    def __init__(self, languages=["en"]):
        try:
            # EasyOCR reader (CPU)
            self.reader = easyocr.Reader(languages, gpu=False)
        except Exception as e:
            print(f"EasyOCR init error: {e}")
            self.reader = None

        # Tesseract config - whitelist and psm for line recognition
        # allow digits, letters, underscore and hyphen
        self.whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"
        self.tess_config = f"-c tessedit_char_whitelist={self.whitelist} --psm 6"

    def _tesseract_read(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                return []

            # convert to RGB for pytesseract
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # use image_to_data to get line-level results
            data = pytesseract.image_to_data(rgb, config=self.tess_config, output_type=pytesseract.Output.DICT)

            results = []
            n = len(data["text"])
            for i in range(n):
                txt = data["text"][i].strip()
                conf = float(data["conf"][i]) if data["conf"][i] != '-1' else 0.0
                if txt:
                    # filter to allowed characters
                    filtered = "".join([c for c in txt if c in self.whitelist])
                    if filtered:
                        results.append({"text": filtered, "confidence": conf/100.0})
            return results
        except Exception as e:
            print("Tesseract error:", e)
            return []

    def _easyocr_read(self, image_path):
        if self.reader is None:
            return []
        try:
            results = self.reader.readtext(image_path, detail=1, paragraph=False)
            cleaned = []
            for box, text, conf in results:
                if not text:
                    continue
                filtered = "".join([c for c in text if c in self.whitelist])
                if filtered:
                    cleaned.append({"text": filtered, "confidence": float(conf)})
            return cleaned
        except Exception as e:
            print("EasyOCR error:", e)
            return []

    def extract_text(self, image_path):
        """
        Returns combined list of OCR outputs from EasyOCR and Tesseract.
        Each item: {"text": ..., "confidence": 0.0-1.0}
        """
        outputs = []

        # EasyOCR first (if available)
        try:
            e_out = self._easyocr_read(image_path)
            outputs.extend(e_out)
        except Exception as _:
            pass

        # Tesseract
        try:
            t_out = self._tesseract_read(image_path)
            outputs.extend(t_out)
        except Exception as _:
            pass

        # Final dedupe preserving order: keep best confidence per exact text
        seen = {}
        combined = []
        for item in outputs:
            t = item["text"]
            c = float(item["confidence"])
            if t not in seen or c > seen[t]:
                seen[t] = c
        # produce list sorted by confidence desc
        for t, c in sorted(seen.items(), key=lambda x: -x[1]):
            combined.append({"text": t, "confidence": c})

        return combined
    
