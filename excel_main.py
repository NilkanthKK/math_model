# # import pandas as pd
# # import json
# # import ollama

# # # Load CSV
# # # csv_path = r"C:\Users\Hello\Desktop\amzone_messo\amazone\MTR_B2C-FEBRUARY-2025-A3BLZ9II8BQNQT.csv"
# # csv_path = r"c:\Users\Hello\Desktop\amzone_messo\messo\ReverseShipping.xlsx"
# # df = pd.read_csv(csv_path)

# # # Take sample (to avoid overload)
# # sample = df.head(50).to_dict(orient="records")
# # columns = df.columns.tolist()

# # # Prompt to Ollama
# # prompt = f"""
# # You are a data parser. 
# # Given the following CSV columns: {columns}
# # And data sample: {sample[:5]}

# # Task:
# # 1. Identify which columns represent:
# #    - ship_from_state
# #    - ship_to_state
# #    - invoice amount
# #    - tax amount
# #    - discount amount (all discounts combined)
# #    - item count / quantity
# # 2. Sum values state-wise.
# # 3. Return only valid JSON in this exact schema:

# # {{
# #   "ship_from_state": {{
# #     "STATE_NAME": {{
# #       "total_invoice_amount": number,
# #       "total_tax_amount": number,
# #       "total_discount_amount": number,
# #       "total_item_count": number
# #     }}
# #   }},
# #   "ship_to_state": {{
# #     "STATE_NAME": {{
# #       "total_invoice_amount": number,
# #       "total_tax_amount": number,
# #       "total_discount_amount": number,
# #       "total_item_count": number
# #     }}
# #   }}
# # }}

# # Important:
# # - No explanation, no markdown, only JSON output.
# # - All numeric values must be rounded to 2 decimals.
# # """

# # response = ollama.chat(model="mistral", messages=[{"role":"user","content":prompt}])

# # try:
# #     result_json = json.loads(response["message"]["content"])
# #     print(json.dumps(result_json, indent=2, ensure_ascii=False))
# # except Exception as e:
# #     print("❌ Parsing error:", e)
# #     print("Raw response:", response)



# # import pandas as pd
# # import json
# # import ollama
# # import os

# # # File path (change as needed)
# # file_path = r"c:\Users\Hello\Desktop\amzone_messo\myntra\D4NQzbSW_2024-11-05_Seller_Orders_Report_17172_2024-10-01_2024-10-31.csv"


# # # Detect file type
# # ext = os.path.splitext(file_path)[1].lower()

# # if ext in [".csv"]:
# #     df = pd.read_csv(file_path)

# # elif ext in [".xlsx", ".xls"]:
# #     df = pd.read_excel(file_path)

# # else:
# #     raise ValueError(f"❌ Unsupported file format: {ext}")


# # # Take sample (to avoid overload)
# # sample = df.head(50).to_dict(orient="records")
# # columns = df.columns.tolist()


# # # Prompt to Ollama
# # prompt = f"""
# # You are a strict JSON data parser. 
# # Given the following file columns: {columns}
# # And data sample: {sample[:5]}

# # Task:
# # 1. Identify which columns represent:
# #    - state (ship_from_state or ship_to_state or similar)
# #    - invoice amount
# #    - tax amount
# #    - discount amount (all discounts combined)
# #    - item count / quantity
# # 2. Sum values state-wise.
# # 3. If a column is missing, assume its total = 0.
# # 4. Return ONLY valid JSON in this exact schema:

# # {{
# #   "state": {{
# #     "STATE_NAME": {{
# #       "total_invoice_amount": number,
# #       "total_tax_amount": number,
# #       "total_discount_amount": number,
# #       "total_item_count": number
# #     }}
# #   }}
# # }}

# # Important rules:
# # - Only return JSON. No explanation, no text, no markdown.
# # - All numbers rounded to 2 decimals.
# # - If nothing is found, return {{"state": {{}}}}
# # """

# # response = ollama.chat(model="mistral-nemo:latest", messages=[{"role": "user", "content": prompt}])

# # try:
# #     result_json = json.loads(response["message"]["content"])
# #     print(json.dumps(result_json, indent=2, ensure_ascii=False))

# # except Exception as e:
# #     print("❌ Parsing error:", e)
# #     print("Raw response:", response["message"]["content"])





