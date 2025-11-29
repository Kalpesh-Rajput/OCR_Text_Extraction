
# from src.pipeline import OCRPipeline
from src.pipeline import OCRPipeline
pipeline = OCRPipeline()

img = "test.jpg"  # change for each test

res = pipeline.run(img)
print("\n=== RESULT ===")
print(res)
