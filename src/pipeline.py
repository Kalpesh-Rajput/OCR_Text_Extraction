# import cv2
# from src.preprocessing import Preprocessor
# from src.ocr_engine import OCREngine
# from src.text_extraction import TextExtractor

# class OCRPipeline:
#     def __init__(self):
#         # Initialize all backend components
#         self.preprocessor = Preprocessor()
#         self.ocr_engine = OCREngine()
#         self.extractor = TextExtractor()

#     def _resize_original_for_ocr(self, image_path, max_width=1200):
#         """
#         Resize the original image if it's too large for EasyOCR.
#         Returns path to the image that should be fed to OCR.
#         """
#         img = cv2.imread(image_path)
#         if img is None:
#             raise FileNotFoundError(f"Cannot read image for OCR resizing: {image_path}")

#         h, w = img.shape[:2]
#         if w > max_width:
#             scale = max_width / w
#             new_w = int(w * scale)
#             new_h = int(h * scale)
#             resized_original_path = "resized_original_for_ocr.jpg"
#             resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
#             cv2.imwrite(resized_original_path, resized_img)
#             return resized_original_path
#         else:
#             return image_path

#     def run(self, image_path):
#         """
#         Complete backend pipeline:
#         1. Preprocess image (for deskew/visualization)
#         2. Resize original if needed & run OCR on original (resized)
#         3. Extract _1_ pattern
#         Returns dictionary:
#         {
#             "processed_image_path": "...",
#             "ocr_output": [...],
#             "target_line": "...",
#             "confidence": 0.95,
#             "error": None
#         }
#         """
#         result = {
#             "processed_image_path": None,
#             "ocr_output": [],
#             "target_line": None,
#             "confidence": None,
#             "error": None
#         }

#         try:
#             # STEP 1 — Preprocess (used for deskew/visual check)
#             processed = self.preprocessor.preprocess(image_path)
#             if processed is None:
#                 result["error"] = "Preprocessing failed"
#                 return result

#             processed_path = "processed_for_pipeline.jpg"
#             cv2.imwrite(processed_path, processed)
#             result["processed_image_path"] = processed_path

#             # STEP 2 — Prepare OCR input (resize original if it's too large)
#             try:
#                 ocr_input_path = self._resize_original_for_ocr(image_path, max_width=1200)
#             except Exception as e:
#                 result["error"] = f"Failed to prepare OCR input: {e}"
#                 return result

#             # Run OCR on the (possibly resized) original image
#             ocr_output = self.ocr_engine.extract_text(ocr_input_path)
#             result["ocr_output"] = ocr_output

#             if not ocr_output:
#                 result["error"] = "OCR returned no text"
#                 return result

#             # STEP 3 — Extract pattern _1_
#             extracted = self.extractor.find_target_line(ocr_output)
#             if extracted:
#                 result["target_line"] = extracted["text"]
#                 result["confidence"] = extracted["confidence"]
#             else:
#                 result["error"] = "Pattern '_1_' not found"

#             return result

#         except Exception as e:
#             result["error"] = str(e)
#             return result
        

#############################################################

# import cv2
# from src.preprocessing import Preprocessor
# from src.ocr_engine import OCREngine
# from src.text_extraction import TextExtractor

# class OCRPipeline:
#     def __init__(self):
#         self.preprocessor = Preprocessor()
#         self.ocr_engine = OCREngine()
#         self.extractor = TextExtractor()

#     def _resize_original_for_ocr(self, image_path, max_width=1200):
#         img = cv2.imread(image_path)
#         if img is None:
#             raise FileNotFoundError(f"Cannot read image for OCR resizing: {image_path}")
#         h, w = img.shape[:2]
#         if w > max_width:
#             scale = max_width / w
#             new_w = int(w * scale)
#             new_h = int(h * scale)
#             resized_original_path = "resized_original_for_ocr.jpg"
#             resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
#             cv2.imwrite(resized_original_path, resized_img)
#             return resized_original_path
#         else:
#             return image_path

