# """
# INVOICE EXTRACTOR - SIMPLIFIED WORKING VERSION
# FREE | LOCAL | Guaranteed to work
# """

# import ollama
# import json
# import base64
# import re
# from PIL import Image
# import io
# import os
# from datetime import datetime
# import time

# # ==================== CONFIGURATION ====================
# VISION_MODEL = "llama3.2-vision:11b"  # Vision model
# TEXT_MODEL = "gemma2:9b"              # Text model for backup

# # ==================== CHANGE THIS PATH ====================
# IMAGE_PATH = r"C:\Users\Hello\Desktop\Images\3.jpg"  # <-- CHANGE THIS
# # =========================================================

# # Simple prompt - kaam karega guaranteed
# SYSTEM_PROMPT = """You are an expert invoice parser. Extract all visible data and return ONLY valid JSON."""

# USER_PROMPT = """
# Extract complete invoice data from this image.

# FIELDS TO EXTRACT:
# 1. SELLER DETAILS:
#    - name (company name)
#    - gstin (GST number - format: 22ABCDE1234F1Z5)
#    - address (full address)
#    - mobile/phone

# 2. BUYER DETAILS:
#    - name (customer name)
#    - gstin (if mentioned)
#    - address
#    - mobile

# 3. INVOICE DETAILS:
#    - invoice_number (bill no/invoice no)
#    - invoice_date (DD/MM/YYYY)
#    - due_date (if mentioned)
#    - place_of_supply

# 4. ITEMS TABLE (MOST IMPORTANT):
#    Extract ALL rows from the items table. Each item should have:
#    - description (item name)
#    - hsn_code (if visible)
#    - quantity (numbers only)
#    - rate (price per unit)
#    - amount (total for this item)

# 5. FINANCIAL DETAILS:
#    - subtotal (before tax)
#    - taxable_amount
#    - tax_amount (cgst+sgst/igst)
#    - grand_total
#    - outstanding_amount (if any)

# Return in this EXACT JSON structure:
# {
#     "seller": {
#         "name": "",
#         "gstin": "",
#         "address": "",
#         "mobile": ""
#     },
#     "buyer": {
#         "name": "",
#         "gstin": "",
#         "address": "",
#         "mobile": ""
#     },
#     "invoice": {
#         "number": "",
#         "date": "",
#         "due_date": "",
#         "place_of_supply": ""
#     },
#     "items": [
#         {
#             "description": "",
#             "hsn_code": "",
#             "quantity": "",
#             "rate": "",
#             "amount": ""
#         }
#     ],
#     "totals": {
#         "subtotal": "",
#         "taxable_amount": "",
#         "tax_amount": "",
#         "grand_total": "",
#         "outstanding": ""
#     }
# }

# RULES:
# - Extract ALL items from the table (don't limit)
# - Keep original numbers as they appear
# - For GST numbers, maintain exact format
# - If HSN codes visible, include them
# - Return ONLY the JSON object, no other text
# """

# def encode_image_simple(image_path, max_size=1024):
#     """Simple image encoding"""
#     try:
#         img = Image.open(image_path)
        
#         if img.mode != 'RGB':
#             img = img.convert('RGB')
        
#         w, h = img.size
#         if max(w, h) > max_size:
#             scale = max_size / max(w, h)
#             new_size = (int(w * scale), int(h * scale))
#             img = img.resize(new_size, Image.Resampling.LANCZOS)
        
#         buffer = io.BytesIO()
#         img.save(buffer, format='JPEG', quality=85)
#         return base64.b64encode(buffer.getvalue()).decode()
#     except Exception as e:
#         print(f"❌ Image error: {e}")
#         return None

# def extract_json_simple(text):
#     """Simple JSON extraction"""
#     # Find JSON
#     start = text.find('{')
#     end = text.rfind('}')
    
#     if start == -1 or end == -1:
#         return None
    
#     json_str = text[start:end+1]
    
#     # Clean
#     json_str = re.sub(r',\s*}', '}', json_str)
#     json_str = re.sub(r',\s*]', ']', json_str)
    
#     return json_str

# def process_invoice_simple(image_path):
#     """Simple invoice processing"""
#     print("\n" + "="*60)
#     print("🧾 INVOICE EXTRACTOR - SIMPLE VERSION")
#     print("="*60)
    
