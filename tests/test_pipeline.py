# tests/test_pipeline.py
import sys, os
ROOT = os.path.abspath(os.path.join(os.getcwd()))
sys.path.insert(0, ROOT)

from src.pipeline import OCRPipeline

pipeline = OCRPipeline()

IMAGE_NAME = "test06.jpg"  # change to one image in root

res = pipeline.run(IMAGE_NAME)
print("\n=== PIPELINE RESULT ===")
print(res)
