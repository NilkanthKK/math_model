"""
INVOICE EXTRACTOR - FINAL VERSION
FREE | LOCAL | 500+ images/day | JSON Output
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
IMAGE_PATH = r"C:\Users\Hello\Desktop\koffeekodes_invoice_bill\1.jpeg"
OUTPUT_FOLDER = "extracted_data"

# Create output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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
    """
    Convert image to base64 with optimization
    """
    try:
        # Open image
        img = Image.open(image_path)
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large (faster processing)
        w, h = img.size
        if max(w, h) > max_size:
            scale = max_size / max(w, h)
            new_size = (int(w * scale), int(h * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"📐 Resized: {w}x{h} → {new_size[0]}x{new_size[1]}")
        
        # Compress
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        
        # Encode
        encoded = base64.b64encode(buffer.getvalue()).decode()
        print(f"📦 Image size: {len(encoded) / 1024:.1f} KB")
        
        return encoded
        
    except Exception as e:
        print(f"❌ Image error: {e}")
        return None

# ==================== JSON EXTRACTION ====================
def extract_json_from_text(text):
    """
    Extract valid JSON from model response
    """
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
        json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
        json_str = re.sub(r',\s*]', ']', json_str)
        try:
            json.loads(json_str)
            return json_str
        except:
            return None

# ==================== LLM CALL ====================
def call_vision_model(image_base64):
    """
    Call llama3.2-vision with image
    """
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
    """
    Fallback: Use text model if vision fails
    """
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
    """
    Use PaddleOCR as last resort
    """
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

# ==================== MAIN PROCESSING ====================
def process_invoice(image_path):
    """
    Complete invoice processing pipeline
    """
    print("\n" + "="*60)
    print("🧾 INVOICE EXTRACTOR - FINAL VERSION")
    print("="*60)
    
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        return None
    
    print(f"\n📄 Processing: {os.path.basename(image_path)}")
    start_time = datetime.now()
    
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
                    
                    # Validate items array
                    if 'items' in data and len(data['items']) > 0:
                        print(f"📊 Found {len(data['items'])} items")
                    
                    return data
                except:
                    print("⚠️ Vision model returned invalid JSON")
    
    # Step 2: Try Text Model with OCR
    print("\n🔍 Step 2: Trying text model with OCR...")
    ocr_text = extract_text_with_paddle(image_path)
    
    if ocr_text:
        print(f"📝 OCR extracted: {len(ocr_text)} chars")
        response = call_text_model(ocr_text[:3000])  # Limit length
        
        if response:
            json_str = extract_json_from_text(response)
            
            if json_str:
                try:
                    data = json.loads(json_str)
                    print("✅ Text model successful!")
                    
                    if 'items' in data and len(data['items']) > 0:
                        print(f"📊 Found {len(data['items'])} items")
                    
                    return data
                except:
                    pass
    
    # Step 3: Manual extraction (if both fail)
    print("\n🔍 Step 3: Manual extraction...")
    manual_data = {
        "seller": {"name": "", "gstin": "", "address": "", "mobile": ""},
        "buyer": {"name": "", "gstin": "", "address": "", "mobile": ""},
        "invoice": {"number": "", "date": "", "due_date": "", "place_of_supply": ""},
        "items": [],
        "totals": {"subtotal": "", "taxable_amount": "", "tax_amount": "", "grand_total": "", "outstanding": ""}
    }
    
    # Try to extract GST number from OCR
    if ocr_text:
        gst_pattern = r'\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d[Z]{1}[A-Z\d]{1}'
        gst_match = re.search(gst_pattern, ocr_text)
        if gst_match:
            manual_data["seller"]["gstin"] = gst_match.group()
        
        # Try to find total
        total_pattern = r'(?:total|grand total|amount)[:\s]*[₹]?\s*([\d,]+\.?\d*)'
        total_match = re.search(total_pattern, ocr_text, re.IGNORECASE)
        if total_match:
            manual_data["totals"]["grand_total"] = total_match.group(1).replace(',', '')
    
    print("⚠️ Using manual extraction (limited data)")
    return manual_data

# ==================== SAVE RESULTS ====================
def save_results(data, image_path):
    """
    Save extracted data to JSON file
    """
    if not data:
        return
    
    # Create filename
    base_name = os.path.basename(image_path)
    name_without_ext = os.path.splitext(base_name)[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    json_filename = f"{name_without_ext}_{timestamp}.json"
    json_path = os.path.join(OUTPUT_FOLDER, json_filename)
    
    # Add metadata
    output_data = {
        "metadata": {
            "source_file": base_name,
            "processed_at": timestamp,
            "model_used": MODEL
        },
        "extracted_data": data
    }
    
    # Save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved to: {json_path}")
    return json_path

# ==================== DISPLAY RESULTS ====================
def display_results(data):
    """
    Pretty print the extracted data
    """
    print("\n" + "="*60)
    print("✅ EXTRACTION RESULTS")
    print("="*60)
    
    # Seller
    if data.get('seller'):
        print(f"\n🏢 SELLER:")
        print(f"   Name: {data['seller'].get('name', '')}")
        print(f"   GST: {data['seller'].get('gstin', '')}")
        print(f"   Address: {data['seller'].get('address', '')[:50]}...")
    
    # Buyer
    if data.get('buyer'):
        print(f"\n👤 BUYER:")
        print(f"   Name: {data['buyer'].get('name', '')}")
        print(f"   GST: {data['buyer'].get('gstin', '')}")
    
    # Invoice
    if data.get('invoice'):
        print(f"\n📋 INVOICE:")
        print(f"   Number: {data['invoice'].get('number', '')}")
        print(f"   Date: {data['invoice'].get('date', '')}")
    
    # Items
    if data.get('items') and len(data['items']) > 0:
        print(f"\n📦 ITEMS ({len(data['items'])}):")
        for i, item in enumerate(data['items'][:5]):  # Show first 5
            print(f"   {i+1}. {item.get('description', '')[:30]} - "
                  f"Qty: {item.get('quantity', '')} - "
                  f"Rate: {item.get('rate', '')} - "
                  f"Amt: {item.get('amount', '')}")
        if len(data['items']) > 5:
            print(f"   ... and {len(data['items'])-5} more items")
    
    # Totals
    if data.get('totals'):
        print(f"\n💰 TOTALS:")
        print(f"   Taxable: {data['totals'].get('taxable_amount', '')}")
        print(f"   Tax: {data['totals'].get('tax_amount', '')}")
        print(f"   Grand Total: {data['totals'].get('grand_total', '')}")
    
    print("\n" + "="*60)

# ==================== MAIN ====================
if __name__ == "__main__":
    # Process invoice
    extracted_data = process_invoice(IMAGE_PATH)
    
    if extracted_data:
        # Display
        display_results(extracted_data)
        
        # Save
        save_results(extracted_data, IMAGE_PATH)
        
        print("\n✨ Processing complete!")
    else:
        print("\n❌ Failed to extract data from invoice")

# ==================== BATCH PROCESSING ====================
def process_multiple_invoices(folder_path):
    """
    Process all images in a folder
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.pdf'}
    
    images = [f for f in os.listdir(folder_path) 
              if os.path.splitext(f)[1].lower() in image_extensions]
    
    print(f"\n📁 Found {len(images)} images in {folder_path}")
    
    results = []
    for i, img in enumerate(images, 1):
        print(f"\n{'='*60}")
        print(f"Processing {i}/{len(images)}: {img}")
        
        img_path = os.path.join(folder_path, img)
        data = process_invoice(img_path)
        
        if data:
            save_results(data, img_path)
            results.append({"image": img, "status": "success"})
        else:
            results.append({"image": img, "status": "failed"})
    
    # Summary
    print("\n" + "="*60)
    print("📊 BATCH PROCESSING SUMMARY")
    print("="*60)
    successful = sum(1 for r in results if r['status'] == 'success')
    print(f"Total: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(results) - successful}")
    
    return results

# Uncomment to process multiple files:
# process_multiple_invoices(r"C:\Users\Admin\Documents\Model_test\images\2.jpeg")