#     if not os.path.exists(image_path):
#         print(f"❌ Image not found: {image_path}")
#         return None
    
#     print(f"\n📄 Processing: {os.path.basename(image_path)}")
#     start = time.time()
    
#     # Encode image
#     print("📸 Encoding image...")
#     image_b64 = encode_image_simple(image_path)
    
#     if not image_b64:
#         print("❌ Failed to encode image")
#         return None
    
#     # Call vision model
#     print(f"🤖 Calling {VISION_MODEL}...")
#     try:
#         response = ollama.chat(
#             model=VISION_MODEL,
#             messages=[
#                 {"role": "system", "content": SYSTEM_PROMPT},
#                 {"role": "user", "content": USER_PROMPT, "images": [image_b64]}
#             ],
#             options={"temperature": 0.1, "num_predict": 1024}
#         )
        
#         result = response['message']['content']
#         print(f"✅ Model responded")
        
#         # Extract JSON
#         json_str = extract_json_simple(result)
        
#         if json_str:
#             try:
#                 data = json.loads(json_str)
#                 print(f"✅ JSON extracted successfully")
                
#                 # Show time
#                 elapsed = time.time() - start
#                 print(f"⏱ Time: {elapsed:.1f} seconds")
                
#                 return data
#             except:
#                 print("❌ Invalid JSON")
#                 print(result[:200])
#         else:
#             print("❌ No JSON found")
#             print(result[:200])
            
#     except Exception as e:
#         print(f"❌ Ollama error: {e}")
#         print("\n💡 SOLUTION:")
#         print("1. Open new terminal and run: ollama serve")
#         print("2. In this terminal, run: ollama list")
#         print("3. Make sure llama3.2-vision:11b is installed")
    
#     return None

# # ==================== TEXT MODEL FALLBACK ====================
# def process_with_text_model(image_path):
#     """Fallback using text model if vision fails"""
#     print("\n🔄 Trying text model fallback...")
    
#     # Try to extract text using simple OCR
#     try:
#         import pytesseract
#         img = Image.open(image_path)
#         ocr_text = pytesseract.image_to_string(img)
        
#         if ocr_text.strip():
#             print(f"📝 OCR extracted: {len(ocr_text)} chars")
            
#             prompt = f"""
#             Extract invoice data from this OCR text.
#             Return JSON with: seller_name, seller_gst, buyer_name, buyer_gst, 
#             invoice_number, invoice_date, items array, grand_total.
            
#             OCR Text:
#             {ocr_text[:2000]}
#             """
            
#             response = ollama.chat(
#                 model=TEXT_MODEL,
#                 messages=[{"role": "user", "content": prompt}],
#                 options={"temperature": 0.1}
#             )
            
#             json_str = extract_json_simple(response['message']['content'])
#             if json_str:
#                 return json.loads(json_str)
#     except:
#         pass
    
#     return None

# # ==================== MAIN ====================
# if __name__ == "__main__":
#     print("\n🚀 STARTING INVOICE EXTRACTION")
#     print(f"📁 Image: {IMAGE_PATH}")
    
#     # First try vision model
#     data = process_invoice_simple(IMAGE_PATH)
    
#     # If vision fails, try text model
#     if not data:
#         print("\n⚠️ Vision model failed, trying text model...")
#         data = process_with_text_model(IMAGE_PATH)
    
#     # Show result
#     if data:
#         print("\n" + "="*60)
#         print("✅ EXTRACTED DATA")
#         print("="*60)
#         print(json.dumps(data, indent=2, ensure_ascii=False))
        
#         # Save to file
#         filename = f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
#         with open(filename, 'w', encoding='utf-8') as f:
#             json.dump(data, f, indent=2, ensure_ascii=False)
#         print(f"\n💾 Saved to: {filename}")
#     else:
#         print("\n❌ Failed to extract data")


"""
INVOICE EXTRACTOR - WITH HTML REPORT
Ek hi file mein: Upar Image, Neeche JSON
"""

import ollama
import json
import base64
import re
from PIL import Image
import io
import os
from datetime import datetime
import time

# ==================== CONFIGURATION ====================
VISION_MODEL = "llama3.2-vision:11b"  # Vision model
TEXT_MODEL = "gemma2:9b"              # Text model for backup

