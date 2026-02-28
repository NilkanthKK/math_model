import os
import json
import time
from paddleocr import PaddleOCR
import ollama

os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"
os.environ["OMP_NUM_THREADS"] = "1"

# ---------------------------
# OCR INIT
# ---------------------------
ocr = PaddleOCR(lang='en', use_angle_cls=True)

# ---------------------------
# OCR TEXT EXTRACTION
# ---------------------------
def extract_text_from_image(image_path):
    result = ocr.ocr(image_path)

    extracted_text = ""
    for line in result[0]:
        extracted_text += line[1][0] + "\n"

    return extracted_text


# ---------------------------
# LLM STRUCTURED EXTRACTION
# ---------------------------
def extract_structured_data(text):

    prompt = f"""
You are an expert invoice data extractor.

Return ONLY valid JSON.
No explanation.
No markdown.
No extra text.

Invoice Text:
{text}
"""

    start_time = time.time()

    response = ollama.chat(
        model="minicpm-v",
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0}
    )

    end_time = time.time()
    response_time = round(end_time - start_time, 2)

    content = response["message"]["content"].strip()

    print("\n🚀 Processing Invoice...")
    
    try:
        structured = json.loads(content)
        print("\n✅ Extracted JSON:\n")
        print(json.dumps(structured, indent=2))
    except:
        print("\n⚠ JSON parsing failed.")
        print("\n📄 Raw Model Output:\n")
        print(content)

    print(f"\n⏱ Response Time: {response_time} seconds")


# # ---------------------------
# # MAIN
# # ---------------------------
# if __name__ == "__main__":

#     image_path = r"C:\Users\Hello\Desktop\koffeekodes_invoice_bill\1.jpeg"

#     print("Extracting text from image...")
#     text = extract_text_from_image(image_path)

#     extract_structured_data(text)


from pathlib import Path

# ---------------------------
# MAIN
# ---------------------------
if __name__ == "__main__":

    folder_path = Path(r"C:\Users\Hello\Desktop\koffeekodes_invoice_bill")

    # Supported image extensions
    image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]

    print("Scanning folder for images...")

    # Loop through all images in folder
    for image_path in folder_path.iterdir():
        if image_path.suffix.lower() in image_extensions:

            print(f"\nProcessing: {image_path.name}")

            text = extract_text_from_image(str(image_path))
            extract_structured_data(text)

    print("\nAll images processed successfully ✅")