#!/usr/bin/env python3
import ollama
import json
import base64
import time
from PIL import Image
import io

# ---------------- CONFIG ----------------
MODEL = "llama3.2-vision"
MAX_IMG_SIZE = 1024   # resize large images for speed
JPEG_QUALITY = 80

# ---------------- PROMPT ----------------
SYSTEM_PROMPT = "You are a document understanding AI that reads invoices and converts them into structured JSON."

USER_PROMPT = """
Read this GST invoice image and convert its visible content into structured JSON.

Important:
Only read what is visible in the image
Do not guess missing values
Keep values exactly as written
Return only JSON
Extract ALL line items present in the invoice table
"items" array should contain one object per row dynamically
Do NOT limit number of items

Use this schema:

{
  "seller": {"name": "", "gstin": "", "address": "", "mobile": ""},
  "buyer": {"name": "", "gstin": "", "address": "", "mobile": ""},
  "invoice_details": {
    "bill_number": "",
    "bill_date": "",
    "due_date": "",
    "place_of_supply": ""
  },
  "items": [
    {
      "item_name": "",
      "quantity": "",
      "rate": "",
      "total": ""
    }
  ],
  "total_items": "",
  "taxable_amount": "",
  "tax_amount": "",
  "grand_total": "",
  "outstanding_amount": ""
}
"""
# ---------------- IMAGE PREPROCESS ----------------
def prepare_image(path):
    img = Image.open(path)

    # resize for speed
    w, h = img.size
    scale = min(MAX_IMG_SIZE / max(w, h), 1.0)
    img = img.resize((int(w * scale), int(h * scale)))

    if img.mode != "RGB":
        img = img.convert("RGB")

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)

    return base64.b64encode(buf.getvalue()).decode()

# ---------------- JSON CLEAN ----------------
def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None
    candidate = text[start:end+1]

    # remove markdown if exists
    candidate = candidate.replace("json", "").replace("", "").strip()
    return candidate

# ---------------- MAIN CALL ----------------
def run_invoice_extraction(image_path):

    image_b64 = prepare_image(image_path)

    start = time.time()

    stream = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_PROMPT, "images": [image_b64]},
        ],
        options={
            "temperature": 0,
            "num_predict": 1500,
            "num_ctx": 4096
        },
        stream=True
    )

    full_text = ""
    open_braces = 0

    for chunk in stream:
        part = chunk["message"]["content"]
        print(part, end="", flush=True)

        full_text += part
        open_braces += part.count("{") - part.count("}")

        # stop early when JSON complete
        if open_braces == 0 and "{" in full_text:
            break

    elapsed = time.time() - start

    print("\n\n---- PARSED JSON ----")

    json_text = extract_json(full_text)

    if not json_text:
        print("❌ JSON not detected")
        return

    try:
        data = json.loads(json_text)
        print(json.dumps(data, indent=2))
    except Exception as e:
        print("❌ JSON parse error:", e)
        print(json_text)

    print(f"\n⏱ Response Time: {elapsed:.2f} sec")


# ---------------- RUN ----------------
if __name__ == "__main__":
    image_path = r"C:\Users\Hello\Desktop\Images\7.jpeg"
    run_invoice_extraction(image_path)