# ==================== CHANGE THIS PATH ====================
IMAGE_PATH = r"C:\Users\Hello\Desktop\koffeekodes_invoice_bill\1.jpeg"  # <-- CHANGE THIS
# =========================================================

# Simple prompt
SYSTEM_PROMPT = """You are an expert invoice parser. Extract all visible data and return ONLY valid JSON."""

USER_PROMPT = """
Extract complete invoice data from this image.

FIELDS TO EXTRACT:
1. SELLER DETAILS:
   - name (company name)
   - gstin (GST number)
   - address
   - mobile

2. BUYER DETAILS:
   - name
   - gstin
   - address
   - mobile

3. INVOICE DETAILS:
   - number
   - date
   - due_date
   - place_of_supply

4. ITEMS TABLE:
   Extract ALL rows. Each item: description, hsn_code, quantity, rate, amount

5. FINANCIAL DETAILS:
   - subtotal
   - taxable_amount
   - tax_amount
   - grand_total
   - outstanding

Return in this EXACT JSON structure:
{
    "seller": {"name": "", "gstin": "", "address": "", "mobile": ""},
    "buyer": {"name": "", "gstin": "", "address": "", "mobile": ""},
    "invoice": {"number": "", "date": "", "due_date": "", "place_of_supply": ""},
    "items": [
        {"description": "", "hsn_code": "", "quantity": "", "rate": "", "amount": ""}
    ],
    "totals": {"subtotal": "", "taxable_amount": "", "tax_amount": "", "grand_total": "", "outstanding": ""}
}
"""

def encode_image_simple(image_path, max_size=1024):
    """Simple image encoding"""
    try:
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        w, h = img.size
        if max(w, h) > max_size:
            scale = max_size / max(w, h)
            new_size = (int(w * scale), int(h * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception as e:
        print(f"❌ Image error: {e}")
        return None

def extract_json_simple(text):
    """Simple JSON extraction"""
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1:
        return None
    
    json_str = text[start:end+1]
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    return json_str

# ==================== HTML REPORT GENERATOR ====================
def create_html_report(image_path, json_data, output_filename="invoice_report.html"):
    """
    Create HTML file with:
    - Top: Invoice Image
    - Bottom: Extracted JSON
    """
    # Convert image to base64 for HTML embedding
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode()
    
    # Get image extension
    img_ext = os.path.splitext(image_path)[1][1:].lower()
    if img_ext == "jpg":
        img_ext = "jpeg"
    
    # Format JSON nicely
    json_pretty = json.dumps(json_data, indent=2, ensure_ascii=False)
    
    # HTML Template
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice Extraction Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #2c3e50;
            color: white;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .image-section {{
            margin-bottom: 30px;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
        }}
        .image-section h2 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .invoice-image {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            box-shadow: 0 0 5px rgba(0,0,0,0.1);
        }}
        .json-section {{
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
        }}
        .json-section h2 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        pre {{
            background-color: white;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }}
        .timestamp {{
            color: #666;
            font-size: 12px;
            margin-top: 10px;
        }}
        .metadata {{
            background-color: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧾 Invoice Extraction Report</h1>
            <p>Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</p>
        </div>
        
        <div class="metadata">
            <strong>File:</strong> {os.path.basename(image_path)}<br>
            <strong>Model Used:</strong> {VISION_MODEL}<br>
            <strong>Status:</strong> Success ✅
        </div>
        
        <div class="image-section">
            <h2>📷 Original Invoice Image</h2>
            <img src="data:image/{img_ext};base64,{img_base64}" class="invoice-image" alt="Invoice Image">
        </div>
        
        <div class="json-section">
            <h2>📊 Extracted JSON Data</h2>
            <pre>{json_pretty}</pre>
        </div>
        
        <div class="timestamp">
            * This report contains the original image and extracted data in structured JSON format.
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(html_template)
    
    return output_filename

def process_invoice_simple(image_path):
    """Simple invoice processing"""
    print("\n" + "="*60)
    print("🧾 INVOICE EXTRACTOR - WITH HTML REPORT")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    print(f"\n📄 Processing: {os.path.basename(image_path)}")
    start = time.time()
    
    # Encode image
    print("📸 Encoding image...")
    image_b64 = encode_image_simple(image_path)
    
    if not image_b64:
        print("❌ Failed to encode image")
        return None
    
    # Call vision model
    print(f"🤖 Calling {VISION_MODEL}...")
    try:
        response = ollama.chat(
            model=VISION_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT, "images": [image_b64]}
            ],
            options={"temperature": 0.1, "num_predict": 2048}
        )
        
        result = response['message']['content']
        print(f"✅ Model responded")
        
        # Extract JSON
        json_str = extract_json_simple(result)
        
        if json_str:
            try:
                data = json.loads(json_str)
                print(f"✅ JSON extracted successfully")
                
                # Show time
                elapsed = time.time() - start
                print(f"⏱ Time: {elapsed:.1f} seconds")
                
                return data
            except Exception as e:
                print(f"❌ Invalid JSON: {e}")
                print(result[:200])
        else:
            print("❌ No JSON found")
            print(result[:200])
            
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        print("\n💡 SOLUTION:")
        print("1. Open new terminal and run: ollama serve")
        print("2. In this terminal, run: ollama list")
        print("3. Make sure llama3.2-vision:11b is installed")
    
    return None

def process_with_text_model(image_path):
    """Fallback using text model if vision fails"""
    print("\n🔄 Trying text model fallback...")
    
    try:
        import pytesseract
        img = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(img)
        
        if ocr_text.strip():
            print(f"📝 OCR extracted: {len(ocr_text)} chars")
            
            prompt = f"""
            Extract invoice data from this OCR text.
            Return JSON with: seller, buyer, invoice details, items array, totals.
            
            OCR Text:
            {ocr_text[:2000]}
            
            Use this structure:
            {{
                "seller": {{"name": "", "gstin": "", "address": "", "mobile": ""}},
                "buyer": {{"name": "", "gstin": "", "address": "", "mobile": ""}},
                "invoice": {{"number": "", "date": "", "due_date": "", "place_of_supply": ""}},
                "items": [{{"description": "", "hsn_code": "", "quantity": "", "rate": "", "amount": ""}}],
                "totals": {{"subtotal": "", "taxable_amount": "", "tax_amount": "", "grand_total": "", "outstanding": ""}}
            }}
            """
            
            response = ollama.chat(
                model=TEXT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.1}
            )
            
            json_str = extract_json_simple(response['message']['content'])
            if json_str:
                return json.loads(json_str)
    except Exception as e:
        print(f"⚠️ Text model error: {e}")
    
    return None

