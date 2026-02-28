# """
# 100% VISION BASED
# INVOICE EXTRACTOR - CONSOLE OUTPUT ONLY
# MODEL: llama3.2-vision:11b
# """

# import ollama
# import json
# import base64
# import re
# from PIL import Image
# import io
# import os
# from pathlib import Path
# import time


# # ==================== CONFIGURATION ====================
# MODEL = "llama3.2-vision:11b"

# IMAGE_PATH = r"C:\Users\Hello\Desktop\koffeekodes_invoice_bill\6.jpeg"

# # ==================== PROMPTS ====================

# SYSTEM_PROMPT = """
# You are a highly accurate Indian GST invoice parser.

# Important extraction rules:

# 1. Buyer name is usually under:
#    - "Bill To"
#    - "Ship To"
#    - "Billed To"

# 2. The FIRST line immediately below "Bill To" or "Ship To"
#    should be considered the buyer name.

# 3. Do NOT leave buyer.name empty if visible.

# 4. Extract GST numbers carefully:
#    Format: 2 digits + 10 alphanumeric + 1 digit + Z + 1 alphanumeric

# 5. Extract tax amounts exactly as printed.
#    Do not calculate totals.

# Return ONLY valid JSON.
# No explanation.
# No markdown.
# No guessing.
# """

# USER_PROMPT = """
# Extract complete invoice data from this image.

# FIELDS:

# 1. SELLER:
# - name
# - gstin
# - address
# - mobile

# 2. BUYER:
# - name
# - gstin
# - address
# - mobile

# 3. INVOICE:
# - number
# - date
# - due_date
# - place_of_supply

# 4. ITEMS (extract ALL rows):
# - description
# - hsn_code
# - quantity
# - rate
# - amount

# 5. TAX DETAILS:
# - cgst_rate
# - cgst_amount
# - sgst_rate
# - sgst_amount
# - igst_rate
# - igst_amount
# - total_tax_amount

# 6. TOTALS:
# - subtotal
# - taxable_amount
# - grand_total
# - outstanding

# Return STRICT JSON in this format:

# {
#   "seller": {"name":"","gstin":"","address":"","mobile":""},
#   "buyer": {"name":"","gstin":"","address":"","mobile":""},
#   "invoice": {"number":"","date":"","due_date":"","place_of_supply":""},
#   "items": [
#     {"description":"","hsn_code":"","quantity":"","rate":"","amount":""}
#   ],
#   "tax_details": {
#     "cgst_rate":"",
#     "cgst_amount":"",
#     "sgst_rate":"",
#     "sgst_amount":"",
#     "igst_rate":"",
#     "igst_amount":"",
#     "total_tax_amount":""
#   },
#   "totals": {
#     "subtotal":"",
#     "taxable_amount":"",
#     "grand_total":"",
#     "outstanding":""
#   }
# }
# """

# # ==================== IMAGE ENCODING ====================

# def encode_image(image_path, max_size=1024, quality=85):
#     try:
#         img = Image.open(image_path)

#         if img.mode != "RGB":
#             img = img.convert("RGB")

#         w, h = img.size

#         if max(w, h) > max_size:
#             scale = max_size / max(w, h)
#             img = img.resize(
#                 (int(w * scale), int(h * scale)),
#                 Image.Resampling.LANCZOS
#             )

#         buffer = io.BytesIO()
#         img.save(buffer, format="JPEG", quality=quality, optimize=True)

#         return base64.b64encode(buffer.getvalue()).decode()

#     except Exception as e:
#         print(f"❌ Image processing error: {e}")
#         return None


# # ==================== JSON EXTRACTION ====================

# def extract_json(text):
#     text = re.sub(r"```json", "", text)
#     text = re.sub(r"```", "", text)

#     start = text.find("{")
#     end = text.rfind("}")

#     if start == -1 or end == -1:
#         return None

#     json_str = text[start:end + 1]

#     try:
#         return json.loads(json_str)
#     except:
#         return None


# # ==================== VISION CALL ====================

# def call_vision_model(image_b64):
#     try:
#         response = ollama.chat(
#             model=MODEL,
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user", "content": USER_PROMPT, "images": [image_b64]}
#             ],
#             options={
#                 "temperature": 0,
#                 "top_p": 0.9,
#                 "num_predict": 2048
#             }
#         )

#         print("Model RESPONSE \n ----------------------->",response["message"]["content"])
#         return response["message"]["content"]

#     except Exception as e:
#         print(f"❌ Model error: {e}")
#         return None


# # ==================== STRUCTURE VALIDATION ====================

# def validate_structure(data):
#     template = {
#         "seller": {"name":"","gstin":"","address":"","mobile":""},
#         "buyer": {"name":"","gstin":"","address":"","mobile":""},
#         "invoice": {"number":"","date":"","due_date":"","place_of_supply":""},
#         "items": [],
#         "totals": {
#             "subtotal":"",
#             "taxable_amount":"",
#             "tax_amount":"",
#             "grand_total":"",
#             "outstanding":""
#         }
#     }

