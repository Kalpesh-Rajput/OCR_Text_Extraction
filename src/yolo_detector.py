import cv2
from ultralytics import YOLO

class YOLOTextDetector:
    def __init__(self):
        # Pretrained text detection model
        self.model = YOLO("yolov8x-ocr.pt")  

    def detect_text_boxes(self, image_path):
        results = self.model(image_path, conf=0.25)

        boxes = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                boxes.append([int(x1), int(y1), int(x2), int(y2)])

        return boxes