# ==================== MAIN WITH HTML REPORT ====================
if __name__ == "__main__":
    print("\n🚀 STARTING INVOICE EXTRACTION WITH HTML REPORT")
    print(f"📁 Image: {IMAGE_PATH}")
    
    # Create reports directory
    reports_dir = "invoice_reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Generate filename based on image name
    base_name = os.path.splitext(os.path.basename(IMAGE_PATH))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = os.path.join(reports_dir, f"{base_name}_report_{timestamp}.html")
    json_filename = os.path.join(reports_dir, f"{base_name}_data_{timestamp}.json")
    
    # First try vision model
    data = process_invoice_simple(IMAGE_PATH)
    
    # If vision fails, try text model
    if not data:
        print("\n⚠️ Vision model failed, trying text model...")
        data = process_with_text_model(IMAGE_PATH)
    
    # Show result and create HTML report
    if data:
        print("\n" + "="*60)
        print("✅ EXTRACTED DATA")
        print("="*60)
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        # Save JSON separately
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n💾 JSON saved to: {json_filename}")
        
        # Create HTML report with image + JSON
        html_file = create_html_report(IMAGE_PATH, data, html_filename)
        print(f"📄 HTML Report created: {html_file}")
        print(f"\n🌐 Open this file in browser to see image + JSON together!")
        
    else:
        print("\n❌ Failed to extract data from invoice")
        
        # Create error report
        error_html = os.path.join(reports_dir, f"{base_name}_error_{timestamp}.html")
        with open(error_html, 'w') as f:
            f.write(f"""
            <html>
            <head><title>Error Report</title></head>
            <body>
                <h1>❌ Extraction Failed</h1>
                <p>Image: {IMAGE_PATH}</p>
                <p>Time: {datetime.now()}</p>
                <p>Could not extract data from this invoice image.</p>
            </body>
            </html>
            """)
        print(f"📄 Error report: {error_html}")