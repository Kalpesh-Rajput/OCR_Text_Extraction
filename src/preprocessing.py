import cv2
import numpy as np

class Preprocessor:
    def __init__(self):
        pass

    def load_image(self, image_path):
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Error: Unable to load image: {image_path}")
        return image

    def to_gray(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def denoise(self, img):
        return cv2.GaussianBlur(img, (5, 5), 0)

    def enhance_contrast(self, img):
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        return clahe.apply(img)

    def thresholding(self, img):
        return cv2.adaptiveThreshold(
            img, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 2
        )

    def resize(self, img, scale=1.5):
        h, w = img.shape[:2]
        return cv2.resize(img, (int(w * scale), int(h * scale)))

    def deskew(self, img):
        coords = np.column_stack(np.where(img > 0))
        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        (h, w) = img.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    def preprocess(self, image_path):
        try:
            img = self.load_image(image_path)

            gray = self.to_gray(img)
            den = self.denoise(gray)
            contrast = self.enhance_contrast(den)
            resized = self.resize(contrast)
            thresh = self.thresholding(resized)
            deskewed = self.deskew(thresh)

            return deskewed

        except Exception as e:
            print(f"Preprocessing Error: {e}")
            return None