#     for key in template:
#         if key not in data:
#             data[key] = template[key]

#     return data


# # ==================== MAIN PROCESS ====================

# def process_invoice(image_path):
#     print("="*60)
#     print("🧾 VISION INVOICE EXTRACTOR")
#     print("="*60)

#     if not os.path.exists(image_path):
#         print("❌ Image not found")
#         return None

#     print(f"📄 Processing: {os.path.basename(image_path)}")

#     image_b64 = encode_image(image_path)
#     if not image_b64:
#         return None

#     print("🔍 Calling llama3.2-vision:11b ...")

#     response = call_vision_model(image_b64)
#     if not response:
#         return None

#     data = extract_json(response)
#     if not data:
#         print("❌ Invalid JSON from model")
#         return None

#     print("✅ Extraction Successful")
#     return validate_structure(data)


# # ==================== RUN ====================

# if __name__ == "__main__":
#     start_time = time.time()

#     image_path = Path(IMAGE_PATH)

#     result = process_invoice(str(image_path))

#     print("\n" + "="*60)

#     if result:
#         print("📦 FINAL JSON OUTPUT:\n")
#         print(json.dumps(result, indent=2, ensure_ascii=False))
#         print("\n✨ Done (Console Only)")
#     else:
#         print("❌ Failed to extract invoice")

#     # time the response
#     end_time = time.time() 
#     elapsed = end_time - start_time
#     print("Finel Time ",elapsed)


"""
STRICT JSON VISION INVOICE EXTRACTOR
MODEL: llama3.2-vision:11b
Console Output Only
"""

import ollama
import json
import base64
import re
from PIL import Image
import io
import os
from pathlib import Path
import time

# ==================== CONFIG ====================

MODEL = "llama3.2-vision:11b"
# MODEL = "llava:34b"
IMAGE_PATH = r"C:\Users\Hello\Desktop\koffeekodes_invoice_bill\17.jpeg"

# ==================== STRICT PROMPTS ====================

SYSTEM_PROMPT = """
You are a strict JSON API.

You must ONLY return valid JSON.
Do NOT explain.
Do NOT describe.
Do NOT summarize.
Do NOT use markdown.
Do NOT write text before or after JSON.

If output is not valid JSON, the system will fail.

Always return a single JSON object.
"""

# USER_PROMPT = """
# You are a production-grade GST invoice OCR extraction engine.

# STRICT JSON MODE.
# NO explanation.
# NO markdown.
# NO extra text.

# If a value is not clearly visible, return "".

# ===============================
# EXTRACT THE FOLLOWING FIELDS
# ===============================

# SELLER (Top Company Block)
# - seller.name → Company name at top
# - seller.gstin → 15 character GSTIN only
# - seller.address → Full address under seller
# - seller.mobile → Only if clearly labeled

# BUYER (Under "Bill To" or "Buyer")
# - buyer.name
# - buyer.gstin (15 character only)
# - buyer.address
# - buyer.mobile

# INVOICE DETAILS
# - invoice.number → Invoice No
# - invoice.date → Invoice Date
# - invoice.due_date → Due Date if present
# - invoice.place_of_supply → If clearly printed

# ITEM TABLE
# Extract rows between header and Total row.

# Header must contain any of:
# Description | HSN | SAC | Qty | Rate | Amount

# For each row return:
# - description
# - hsn_code (numbers only)
# - quantity
# - rate
# - amount

# Rules:
# • Do NOT include tax rows
# • Do NOT include discount rows
# • Skip corrupted rows
# • Max 50 rows
# • If unreadable → return []

# TAX DETAILS (From tax summary only)
# - cgst_rate
# - cgst_amount
# - sgst_rate
# - sgst_amount
# - igst_rate
# - igst_amount
# - total_tax_amount

# TOTALS (Bottom Section Only)
# - subtotal
# - taxable_amount
# - grand_total (final bottom-most Total)
# - outstanding (if labeled Balance or Outstanding)

# ===============================
# RETURN STRICT JSON
# ===============================

# {
#   "seller": {"name":"","gstin":"","address":"","mobile":""},
#   "buyer": {"name":"","gstin":"","address":"","mobile":""},
#   "invoice": {"number":"","date":"","due_date":"","place_of_supply":""},
#   "items": [],
#   "tax_details": {
#     "cgst_rate":"",
#     "cgst_amount":"",
#     "sgst_rate":"",
#     "sgst_amount":"",
#     "igst_rate":"",
#     "igst_amount":"",
#     "total_tax_amount":""
#   },
#   "totals": {
#     "subtotal":"",
#     "taxable_amount":"",
#     "grand_total":"",
#     "outstanding":""
#   }
# }
# """