# # import pandas as pd
# # import json
# # import ollama
# # import os
# # import math
# # import time


# # # # File path
# # file_path = r"c:\Users\nilka\Desktop\amzone_messo\amazone\MTR_B2C-FEBRUARY-2025-A3BLZ9II8BQNQT.csv"

# # # # time the response
# # start_time = time.time()

# # # Load CSV
# # df = pd.read_csv(file_path)

# # # Batch size (rows per chunk to send to model)
# # batch_size = 50

# # num_batches = math.ceil(len(df) / batch_size)

# # all_results = {}

# # for i in range(num_batches):
# #     chunk = df.iloc[i*batch_size : (i+1)*batch_size]
# #     sample = chunk.to_dict(orient="records")
# #     columns = df.columns.tolist()

# #     prompt = f"""
# #     You are a strict JSON data parser. 
# #     Given the following file columns: {columns}
# #     And data sample: {sample}

# #     Task:
# #     1. Identify which columns represent:
# #        - state (ship_from_state or ship_to_state or similar)
# #        - invoice amount
# #        - tax amount
# #        - discount amount (all discounts combined)
# #        - item count / quantity
# #     2. Sum values state-wise.
# #     3. If a column is missing, assume its total = 0.
# #     4. Return ONLY valid JSON in this exact schema:

# #     {{
# #       "state": {{
# #         "STATE_NAME": {{
# #           "total_invoice_amount": number,
# #           "total_tax_amount": number,
# #           "total_discount_amount": number,
# #           "total_item_count": number
# #         }}
# #       }}
# #     }}

# #     Important rules:
# #     - Only return JSON. No explanation, no text, no markdown.
# #     - All numbers rounded to 2 decimals.
# #     - If nothing is found, return {{"state": {{}}}}
# #     """

# #     response = ollama.chat(
# #         model="qwen2.5vl:32b", 
# #         # model="stablelm2:12b", 
# #         # model="qwen2.5:14b", 
# #         messages=[{"role": "user", "content": prompt}]
# #     )

# #     result_json = json.loads(response["message"]["content"])

# #     print("=========================\n",result_json)
# #     print("=========================")
# #     try:

# #         for state, vals in result_json.get("state", {}).items():
# #             if state not in all_results:
# #                 all_results[state] = vals
# #             else:
# #                 # Merge batch results by adding values
# #                 all_results[state]["total_invoice_amount"] += vals["total_invoice_amount"]
# #                 all_results[state]["total_tax_amount"] += vals["total_tax_amount"]
# #                 all_results[state]["total_discount_amount"] += vals["total_discount_amount"]
# #                 all_results[state]["total_item_count"] += vals["total_item_count"]

# #     except Exception as e:
# #         print(f"❌ Error parsing batch {i+1}: {e}")

# # # time the response
# # end_time = time.time() 
# # elapsed = end_time - start_time
# # print(f"Time taken: {elapsed:.2f} seconds")


# # # Final merged JSON
# # final_result = {"state": all_results}
# # print(json.dumps(final_result, indent=2, ensure_ascii=False))



# # import pandas as pd
# # import json
# # import ollama
# import math
# import time

# # import tensorflow as tf
# # print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))


# # # File path
# # file_path = r"c:\Users\nilka\Desktop\amzone_messo\myntra\D4NQzbSW_2024-11-05_Seller_Orders_Report_17172_2024-10-01_2024-10-31.csv"

# # start_time = time.time()

# # # Load CSV
# # df = pd.read_csv(file_path)

# # # Batch size
# # batch_size = 20  # Reduce batch size to avoid overload

# # num_batches = math.ceil(len(df) / batch_size)

# # all_results = {}

# # for i in range(num_batches):
# #     print(f"\n🔍 Processing batch {i+1}/{num_batches}")
# #     chunk = df.iloc[i*batch_size : (i+1)*batch_size]
# #     sample = chunk.to_dict(orient="records")
# #     columns = df.columns.tolist()

# #     prompt = f"""
# #     You are a strict JSON data parser. 
# #     Given the following file columns: {columns}
# #     And data sample: {sample}

