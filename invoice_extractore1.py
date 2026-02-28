
"""
90%
INVOICE EXTRACTOR - CONSOLE OUTPUT ONLY (No File Save)
FREE | LOCAL | JSON Output in Console
"""

import ollama
import json
import base64
import re
from PIL import Image
import io
import os
from datetime import datetime

# ==================== CONFIGURATION ====================
MODEL = "llama3.2-vision:11b"  # Best for invoices
BACKUP_MODEL = "gemma2:9b"      # Agar vision model fail ho
# IMAGE_PATH = r"C:\Users\Hello\Desktop\Images\1.webp"
# IMAGE_PATH = r"C:\Users\Hello\Desktop\Images\2.jpg"
# IMAGE_PATH = r"C:\Users\Hello\Desktop\Images\3.jpeg"
IMAGE_PATH = r"C:\Users\Hello\Desktop\Images\8.png"

# ==================== PROMPT ENGINEERING ====================
SYSTEM_PROMPT = """You are an expert invoice parser for Indian GST invoices.
Your task is to extract ALL visible data from the invoice image and return ONLY valid JSON.
Do not add explanations. Do not add markdown. Do not add comments.
If a field is not visible, use empty string "". Never guess values."""

USER_PROMPT = """
Extract complete invoice data from this image.

FIELDS TO EXTRACT:
1. SELLER DETAILS:
   - name (company name)
   - gstin (GST number - format: 22ABCDE1234F1Z5)
   - address (full address)
   - mobile/phone

2. BUYER DETAILS:
   - name (customer name)
   - gstin (if mentioned)
   - address
   - mobile

3. INVOICE DETAILS:
   - invoice_number (bill no/invoice no)
   - invoice_date (DD/MM/YYYY)
   - due_date (if mentioned)
   - place_of_supply

4. ITEMS TABLE (MOST IMPORTANT):
   Extract ALL rows from the items table. Each item should have:
   - description (item name)
   - hsn_code (if visible)
   - quantity (numbers only)
   - rate (price per unit)
   - amount (total for this item)

5. FINANCIAL DETAILS:
   - subtotal (before tax)
   - taxable_amount
   - tax_amount (cgst+sgst/igst)
   - grand_total
   - outstanding_amount (if any)

Return in this EXACT JSON structure:
{
    "seller": {
        "name": "",
        "gstin": "",
        "address": "",
        "mobile": ""
    },
    "buyer": {
        "name": "",
        "gstin": "",
        "address": "",
        "mobile": ""
    },
    "invoice": {
        "number": "",
        "date": "",
        "due_date": "",
        "place_of_supply": ""
    },
    "items": [
        {
            "description": "",
            "hsn_code": "",
            "quantity": "",
            "rate": "",
            "amount": ""
        }
    ],
    "totals": {
        "subtotal": "",
        "taxable_amount": "",
        "tax_amount": "",
        "grand_total": "",
        "outstanding": ""
    }
}

RULES:
- Extract ALL items from the table (don't limit)
- Keep original numbers as they appear
- For GST numbers, maintain exact format
- If HSN codes visible, include them
- Return ONLY the JSON object, no other text
"""

# ==================== IMAGE PROCESSING ====================
def encode_image(image_path, max_size=1024, quality=85):
    """Convert image to base64 with optimization"""
    try:
        img = Image.open(image_path)
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        w, h = img.size
        if max(w, h) > max_size:
            scale = max_size / max(w, h)
            new_size = (int(w * scale), int(h * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"📐 Resized: {w}x{h} → {new_size[0]}x{new_size[1]}")
        
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        encoded = base64.b64encode(buffer.getvalue()).decode()
        print(f"📦 Image size: {len(encoded) / 1024:.1f} KB")
        
        return encoded
        
    except Exception as e:
        print(f"❌ Image error: {e}")
        return None

# ==================== JSON EXTRACTION ====================
def extract_json_from_text(text):
    """Extract valid JSON from model response"""
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Find JSON object
    start = text.find('{')
    end = text.rfind('}')
    
    if start == -1 or end == -1:
        return None
    
    json_str = text[start:end+1]
    
    # Basic validation
    try:
        json.loads(json_str)
        return json_str
    except:
        # Try to fix common issues
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        try:
            json.loads(json_str)
            return json_str
        except:
            return None

# ==================== LLM CALL ====================
def call_vision_model(image_base64):
    """Call llama3.2-vision with image"""
    try:
        response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT, "images": [image_base64]}
            ],
            options={
                "temperature": 0.1,
                "num_predict": 2048,
                "top_p": 0.9
            }
        )
        return response['message']['content']
    except Exception as e:
        print(f"❌ Vision model error: {e}")
        return None

