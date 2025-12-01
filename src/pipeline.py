# src/pipeline.py
import cv2
from src.preprocessing import Preprocessor
from src.ocr_engine import OCREngine
from src.text_extraction import TextExtractor
import os

class OCRPipeline:
    def __init__(self):
        self.preprocessor = Preprocessor()
        self.ocr_engine = OCREngine()
        self.extractor = TextExtractor()

    def _resize_if_needed(self, image_path, max_w=1200):
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(image_path)
        h, w = img.shape[:2]
        if w > max_w:
            scale = max_w / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            out = "resized_original_for_ocr.jpg"
            resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
            cv2.imwrite(out, resized)
            return out
        return image_path

    def _run_ocr_candidates(self, candidates):
        combined = []
        diag = {}
        seen = {}
        idx = 0
        for cand in candidates:
            try:
                img = cv2.imread(cand)
                shape = img.shape[:2] if img is not None else None
            except Exception:
                shape = None
            ocr_out = []
            try:
                ocr_out = self.ocr_engine.extract_text(cand)
            except Exception as e:
                ocr_out = []
            diag[f"cand_{idx}"] = {"path": cand, "shape": shape, "ocr_count": len(ocr_out), "ocr_sample": ocr_out[:5]}
            for item in ocr_out:
                t = item["text"].strip()
                c = float(item["confidence"])
                # keep best per exact text
                if t not in seen or c > seen[t]:
                    seen[t] = c
            idx += 1
        # produce combined list sorted by confidence desc
        combined = [{"text": t, "confidence": seen[t]} for t in sorted(seen, key=lambda x: -seen[x])]
        return combined, diag

    def run(self, image_path):
        result = {
            "processed_image_path": None,
            "ocr_output": [],
            "target_line": None,
            "confidence": None,
            "diagnostics": {},
            "error": None
        }
        try:
            # preprocess (deskew+padded) and save
            processed = self.preprocessor.preprocess(image_path)
            if processed is None:
                result["error"] = "Preprocessing failed"
                return result
            proc_path = "processed_for_pipeline.jpg"
            cv2.imwrite(proc_path, processed)
            result["processed_image_path"] = proc_path

            # candidates for OCR
            candidates = []
            # resized original
            try:
                r = self._resize_if_needed(image_path)
                candidates.append(r)
            except Exception:
                candidates.append(image_path)
            # processed (padded + deskew)
            candidates.append(proc_path)
            # smaller resized processed (if large)
            try:
                imgp = cv2.imread(proc_path)
                if imgp is not None:
                    h, w = imgp.shape[:2]
                    if w > 1200:
                        rp = "resized_processed_for_ocr.jpg"
                        scale = 1200 / w
                        resized = cv2.resize(imgp, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
                        cv2.imwrite(rp, resized)
                        candidates.append(rp)
            except Exception:
                pass

            # dedupe candidates preserve order
            unique = []
            seen = set()
            for c in candidates:
                if c not in seen:
                    unique.append(c); seen.add(c)

            combined, diag = self._run_ocr_candidates(unique)
            result["ocr_output"] = combined
            result["diagnostics"] = diag

            if not combined:
                result["error"] = "OCR returned no text"
                return result

            extracted = self.extractor.find_target_line(combined)
            if extracted:
                result["target_line"] = extracted["text"]
                result["confidence"] = extracted["confidence"]
            else:
                result["error"] = "Pattern '_1_' not found"

            return result
        except Exception as e:
            result["error"] = str(e)
            return result
