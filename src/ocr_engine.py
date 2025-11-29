import easyocr

class OCREngine:
    def __init__(self):
        try:
            # Initialize EasyOCR (no unsupported arguments)
            self.ocr = easyocr.Reader(['en'], gpu=False)

            # Allowed characters for the waybill pattern
            self.allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"

        except Exception as e:
            raise RuntimeError(f"Failed to initialize EasyOCR: {e}")

    def _filter_allowed(self, text):
        return "".join([c for c in text if c in self.allowed_chars])

    def extract_text(self, image_path):
        try:
            raw_results = self.ocr.readtext(
                image_path,
                detail=1,
                paragraph=False
            )

            cleaned = []
            for box, text, confidence in raw_results:

                # Cleanup text using whitelist
                filtered = self._filter_allowed(text)

                if filtered.strip():
                    cleaned.append({
                        "text": filtered,
                        "confidence": confidence
                    })

            return cleaned

        except Exception as e:
            print("OCR Error:", e)
            return []
