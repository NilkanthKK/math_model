import ollama
import re
import json
import time
import os
import uuid
from flask import send_from_directory
from validation import validate_image
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return send_from_directory("static", "index2.html")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/extract-invoice", methods=["POST"])
def extract_invoice():

    try:
        image_path = None

        if "image" in request.files:
            image_file = request.files["image"]
            ext = os.path.splitext(image_file.filename)[1]
            unique_name = f"{uuid.uuid4().hex}{ext}"
            save_path = os.path.join(UPLOAD_FOLDER, unique_name)

            image_file.save(save_path)
            image_path = save_path

        if not image_path:
            return jsonify({"status": "fail", "message": "image (form-data) or image_path (JSON) is required"}), 400

        # validate image
        validate_image(image_path)

        # prompt = "From this invoice, I need the party name, party address, party GST number, invoice amount, taxable amount, and all item details including item names and quantities, properly listed in JSON formatand,and if the image is cropped, blurry, or low quality then ask to re-upload a proper clear image."
        # prompt = "From this invoice, I need the party name, party address, party GST number, invoice amount, taxable amount, and all item details including item names and quantities, properly listed in JSON format"


        prompt = '''Extract invoice data with 100% accuracy. RETURN ONLY RAW JSON in the exact structure below. DO NOT CALCULATE ANYTHING. EXTRACT ONLY WHAT IS VISIBLE.

        {
        "party_name": "",
        "party_address": "",
        "party_gst_number": "",
        "place_of_supply": "",
        "invoice_amount": 0.00,
        "taxable_amount": 0.00,
        "tax_amount": 0.00,
        "items": [
            {
            "item_name": "",
            "hsn_code": "",
            "quantity": 0,
            "unit": "",
            "rate": 0.00,
            "amount": 0.00
            }
        ]
        }

        ### STRICT INSTRUCTIONS:

        1. ✅ **FLOAT NUMBERS: ALWAYS INCLUDE DECIMALS**
        - All monetary values must be returned as **floats with exactly two decimal places**.
        - If an amount is written as `15058000.00`, return it as `15058000.00`, not `15058000`.
        - Never drop `.00` or convert to integer.
        - Example:
            - `₹15058000.00` → `15058000.00`
            - `₹15000000` → `15000000.00`
            

        2. ✅ **ITEM EXTRACTION RULES**
        - Count every row in the item table. Extract exactly that many items.
        - Do NOT add extra rows.
        - `item_name`: Extract only the main product name. Remove codes, serial numbers, etc.
        - `hsn_code`: Extract HSN/SAC code exactly as shown.
        - `quantity`: Use number from "Qty" column.
        - `unit`: Unit like NOS, UNT, PCS, etc.
        - `rate`: Rate per unit as shown (e.g., `1500.00`).
        - `amount`: Use value from "Taxable Amount" or "Total" column. DO NOT calculate.

        3. ✅ **KEY FIELD RULES**
        - `party_name`: From "Bill From", "Buyer", or "Customer Name".
        - `party_address`: Full address including PIN code.
        - `party_gst_number`: GSTIN exactly as written. E.g., "27AABCCDDEEFFG if GSTIN else None".
        - `place_of_supply`: State name mentioned under "Place of Supply".
        - `invoice_amount`: Total amount labeled as "Total Amount", "Bill Amount", or "Grand Total". Must include `.00` if present.
        - `taxable_amount`: Sum of "Taxable Amt" column.
        - `tax_amount`: Tax amount (e.g., `58000.00`).

        4. ✅ **CHARACTER CLARITY**
        - If 'S' looks like '5', 'O' like '0', 'I' like '1', etc., return:
            ```json
            { "error": "Ambiguous character detected. Please upload a clearer image." }
            ```
        - Do not guess.

        5. ✅ **QUALITY CHECK**
        - If image is BLURRY, CROPPED, or LOW QUALITY and any field cannot be read with 100% confidence, return:
            ```json
            { "error": "Unclear image. Please upload a clear, complete, and legible invoice." }
            ```

        6. ✅ **OUTPUT FORMAT**
        - Return ONLY the JSON object.
        - No explanation, no markdown, no text before or after.
        - Wrap JSON in ```json if needed, but ensure it's parseable.

        RETURN ONLY THE JSON. NO OTHER TEXT.'''

        start_time = time.time()

        resp = ollama.chat(
            # model="qwen2.5vl:72b",
            # model="qwen2.5vl:32b",
            model="qwen2.5vl:7b",
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [image_path]
            }],
            stream=True 
        )

        content = ""
        for chunk in resp:
            if "message" in chunk and "content" in chunk["message"]:
                content += chunk["message"]["content"]


        # JSON extract
        match = re.search(r"```json\n(.*?)```", content, re.DOTALL)

        if match:
            json_data = json.loads(match.group(1))

            print("json_data=========:\n", json_data)

            end_time = time.time()
            elapsed = end_time - start_time
            print(f"Time taken: {elapsed:.2f} seconds")

            return jsonify({
                "status": "success",
                "message": "Invoice extracted successfully",
                "response": json_data,
                "elapsed_time": f"{elapsed:.2f} seconds"
            })

        else:
            return jsonify({
                "status": "fail",
                "message": "JSON not found in model response",
                "raw_response": content
            }), 422

    except FileNotFoundError as fnf:
        return jsonify({"status": "fail", "message": str(fnf)}), 404

    except ValueError as ve:
        return jsonify({"status": "fail", "message": str(ve)}), 400

    except Exception as e:
        return jsonify({"status": "fail", "message": f"Server Error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