def call_text_model(text):
    """Fallback: Use text model if vision fails"""
    try:
        prompt = f"{SYSTEM_PROMPT}\n\n{USER_PROMPT}\n\nOCR Text from invoice:\n{text}"
        
        response = ollama.chat(
            model=BACKUP_MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.1,
                "num_predict": 2048
            }
        )
        return response['message']['content']
    except Exception as e:
        print(f"❌ Text model error: {e}")
        return None

# ==================== FALLBACK OCR ====================
def extract_text_with_paddle(image_path):
    """Use PaddleOCR as last resort"""
    try:
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang='en', use_angle_cls=False, show_log=False)
        result = ocr.ocr(image_path)
        
        if result and result[0]:
            text = '\n'.join([line[1][0] for line in result[0]])
            return text
    except:
        pass
    return None

# ==================== CLEAN JSON FUNCTION ====================
def clean_extracted_data(data):
    """Clean and validate extracted data"""
    if not data:
        return data
    
    # Ensure all fields exist
    required_structure = {
        "seller": {"name": "", "gstin": "", "address": "", "mobile": ""},
        "buyer": {"name": "", "gstin": "", "address": "", "mobile": ""},
        "invoice": {"number": "", "date": "", "due_date": "", "place_of_supply": ""},
        "items": [],
        "totals": {"subtotal": "", "taxable_amount": "", "tax_amount": "", "grand_total": "", "outstanding": ""}
    }
    
    # Merge with existing data
    for key in required_structure:
        if key not in data:
            data[key] = required_structure[key]
        elif isinstance(required_structure[key], dict):
            for subkey in required_structure[key]:
                if subkey not in data[key]:
                    data[key][subkey] = ""
    
    return data

# ==================== MAIN PROCESSING ====================
def process_invoice(image_path):
    """Complete invoice processing pipeline"""
    print("\n" + "="*60)
    print("🧾 INVOICE EXTRACTOR - CONSOLE OUTPUT ONLY")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    print(f"\n📄 Processing: {os.path.basename(image_path)}")
    
    # Step 1: Try Vision Model (Best)
    print("\n🔍 Step 1: Trying vision model...")
    image_b64 = encode_image(image_path)
    
    if image_b64:
        response = call_vision_model(image_b64)
        
        if response:
            json_str = extract_json_from_text(response)
            
            if json_str:
                try:
                    data = json.loads(json_str)
                    print("✅ Vision model successful!")
                    return clean_extracted_data(data)
                except:
                    print("⚠️ Vision model returned invalid JSON")
    
    # Step 2: Try Text Model with OCR
    print("\n🔍 Step 2: Trying text model with OCR...")
    ocr_text = extract_text_with_paddle(image_path)
    
    if ocr_text:
        print(f"📝 OCR extracted: {len(ocr_text)} chars")
        response = call_text_model(ocr_text[:3000])
        
        if response:
            json_str = extract_json_from_text(response)
            
            if json_str:
                try:
                    data = json.loads(json_str)
                    print("✅ Text model successful!")
                    return clean_extracted_data(data)
                except:
                    pass
    
    return None
from pathlib import Path

# ==================== MAIN ====================
if __name__ == "__main__":

    image_path = Path(r"C:\Users\Hello\Desktop\koffeekodes_invoice_bill\3.jpeg")

    # for image_path in folder_path.iterdir():

    # Process invoice
    extracted_data = process_invoice(image_path)

    print("\n" + "="*60)
    print(f"\nProcessing: {image_path.name}")
    print("\n" + "="*60)

    
    if extracted_data:
        print("\n" + "="*60)
        print(" EXTRACTED JSON DATA")
        print("="*60)
        
        # Print clean JSON directly to console
        print("\n" + "="*60)
        print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
        print("\n" + "="*60)

        print("\n" + "="*60)
        print("✨ Processing complete! (No file saved)")
        print("="*60)

    else:
        print("\n❌ Failed to extract data from invoice")


