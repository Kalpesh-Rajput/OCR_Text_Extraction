# src/text_extraction.py
import re

class TextExtractor:
    def __init__(self):
        # Strict-ish pattern but allow short and long parts
        self.pattern = re.compile(r"[A-Za-z0-9\-]{3,}_1_[A-Za-z0-9\-]{1,}", re.IGNORECASE)

    def _normalize_common_errors(self, s):
        # replace common OCR confusions around the _1_ token
        # do replacements around the substring to avoid global changes
        s = s.replace("l_1_", "1_1_")  # rare double but helps
        s = s.replace("l_1", "1_1")
        s = s.replace("I_1", "1_1")
        s = s.replace("O_1", "0_1")
        s = s.replace(" o_1", " 0_1")
        # handle underscore missed or extra spaces
        s = s.replace(" -1-", "_1_")
        s = s.replace(" 1 ", "_1_")
        return s

    def find_target_line(self, ocr_output, min_confidence=0.0):
        """
        ocr_output: list of {"text":..., "confidence":float}
        Returns dict {"text": ..., "confidence": ...} or None
        """
        best = None
        best_conf = -1.0
        for item in ocr_output:
            text = item["text"]
            conf = float(item.get("confidence", 0.0))

            # normalize
            text_norm = self._normalize_common_errors(text)

            m = self.pattern.search(text_norm)
            if m:
                candidate = m.group(0)
                # if candidate contains suspicious chars, apply small fixes
                candidate = candidate.replace("O", "0")  # O -> 0 often
                candidate = candidate.replace("l", "1")
                # pick highest confidence match
                if conf > best_conf:
                    best_conf = conf
                    best = {"text": candidate, "confidence": conf}
        return best
