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

    def _deskew(self, image):
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (9, 9), 0)
            thresh = cv2.threshold(
                blur, 0, 255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )[1]

            coords = np.column_stack(np.where(thresh > 0))
            angle = cv2.minAreaRect(coords)[-1]

            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated

        except Exception as e:
            print(f"[Preprocessor] Deskew failed: {e}")
            return image  # fallback → return original image

    def preprocess(self, image_path):
        """
        Load, deskew, denoise, enhance contrast, threshold, and perform morphology.
        Returns processed image OR None if failure.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                print(f"[Preprocessor] Failed to load image: {image_path}")
                return None

            # STEP 1: Deskew
            img = self._deskew(img)

            # STEP 2: Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # STEP 3: CLAHE (improves contrast 30-50%)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # STEP 4: Adaptive threshold (handles uneven lighting)
            thresh = cv2.adaptiveThreshold(
                enhanced, 255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY_INV,
                31, 10
            )

            # STEP 5: Morphology (closes small gaps in characters)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(
                thresh, cv2.MORPH_CLOSE, kernel, iterations=2
            )

            return morph

        except Exception as e:
            print(f"[Preprocessor] Error during preprocessing: {e}")
            return None
        
        
        

