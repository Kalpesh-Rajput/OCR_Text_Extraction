import re

class TextExtractor:
    def __init__(self):
        # Pattern required by assignment: something_1_something
        self.pattern = r"[A-Za-z0-9\-]*_1_[A-Za-z0-9\-]*"

    def find_target_line(self, ocr_output):
        """
        Input: list of OCR results like:
            [{ "text": "...", "confidence": 0.89 }, ... ]

        Returns:
            { "text": found_text, "confidence": confidence } or None
        """

        best_match = None
        best_confidence = 0.0

        for item in ocr_output:
            text = item["text"]
            conf = item["confidence"]

            match = re.search(self.pattern, text)

            if match:
                # Pick the line with the highest confidence
                if conf > best_confidence:
                    best_confidence = conf
                    best_match = {
                        "text": match.group(0),
                        "confidence": conf
                    }

        return best_match

# testing
# if __name__ == "__main__":
#     extractor = TextExtractor()
#     test_data = [
#         {"text": "random text", "confidence": 0.7},
#         {"text": "163233702292313922_1_lWV", "confidence": 0.9},
#         {"text": "another line", "confidence": 0.8},
#     ]
#     print(extractor.find_target_line(test_data))
