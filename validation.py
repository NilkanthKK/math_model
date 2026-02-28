import os
import cv2
from PIL import Image, UnidentifiedImageError
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def validate_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError("Image file not found at given path")

    try:
        # corruption check
        with Image.open(image_path) as img:
            img.verify()

        # reload with cv2
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        if img is None:
            raise ValueError("Invalid image file format or unreadable image")

        # --- Resolution Check ---
        h, w = gray.shape
        if h < 400 or w < 400:
            raise ValueError("Image resolution too low or cropped. Please upload a clear invoice image")

        # --- Blur Detection ---
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        if variance < 500:
            raise ValueError("Image too blurry. Please upload a clear image")

        # --- Aspect Ratio Check ---
        aspect_ratio = w / h
        if aspect_ratio < 0.4 or aspect_ratio > 2.5:
            raise ValueError("Image seems cropped/tilted. Please upload a proper full invoice image")

        # --- OCR Text Extraction ---
        text_data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        n_boxes = len(text_data['level'])

        # find text bounding boxes
        text_boxes = []
        for i in range(n_boxes):
            (x, y, bw, bh, text) = (text_data['left'][i], text_data['top'][i], 
                                    text_data['width'][i], text_data['height'][i], text_data['text'][i])
            if text.strip() != "":
                text_boxes.append((x, y, bw, bh))

        if not text_boxes:
            raise ValueError("No readable text found in invoice. Please upload proper bill image")

        # --- Check if text is cut at edges ---
        margin = 20  # px tolerance
        for (x, y, bw, bh) in text_boxes:
            if x <= margin or y <= margin or (x + bw) >= (w - margin) or (y + bh) >= (h - margin):
                raise ValueError("Invoice data seems cut at edges. Please upload full invoice image")

    except UnidentifiedImageError:
        raise ValueError("Invalid image file format or unreadable image")

    except Exception as e:
        raise ValueError(f"Image validation failed: {str(e)}")