USER_PROMPT = """
You are reading a GST invoice image.

STRICT EXTRACTION RULES:

1. Extract text EXACTLY as printed.
2. If value not visible, return empty string "".
3. Never write 'Not provided'.
4. Never explain.
5. Never calculate any value.
6. Always extract final TOTAL from the bottom "Total" row.
7. If Discount row exists, subtract is already reflected in Total. Do NOT calculate.

FIELD LOCATION RULES:

SELLER:
- Seller name = top center large text (company name)
- GSTIN = text starting with GSTIN:
- Mobile = text starting with Mobile:

BUYER:
- Buyer name = first line under "Billing Details"
- Buyer GSTIN = GSTIN under Billing Details

INVOICE:
- number = value next to "Invoice Number"
- date = value next to "Invoice Date"
- due_date = value next to "Due date"

ITEM TABLE:
Extract from row under headers:
Sr | Item Description | HSN/SAC | Qty | List Price | Disc | Tax % | Amount


- description = Item Description column
- hsn_code = HSN/SAC column
- quantity = Qty column
- rate = List Price column
- amount = Amount column

TOTALS:
- subtotal = before discount if visible
- grand_total = value in bottom "Total" row
- outstanding = value next to "Invoice Balance"

Return ONLY this JSON:

{
  "seller": {"name":"","gstin":"","address":"","mobile":""},
  "buyer": {"name":"","gstin":"","address":"","mobile":""},
  "invoice": {"number":"","date":"","due_date":"","place_of_supply":""},
  "items": [
    {"description":"","hsn_code":"","quantity":"","rate":"","amount":""}
  ],
  "tax_details": {
    "cgst_rate":"",
    "cgst_amount":"",
    "sgst_rate":"",
    "sgst_amount":"",
    "igst_rate":"",
    "igst_amount":"",
    "total_tax_amount":""
  },
  "totals": {
    "subtotal":"",
    "taxable_amount":"",
    "grand_total":"",
    "outstanding":""
  }
}
"""

# ==================== IMAGE ENCODE ====================

def encode_image(image_path, max_size=768, quality=80):
    try:
        img = Image.open(image_path)

        if img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size

        if max(w, h) > max_size:
            scale = max_size / max(w, h)
            img = img.resize(
                (int(w * scale), int(h * scale)),
                Image.Resampling.LANCZOS
            )

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)

        return base64.b64encode(buffer.getvalue()).decode()

    except Exception as e:
        print(f"❌ Image processing error: {e}")
        return None


# ==================== STRONG JSON EXTRACTION ====================

def extract_json(text):
    # Try direct JSON parse
    try:
        return json.loads(text)
    except:
        pass

    # Remove markdown if exists
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Extract first JSON block
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except:
            pass

    print("⚠️ Model did not return valid JSON.")
    return None


# ==================== MODEL CALL ====================

def call_model(image_b64):
    try:
        response = ollama.chat(
            model=MODEL,
            format="json",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT, "images": [image_b64]}
            ],
            options={
                "temperature": 0,
                "top_p": 0.8,
                "num_predict": 1500
            }
        )

        print("response----------------\n",response["message"]["content"])
        return response["message"]["content"]

    except Exception as e:
        print(f"❌ Model error: {e}")
        return None


# ==================== STRUCTURE VALIDATION ====================

def validate_structure(data):
    template = {
        "seller": {"name":"","gstin":"","address":"","mobile":""},
        "buyer": {"name":"","gstin":"","address":"","mobile":""},
        "invoice": {"number":"","date":"","due_date":"","place_of_supply":""},
        "items": [],
        "tax_details": {
            "cgst_rate":"",
            "cgst_amount":"",
            "sgst_rate":"",
            "sgst_amount":"",
            "igst_rate":"",
            "igst_amount":"",
            "total_tax_amount":""
        },
        "totals": {
            "subtotal":"",
            "taxable_amount":"",
            "grand_total":"",
            "outstanding":""
        }
    }

    for key in template:
        if key not in data:
            data[key] = template[key]

    return data


# ==================== MAIN PROCESS ====================

def process_invoice(image_path):
    print("="*60)
    print("🧾 STRICT JSON VISION INVOICE EXTRACTOR")
    print("="*60)

    if not os.path.exists(image_path):
        print("❌ Image not found")
        return None

    print(f"📄 Processing: {os.path.basename(image_path)}")

    image_b64 = encode_image(image_path)
    if not image_b64:
        return None

    print("🔍 Calling llama3.2-vision:11b ...")

    response = call_model(image_b64)
    if not response:
        return None

    data = extract_json(response)
    if not data:
        print("❌ Invalid JSON from model")
        return None

    return validate_structure(data)


# ==================== RUN ====================

if __name__ == "__main__":
    start_time = time.time()

    image_path = Path(IMAGE_PATH)
    result = process_invoice(str(image_path))

    print("\n" + "="*60)

    if result:
        print("📦 FINAL JSON OUTPUT:\n")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print("\n✨ Done (Console Only)")
    else:
        print("❌ Failed to extract invoice")

    print("\n⏱ Total Time:", round(time.time() - start_time, 2), "seconds")


