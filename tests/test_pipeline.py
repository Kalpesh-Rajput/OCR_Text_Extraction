import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), "")))

from src.pipeline import OCRPipeline

pipeline = OCRPipeline()

# Replace this with the exact filename that exists in your project root
# e.g. "test.jpg" or "reverseWaybill-156387426414724544_1.jpg"
IMAGE_NAME = "test01.jpg"

result = pipeline.run(IMAGE_NAME)

print("\n=== PIPELINE RESULT ===")
print(result)
