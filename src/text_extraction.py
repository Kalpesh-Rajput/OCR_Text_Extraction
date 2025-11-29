import re

class TextExtractor:
    def __init__(self):
        # Strict target pattern
        self.pattern = r"[A-Za-z0-9\-]{6,}_1_[A-Za-z0-9\-]{2,}"

    def _correct_common_errors(self, text):
        corrections = {
            "l": "1",
            "I": "1",
            "O": "0",
            "S": "5"
        }
        for bad, good in corrections.items():
            text = text.replace(bad + "_1_", good + "_1_")
        return text

    def find_target_line(self, ocr_output):
        best_match = None
        best_conf = 0.0

        for item in ocr_output:
            text = self._correct_common_errors(item["text"])
            conf = item["confidence"]

            match = re.search(self.pattern, text)
            if match and conf > best_conf:
                best_match = {
                    "text": match.group(0),
                    "confidence": conf
                }
                best_conf = conf

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