# #     Task:
# #     1. Identify which columns represent:
# #        - state (ship_from_state or ship_to_state or similar)
# #        - invoice amount
# #        - tax amount
# #        - discount amount (all discounts combined)
# #        - item count / quantity
# #     2. Sum values state-wise.
# #     3. If a column is missing, assume its total = 0.
# #     4. Return ONLY valid JSON in this exact schema:

# #     {{
# #       "state": {{
# #         "STATE_NAME": {{
# #           "total_invoice_amount": number,
# #           "total_tax_amount": number,
# #           "total_discount_amount": number,
# #           "total_item_count": number
# #         }}
# #       }}
# #     }}

# #     Important rules:
# #     - Only return JSON. No explanation, no text, no markdown.
# #     - All numbers rounded to 2 decimals.
# #     - If nothing is found, return {{"state": {{}}}}
# #     """

# #     try:
# #         response = ollama.chat(
# #             model="qwen2.5vl:32b",
# #             messages=[{"role": "user", "content": prompt}],
# #             options={
# #                 "temperature": 0,
# #                 "num_gpu": 1,
# #                 "gpu_layers": 40 
# #             }
# #         )



# #         result_json = json.loads(response["message"]["content"])

# #         print(f"✅ Batch {i+1} result:", json.dumps(result_json, indent=2))

# #         for state, vals in result_json.get("state", {}).items():
# #             if state not in all_results:
# #                 all_results[state] = {
# #                     "total_invoice_amount": 0,
# #                     "total_tax_amount": 0,
# #                     "total_discount_amount": 0,
# #                     "total_item_count": 0
# #                 }
# #             all_results[state]["total_invoice_amount"] += vals["total_invoice_amount"]
# #             all_results[state]["total_tax_amount"] += vals["total_tax_amount"]
# #             all_results[state]["total_discount_amount"] += vals["total_discount_amount"]
# #             all_results[state]["total_item_count"] += vals["total_item_count"]

# #     except Exception as e:
# #         print(f"❌ Error in batch {i+1}: {e}")
# #         continue

# # # Final result
# # end_time = time.time()
# # print(f"\n⏱️ Total time taken: {end_time - start_time:.2f} seconds")

# # final_result = {"state": all_results}
# # print("\n📊 Final merged result:")
# # print(json.dumps(final_result, indent=2, ensure_ascii=False))



# # import pandas as pd
# # import json
# # import ollama
# # import time
# # import sys

# # # ========================
# # # File path
# # # ========================
# # file_path = r"c:\Users\nilka\Desktop\amzone_messo\myntra\D4NQzbSW_2024-11-05_Seller_Orders_Report_17172_2024-10-01_2024-10-31.csv"

# # start_time = time.time()

# # # ========================
# # # Helper: read file sample
# # # ========================
# # def read_file_sample(file_path, nrows=5):
# #     try:
# #         if file_path.lower().endswith('.csv'):
# #             df = pd.read_csv(file_path, nrows=nrows)
# #         else:
# #             df = pd.read_excel(file_path, nrows=nrows)
# #         return df
# #     except Exception as e:
# #         print(json.dumps({"error": f"File read error: {str(e)}"}, indent=2))
# #         sys.exit(1)


# # # ========================
# # # Main processing
# # # ========================
# # df_sample = read_file_sample(file_path)
# # df_full = pd.read_csv(file_path) if file_path.lower().endswith('.csv') else pd.read_excel(file_path)

# # # 3 rows sample for prompt
# # sample_data = df_sample.head(3).to_string(index=False)


# # # Batch size
# # batch_size = 20  # Reduce batch size to avoid overload

# # df = pd.read_csv(df_full)

# # num_batches = math.ceil(len(df) / batch_size)

# # all_results = {}

# # for i in range(num_batches):
# #     print(f"\n🔍 Processing batch {i+1}/{num_batches}")
# #     chunk = df.iloc[i*batch_size : (i+1)*batch_size]
# #     sample = chunk.to_dict(orient="records")
# #     columns = df.columns.tolist()




# # prompt = f"""
# # You are a data expert. From the given data, calculate **state-wise totals**.
# # Given the following file columns: {columns}


# # For each state, return ONLY JSON format (no explanation, no extra text):

