# src/preprocessing.py
import cv2
import numpy as np

class Preprocessor:
    def __init__(self):
        pass

    def _rotate_bound(self, image, angle):
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))
        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY
        rotated = cv2.warpAffine(image, M, (nW, nH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated

    def _deskew(self, image):
        try:
            pad = 80
            image = cv2.copyMakeBorder(image, pad, pad, pad, pad, borderType=cv2.BORDER_REPLICATE)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (7,7), 0)
            thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            if thresh is None or thresh.size == 0:
                return image
            coords = np.column_stack(np.where(thresh > 0))
            if coords.size == 0:
                return image
            angle = cv2.minAreaRect(coords)[-1]
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle
            rotated = self._rotate_bound(image, angle)
            return rotated
        except Exception as e:
            print(f"[Preprocessor] Deskew failed: {e}")
            return image

    def preprocess(self, image_path):
        try:
            img = cv2.imread(image_path)
            if img is None:
                print(f"[Preprocessor] Failed to load: {image_path}")
                return None
            img = self._deskew(img)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            thresh = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 10)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
            morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
            return morph
        except Exception as e:
            print(f"[Preprocessor] Error: {e}")
            return None
