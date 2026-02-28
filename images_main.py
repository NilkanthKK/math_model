# # python core code 
# import ollama
# import re
# import json
# import time

# # time the response
# start_time = time.time()

# resp = ollama.chat(
#     model="qwen2.5vl:32b",
#     messages=[
#         {
#             "role": "user",
#             "content": "From this invoice, I need the party name, party address, party GST number, invoice amount, taxable amount, and all item details including item names and quantities, properly listed in JSON format",
#             "images": ["C:\\Users\\nilka\\Desktop\\images\\bill9.jpg"]
#         }
#     ],
#     stream=True
# )

# content = ""
# for chunk in resp:
#     if "message" in chunk and "content" in chunk["message"]:
#         piece = chunk["message"]["content"]
#         # print(piece, end="", flush=True)  # realtime print
#         content += piece


# # time the response
# end_time = time.time() 
# elapsed = end_time - start_time


# # JSON extract after full response
# match = re.search(r"```json\n(.*?)```", content, re.DOTALL)
# if match:
#     json_data = json.loads(match.group(1))
#     print(json.dumps(json_data, indent=2))
# else:
#     print("JSON not found in response")

# print(f"\nResponse Time: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")


# Note :
# ollama model download

# ollama run qwen2.5vl:7b
# ollama run qwen2.5vl:32b




# prompt = '''Extract invoice data with 100% accuracy. RETURN ONLY RAW JSON in the exact structure shown below. DO NOT CALCULATE ANYTHING. EXTRACT ONLY WHAT IS VISIBLE.

# {
# "party_name": "",
# "party_address": "",
# "party_gst_number": "",
# "place_of_supply": "",
# "invoice_amount": 0.00,
# "taxable_amount": 0.00,
# "tax_amount": 0.00,
# "items": [
#     {
#     "item_name": "",
#     "hsn_code": "",
#     "quantity": 0,
#     "unit": "",
#     "rate": 0.00,
#     "amount": 0.00
#     }
# ]
# }

# ### STRICT INSTRUCTIONS:

# 1. ✅ **EXTRACT, DO NOT CALCULATE**  
# - Use ONLY values as printed on the invoice.  
# - Do NOT sum item amounts. Use the "Taxable Amount" column value directly.  
# - Do NOT add tax + taxable to get invoice amount. Use the "Grand Total", "Bill Amount", or "Invoice Total" as printed.

# 2. ✅ **ITEM EXTRACTION RULES**  
# - Count every row in the item table. Extract exactly that many items.  
# - `item_name`: Extract only the main product name. REMOVE all internal codes, serial numbers, SKUs, model numbers, or text in brackets like (ABC123), #XYZ, etc.  
#     - ❌ Bad: "Laptop Dell Inspiron (DINP123)"  
#     - ✅ Good: "Laptop Dell Inspiron"  
# - `hsn_code`: Extract HSN or SAC code exactly as shown in its column.  
# - `quantity`: Use number from "Qty" column.  
# - `unit`: Unit like PCS, NOS, KG, etc.  
# - `rate`: Rate per unit as shown.  
# - `amount`: Use value from "Taxable Amount" column for each row. DO NOT calculate (rate × qty).

# 3. ✅ **KEY FIELD RULES**  
# - `party_name`: From "BILL TO", "Buyer", or "Customer Name" or "Bill From" section.  
# - `party_address`: Full address including street, city, state, PIN code.  
# - `party_gst_number`: GSTIN exactly as written (e.g., 27AABCCDDEEFFG) and ex :If 'S' looks like '5', 'O' like '0', 'I' like '1', 'Z' like '2'.  
# - `place_of_supply`: State name mentioned under "Place of Supply".  
# - `invoice_amount`: Value labeled as "Grand Total", "Invoice Value", or "Bill Amount ex :If '6.99' looks like '6.99 not".  
# - `taxable_amount`: Total of "Taxable Value" column IF labeled, otherwise sum of all item `amount` fields ONLY IF clearly stated.  
# - `tax_amount`: Total GST, IGST, or Tax amount as printed (e.g., "Total Tax: ₹1,200").

# 4.✅ **FLOAT NUMBERS: ALWAYS INCLUDE DECIMALS**
# - All monetary values must be returned as **floats with exactly two decimal places**.
# - If an amount is written as `15058000.00`, return it as `15058000.00`, not `15058000`.
# - If an amount is written as `15000000`, return it as `15000000.00`.
# - Never drop `.00` or convert to integer.
# - Example:
#     - `₹15058000.00` → `15058000.00`
#     - `₹15000000` → `15000000.00`
#     - `₹58000` → `58000.00`

# 5. ✅ **QUALITY CHECK**  
# - If image is BLURRY, CROPPED, or LOW QUALITY and any field cannot be read with 100% confidence, return:
#     ```json
#     { "error": "Unclear image. Please upload a clear, complete, and legible invoice." }
#     ```
# - Do not guess or assume missing values.

# 6. ✅ **CHARACTER CLARITY**
# - If 'S' looks like '5', 'O' like '0', 'I' like '1', etc., return:
#     { "error": "Ambiguous character detected. Please upload a clearer image." }
# - Do not guess.

# 7. ✅ **OUTPUT FORMAT**  
# - Return ONLY the JSON object.  
# - No explanation, no markdown, no text before or after.  
# - Wrap JSON in ```json if needed, but ensure it's parseable.

# RETURN ONLY THE JSON. NO OTHER TEXT.'''
import ollama
import time
import re

start_time = time.time()

resp = ollama.chat(
    model="qwen2.5vl:7b",
    messages=[
        {
            "role": "user",
            "content": "1+1= ?",
        }
    ],
    options={
        "temperature": 0,
        "num_gpu": 1,
        "gpu_layers": 20000
    },
    stream=True
)


print("-------------------------")

# Collect full response
full_response = ""
for chunk in resp:
    if "message" in chunk:
        text = chunk["message"]["content"]
        print(text, end="", flush=True)
        full_response += text

print("\n-------------------------")

print("Time taken:", time.time() - start_time, "seconds")
