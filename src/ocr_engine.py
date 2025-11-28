import easyocr

class OCREngine:
    def __init__(self):
        try:
            self.reader = easyocr.Reader(['en'], gpu=False)  # CPU mode
        except Exception as e:
            raise RuntimeError(f"Failed to initialize EasyOCR engine: {e}")

    def extract_text(self, image_path):
        """
        Returns list of:
        {
            "text": "...",
            "confidence": float
        }
        """

        try:
            results = self.reader.readtext(image_path, detail=1)

            extracted = []

            for (bbox, text, confidence) in results:
                extracted.append({
                    "text": text,
                    "confidence": float(confidence)
                })

            return extracted

        except Exception as e:
            print(f"OCR Error: {e}")
            return []