# # {{
# #   "state_name": {{
# #       "total_invoice_amount": number,
# #       "total_tax_amount": number,
# #       "total_discount_amount": number,
# #       "total_item_count": number
# #   }}
# # }}

# # Data sample:
# # {sample_data}
# # """

# # # ========================
# # # Call Ollama
# # # ========================
# # try:
# #     response = ollama.chat(
# #         model="qwen2.5:32b",   # qwen2.5vl bhi chalega agar installed hai
# #         messages=[{"role": "user", "content": prompt}],
# #         options={
# #             "temperature": 0,
# #             "num_gpu": 1,
# #             "gpu_layers": 40
# #         }
# #     )

# #     raw_output = response["message"]["content"].strip()
# #     print("\n🔹 Raw Model Output:\n", raw_output)

# #     # ========================
# #     # Try JSON parsing
# #     # ========================
# #     try:
# #         result_json = json.loads(raw_output)
# #         print("\n✅ Final JSON Result:\n", json.dumps(result_json, indent=2))
# #     except json.JSONDecodeError:
# #         # Agar JSON clean nahi hai to braces ke andar ka part extract karenge
# #         start = raw_output.find("{")
# #         end = raw_output.rfind("}") + 1
# #         if start != -1 and end != -1:
# #             try:
# #                 cleaned = raw_output[start:end]
# #                 result_json = json.loads(cleaned)
# #                 print("\n✅ Cleaned JSON Result:\n", json.dumps(result_json, indent=2))
# #             except Exception as e:
# #                 print("\n⚠️ JSON parse failed even after cleaning. Returning raw text.\n")
# #                 print(raw_output)
# #         else:
# #             print("\n⚠️ No JSON found in response.\n")
# #             print(raw_output)

# # except Exception as e:
# #     print(f"❌ Ollama error: {str(e)}")



# import pandas as pd
# import json
# import ollama
# import time
# import sys
# import math

# # ========================
# # File path
# # ========================
# file_path = r"c:\Users\nilka\Desktop\amzone_messo\myntra\D4NQzbSW_2024-11-05_Seller_Orders_Report_17172_2024-10-01_2024-10-31.csv"

# start_time = time.time()

# # ========================
# # Helper: read file sample
# # ========================
# def read_file_sample(file_path, nrows=5):
#     try:
#         if file_path.lower().endswith('.csv'):
#             df = pd.read_csv(file_path, nrows=nrows)
#         else:
#             df = pd.read_excel(file_path, nrows=nrows)
#         return df
#     except Exception as e:
#         print(json.dumps({"error": f"File read error: {str(e)}"}, indent=2))
#         sys.exit(1)


# # ========================
# # Main processing
# # ========================
# df_full = pd.read_csv(file_path) if file_path.lower().endswith('.csv') else pd.read_excel(file_path)
# columns = df_full.columns.tolist()

# # Batch size
# batch_size = 20  
# num_batches = math.ceil(len(df_full) / batch_size)

# all_results = {}

# for i in range(num_batches):
#     print(f"\n🔍 Processing batch {i+1}/{num_batches}")
#     chunk = df_full.iloc[i*batch_size : (i+1)*batch_size]

#     # Prompt ko batch ke data ke saath banao
#     sample_data = chunk.to_string(index=False)

#     prompt = f"""
#     You are a data expert. From the given data, calculate **state-wise totals**.
#     Given the following file columns: {columns}

#     For each state, return ONLY JSON format (no explanation, no extra text):

#     {{
#       "state_name": {{
#           "total_invoice_amount": number,
#           "total_tax_amount": number,
#           "total_discount_amount": number,
#           "total_item_count": number
#       }}
#     }}

#     Data sample:
#     {sample_data}
#     """

#     try:
#         response = ollama.chat(
#             model="llama2:7b",
#             messages=[{"role": "user", "content": prompt}],
#             options={
#                 "temperature": 0,
#                 "num_gpu": 1,
#                 "gpu_layers": 40
#             }
#         )

#         raw_output = response["message"]["content"].strip()
#         print("\n🔹 Raw Model Output:\n", raw_output)

