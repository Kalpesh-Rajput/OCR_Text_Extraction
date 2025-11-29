# import cv2
# import numpy as np

# class Preprocessor:
#     def __init__(self):
#         pass

#     def load_image(self, image_path):
#         image = cv2.imread(image_path)
#         if image is None:
#             raise FileNotFoundError(f"Error: Unable to load image: {image_path}")
#         return image

#     def to_gray(self, img):
#         return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     def denoise(self, img):
#         return cv2.GaussianBlur(img, (5, 5), 0)

#     def enhance_contrast(self, img):
#         clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
#         return clahe.apply(img)

#     def thresholding(self, img):
#         return cv2.adaptiveThreshold(
#             img, 255,
#             cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#             cv2.THRESH_BINARY,
#             31, 2
#         )

#     def resize(self, img, scale=1.5):
#         h, w = img.shape[:2]
#         return cv2.resize(img, (int(w * scale), int(h * scale)))

#     def _rotate_bound(self, image, angle):
#         """
#         Rotate image without cropping by expanding the canvas (imutils.rotate_bound behaviour).
#         """
#         (h, w) = image.shape[:2]
#         (cX, cY) = (w // 2, h // 2)

#         # rotation matrix
#         M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
#         cos = np.abs(M[0, 0])
#         sin = np.abs(M[0, 1])

#         # compute new bounding dimensions
#         nW = int((h * sin) + (w * cos))
#         nH = int((h * cos) + (w * sin))

#         # adjust rotation matrix to account for translation
#         M[0, 2] += (nW / 2) - cX
#         M[1, 2] += (nH / 2) - cY

#         rotated = cv2.warpAffine(image, M, (nW, nH), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
#         return rotated

#     def _deskew(self, image):
#         try:
#             # Add padding so near-edge text is preserved during threshold/deskew
#             pad = 60  # pixels; increase if your labels are very close to borders
#             image = cv2.copyMakeBorder(image, pad, pad, pad, pad, borderType=cv2.BORDER_REPLICATE)

#             gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#             blur = cv2.GaussianBlur(gray, (9, 9), 0)
#             # use a binary inverse so text becomes white (consistent with later steps)
#             thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

#             # guard: if thresh is empty, return original (avoid exceptions)
#             if thresh is None or thresh.size == 0:
#                 return image

#             coords = np.column_stack(np.where(thresh > 0))
#             if coords.size == 0:
#                 return image

#             angle = cv2.minAreaRect(coords)[-1]
#             if angle < -45:
#                 angle = -(90 + angle)
#             else:
#                 angle = -angle

#             rotated = self._rotate_bound(image, angle)
#             return rotated

#         except Exception as e:
#             print(f"[Preprocessor] Deskew failed: {e}")
#             return image  # fallback → return original image

#     def preprocess(self, image_path):
#         """
#         Load, pad, deskew (without cropping), denoise, enhance contrast,
#         threshold, and perform morphology. Returns processed image OR None.
#         """
#         try:
#             img = cv2.imread(image_path)
#             if img is None:
#                 print(f"[Preprocessor] Failed to load image: {image_path}")
#                 return None

#             # STEP 1: Deskew with padding and rotate-bound (prevents cropping)
#             img = self._deskew(img)

#             # STEP 2: Convert to grayscale
#             gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#             # STEP 3: CLAHE (contrast)
#             clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
#             enhanced = clahe.apply(gray)

#             # STEP 4: Adaptive threshold (text becomes white)
#             thresh = cv2.adaptiveThreshold(
#                 enhanced, 255,
#                 cv2.ADAPTIVE_THRESH_MEAN_C,
#                 cv2.THRESH_BINARY_INV,
#                 31, 10
#             )

#             # STEP 5: Morphology – close gaps and reduce small holes
#             kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
#             morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)

#             # Optional: trim extreme border padding if you want (keeps text intact)
#             return morph

#         except Exception as e:
#             print(f"[Preprocessor] Error during preprocessing: {e}")
#             return None
        
        
##################################################################
import cv2
import numpy as np

class Preprocessor:
    def __init__(self):
        pass

    def _rotate_bound(self, image, angle):
        """
        Rotate image without cropping by expanding canvas.
        """
        (h, w) = image.shape[:2]
        (cX, cY) = (w // 2, h // 2)

        M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])

        nW = int((h * sin) + (w * cos))
        nH = int((h * cos) + (w * sin))

        M[0, 2] += (nW / 2) - cX
        M[1, 2] += (nH / 2) - cY

        rotated = cv2.warpAffine(
            image, M, (nW, nH),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return rotated

    def _deskew(self, image):
        """
        Deskew with padding + rotate-bound to prevent corner cropping.
        """
        try:
            pad = 80  # increase padding to avoid corner cropping
            image = cv2.copyMakeBorder(
                image, pad, pad, pad, pad,
                borderType=cv2.BORDER_REPLICATE
            )

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (9, 9), 0)

            thresh = cv2.threshold(
                blur, 0, 255,
                cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
            )[1]

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
        """
        Full preprocessing pipeline: load → deskew → enhance → threshold → morphology.
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                print(f"[Preprocessor] Failed to load image: {image_path}")
                return None

            # 1. Deskew with safe padding and rotate-bound
            img = self._deskew(img)

            # 2. Grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # 3. CLAHE contrast enhancement
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # 4. Adaptive threshold for uneven lighting
            thresh = cv2.adaptiveThreshold(
                enhanced, 255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY_INV,
                31, 10
            )

            # 5. Morphology to strengthen text
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            morph = cv2.morphologyEx(
                thresh, cv2.MORPH_CLOSE,
                kernel, iterations=2
            )

            return morph

        except Exception as e:
            print(f"[Preprocessor] Error during preprocessing: {e}")
            return None

