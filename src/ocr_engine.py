# import easyocr

# class OCREngine:
#     def __init__(self):
#         try:
#             # Initialize EasyOCR (no unsupported arguments)
#             self.ocr = easyocr.Reader(['en'], gpu=False)

#             # Allowed characters for the waybill pattern
#             self.allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-"

#         except Exception as e:
#             raise RuntimeError(f"Failed to initialize EasyOCR: {e}")

#     def _filter_allowed(self, text):
#         return "".join([c for c in text if c in self.allowed_chars])

#     def extract_text(self, image_path):
#         try:
#             raw_results = self.ocr.readtext(
#                 image_path,
#                 detail=1,
#                 paragraph=False
#             )

#             cleaned = []
#             for box, text, confidence in raw_results:

#                 # Cleanup text using whitelist
#                 filtered = self._filter_allowed(text)

#                 if filtered.strip():
#                     cleaned.append({
#                         "text": filtered,
#                         "confidence": confidence
#                     })

#             return cleaned

#         except Exception as e:
#             print("OCR Error:", e)
#             return []
        
######################################################################################################
import easyocr
import cv2

class OCREngine:
    def __init__(self):
        try:
            self.ocr = easyocr.Reader(
                ['en'],
                gpu=False,
                verbose=False
            )
        except Exception as e:
            raise RuntimeError(f"EasyOCR initialization failed: {e}")

    def extract_text(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            print("[OCR] Cannot load image.")
            return []

        h, w = img.shape[:2]

        # ------------------------------------
        # OCR candidates
        # ------------------------------------
        candidates = []

        # Full image
        candidates.append(img)

        # Bottom 30% of image (pattern usually here)
        bottom_crop = img[int(h * 0.65):h, 0:w]
        if bottom_crop.size > 0:
            candidates.append(bottom_crop)

        # Left-bottom corner
        left_crop = img[int(h * 0.65):h, 0:int(w * 0.4)]
        candidates.append(left_crop)

        # Right-bottom corner
        right_crop = img[int(h * 0.65):h, int(w * 0.6):w]
        candidates.append(right_crop)

        # ------------------------------------
        # Run OCR on each candidate
        # ------------------------------------
        results = []
        seen = set()

        for c in candidates:
            out = self.ocr.readtext(c, detail=1)
            for box, text, conf in out:
                clean = text.strip()
                if clean and clean not in seen:
                    seen.add(clean)
                    results.append({"text": clean, "confidence": float(conf)})

        return results