#         # ========================
#         # Try JSON parsing
#         # ========================
#         try:
#             result_json = json.loads(raw_output)
#         except json.JSONDecodeError:
#             start = raw_output.find("{")
#             end = raw_output.rfind("}") + 1
#             if start != -1 and end != -1:
#                 cleaned = raw_output[start:end]
#                 result_json = json.loads(cleaned)
#             else:
#                 print("\n⚠️ No JSON found in response, skipping this batch.")
#                 continue

#         # ========================
#         # Merge results batch by batch
#         # ========================
#         for state, values in result_json.items():
#             if state not in all_results:
#                 all_results[state] = {
#                     "total_invoice_amount": 0,
#                     "total_tax_amount": 0,
#                     "total_discount_amount": 0,
#                     "total_item_count": 0
#                 }
#             all_results[state]["total_invoice_amount"] += values.get("total_invoice_amount", 0)
#             all_results[state]["total_tax_amount"] += values.get("total_tax_amount", 0)
#             all_results[state]["total_discount_amount"] += values.get("total_discount_amount", 0)
#             all_results[state]["total_item_count"] += values.get("total_item_count", 0)

#     except Exception as e:
#         print(f"❌ Ollama error in batch {i+1}: {str(e)}")

# # ========================
# # Final merged result
# # ========================
# print("\n================= FINAL MERGED RESULT =================")
# print(json.dumps(all_results, indent=2))



import cv2
import re
import json
import time
from paddleocr import PaddleOCR
import ollama

# -----------------------------
# CONFIG
# -----------------------------
IMAGE_PATH = r"C:\Users\Hello\Desktop\Images\5.jpg"
MODEL_NAME = "llama3.2"   # TEXT model only (NOT vision)

# -----------------------------
# STEP 1: OCR
# -----------------------------
def extract_text_from_image(image_path):
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    result = ocr.ocr(image_path)

    lines = []
    for line in result[0]:
        text = line[1][0]
        lines.append(text)

    return "\n".join(lines)


# -----------------------------
# STEP 2: TABLE ISOLATION LOGIC
# -----------------------------
def isolate_table(text):
    lines = text.split("\n")
    table_lines = []

    for line in lines:
        # detect numeric heavy rows
        numbers = re.findall(r"\d+\.\d+|\d+", line)

        if len(numbers) >= 2:
            # ignore summary lines
            if "total" not in line.lower() and "rupees" not in line.lower():
                table_lines.append(line)

    return "\n".join(table_lines)


# -----------------------------
# STEP 3: LLM JSON PARSER
# -----------------------------
def parse_with_llm(full_text, table_text):

    prompt = f"""
You are a strict invoice JSON generator.

RULES:
- Use FULL_TEXT for seller, buyer and invoice info.
- Use TABLE_TEXT ONLY for items.
- Ignore lines containing 'Rupees Only'.
- Ignore summary lines.
- Do not repeat fields.
- If value not found return empty string.
- Return RAW JSON only.

FULL_TEXT:
{full_text}

TABLE_TEXT:
{table_text}

Return in this format:

{{
  "seller": {{
    "name": "",
    "gstin": "",
    "address": "",
    "mobile": ""
  }},
  "buyer": {{
    "name": "",
    "address": "",
    "mobile": ""
  }},
  "invoice_details": {{
    "bill_number": "",
    "bill_date": "",
    "due_date": "",
    "place_of_supply": ""
  }},
  "items": [
    {{
      "item_name": "",
      "quantity": "",
      "rate": "",
      "taxable_amount": "",
      "total": ""
    }}
  ],
  "total_items": "",
  "grand_total": ""
}}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
        stream=False
    )

    return response["message"]["content"]


# -----------------------------
# MAIN PIPELINE
# -----------------------------
if __name__ == "__main__":

    start_time = time.time()

    print("🔎 Extracting OCR text...")
    full_text = extract_text_from_image(IMAGE_PATH)

    print("📊 Isolating table...")
    table_text = isolate_table(full_text)

    print("🤖 Parsing with LLM...")
    llm_output = parse_with_llm(full_text, table_text)

    # Safe JSON parse
    try:
        json_data = json.loads(llm_output)
        print("\n✅ FINAL JSON:\n")
        print(json.dumps(json_data, indent=2))
    except:
        print("\n❌ Invalid JSON returned:\n")
        print(llm_output)

    end_time = time.time()
    print(f"\n⏱ Total Time: {end_time - start_time:.2f} seconds")