#     def _run_ocr_on_candidates(self, candidates):
#         """
#         Run OCR on a list of file paths and aggregate outputs.
#         Returns combined list of OCR lines (dicts: text, confidence).
#         """
#         combined = []
#         seen_texts = set()
#         for path in candidates:
#             try:
#                 ocr_out = self.ocr_engine.extract_text(path)
#                 for item in ocr_out:
#                     t = item["text"].strip()
#                     if not t:
#                         continue
#                     # deduplicate identical texts (simple)
#                     if t not in seen_texts:
#                         combined.append(item)
#                         seen_texts.add(t)
#             except Exception:
#                 continue
#         return combined

#     def run(self, image_path):
#         result = {
#             "processed_image_path": None,
#             "ocr_output": [],
#             "target_line": None,
#             "confidence": None,
#             "error": None
#         }

#         try:
#             # STEP 1 — Preprocess (deskew + pad). This is for visualization and as an OCR candidate.
#             processed = self.preprocessor.preprocess(image_path)
#             if processed is None:
#                 result["error"] = "Preprocessing failed"
#                 return result

#             processed_path = "processed_for_pipeline.jpg"
#             cv2.imwrite(processed_path, processed)
#             result["processed_image_path"] = processed_path

#             # STEP 2 — Prepare OCR candidate files
#             candidates = []

#             # 2a. Resize original for OCR (primary)
#             try:
#                 ocr_original = self._resize_original_for_ocr(image_path, max_width=1200)
#                 candidates.append(ocr_original)
#             except Exception as e:
#                 # if cannot resize, still try original
#                 candidates.append(image_path)

#             # 2b. Use processed image as candidate (sometimes helps)
#             candidates.append(processed_path)

#             # 2c. Also try a resized version of processed image (if processed is very big)
#             try:
#                 proc_img = cv2.imread(processed_path)
#                 if proc_img is not None:
#                     h, w = proc_img.shape[:2]
#                     if w > 1200:
#                         resized_proc_path = "resized_processed_for_ocr.jpg"
#                         scale = 1200 / w
#                         resized_proc = cv2.resize(proc_img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
#                         cv2.imwrite(resized_proc_path, resized_proc)
#                         candidates.append(resized_proc_path)
#             except Exception:
#                 pass

#             # remove duplicates while preserving order
#             unique_candidates = []
#             seen = set()
#             for c in candidates:
#                 if c not in seen:
#                     unique_candidates.append(c)
#                     seen.add(c)

#             # STEP 3 — Run OCR on all candidates and combine outputs
#             combined_ocr = self._run_ocr_on_candidates(unique_candidates)
#             result["ocr_output"] = combined_ocr

#             if not combined_ocr:
#                 result["error"] = "OCR returned no text"
#                 return result

#             # STEP 4 — Extract pattern _1_ from combined OCR outputs
#             extracted = self.extractor.find_target_line(combined_ocr)
#             if extracted:
#                 result["target_line"] = extracted["text"]
#                 result["confidence"] = extracted["confidence"]
#             else:
#                 result["error"] = "Pattern '_1_' not found"

#             return result

#         except Exception as e:
#             result["error"] = str(e)
#             return result

##############################################################################################
import cv2
from src.preprocessing import Preprocessor
from src.ocr_engine import OCREngine
from src.text_extraction import TextExtractor

class OCRPipeline:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.ocr_engine = OCREngine()
        self.extractor = TextExtractor()

    def run(self, image_path):
        result = {
            "processed_image_path": None,
            "ocr_output": [],
            "target_line": None,
            "confidence": None,
            "error": None
        }

        # 1. Preprocess
        processed = self.preprocessor.preprocess(image_path)
        processed_path = "processed_for_pipeline.jpg"
        cv2.imwrite(processed_path, processed)
        result["processed_image_path"] = processed_path

        # 2. OCR on original
        o1 = self.ocr_engine.extract_text(image_path)

        # 3. OCR on processed
        cv2.imwrite("temp_processed.jpg", processed)
        o2 = self.ocr_engine.extract_text("temp_processed.jpg")

        # 4. Aggregate
        ocr_combined = o1 + o2
        result["ocr_output"] = ocr_combined

        # 5. Extract pattern
        extracted = self.extractor.find_target_line(ocr_combined)

        if extracted:
            result["target_line"] = extracted["text"]
            result["confidence"] = extracted["confidence"]
        else:
            result["error"] = "Pattern _1_ not found"

        return result
