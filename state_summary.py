

import pandas as pd
import json
import sys
import subprocess
import os
import re

# Check Ollama
def check_ollama():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, encoding='utf-8')
        return 'NAME' in result.stdout
    except Exception:
        return False

# Read sample
def read_file_sample(file_path, nrows=5):
    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path, nrows=nrows)
        else:
            df = pd.read_excel(file_path, nrows=nrows)
        return df
    except Exception as e:
        print(json.dumps({"error": f"File read error: {str(e)}"}, indent=2))
        sys.exit(1)

# Clean and convert to numeric (handles ₹1,500, $200, etc.)
def to_numeric_clean(series):
    if series.dtype == 'float64' or series.dtype == 'int64':
        return pd.to_numeric(series, errors='coerce')
    # Remove ₹, $, commas, spaces
    return pd.to_numeric(
        series.astype(str).str.replace(r'[^\d.-]', '', regex=True),
        errors='coerce'
    )

# Ask Ollama
def ask_ollama_for_mapping(df_sample):
    sample_data = df_sample.head(3).to_string(index=False)
    prompt = f"""
    You are a data expert. From the given data, calculate state-wise totals.

    For each state, return JSON format:
    {{
    "state_name": {{
        "total_invoice_amount": number,
        "total_tax_amount": number,
        "total_discount_amount": number,
        "total_item_count": number
    }}
    }}

    Data:
    {sample_data}
    """

    cmd = ['ollama', 'run', 'mistral:7b', prompt]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=50
    )
    response = result.stdout.strip()
    start = response.find('{')
    end = response.rfind('}') + 1
    print("---------------------response---------------------", response)
    print("---------------------response---------------------")
    try:
        if start == -1: return None
        return json.loads(response[start:end])
    except Exception as e:
        print(f"⚠️ Ollama error: {e}", file=sys.stderr)
        return None

# Fallback: Rule-based detection
def detect_columns_fallback(df):
    cols = [str(col).strip() for col in df.columns]
    state_col = inv_col = tax_col = disc_col = None

    # Keywords (case-insensitive)
    state_k = r'state|shipto|billto|dest.state|province'
    inv_k  = r'total.*price|item.*value|invoice.*amt|order.*val|amount|sale|net.*amount|final.*value|grand.*total'
    tax_k  = r'tax|gst|cgst.*sgst|total.*tax|g.s.t|vat|tcs|t.d.s'
    disc_k = r'discount|disc|promo|coupon|offer|savings'

    for col in cols:
        val = str(col).lower()
        if not state_col and re.search(state_k, val, re.I):
            state_col = col
        if not inv_col and re.search(inv_k, val, re.I):
            inv_col = col
        if not tax_col and re.search(tax_k, val, re.I):
            tax_col = col
        if not disc_col and re.search(disc_k, val, re.I):
            disc_col = col

    # print(f"🔍 Fallback detected: state={state_col}, amount={inv_col}, tax={tax_col}, disc={disc_col}", file=sys.stderr)
    return {"state": state_col, "invoice_amount": inv_col, "tax_amount": tax_col, "discount_amount": disc_col}

# Validate and pick best numeric column
def validate_and_choose(df, mapping):
    for key in ["invoice_amount", "tax_amount", "discount_amount"]:
        col = mapping.get(key)
        if col and col in df.columns:
            cleaned = to_numeric_clean(df[col])
            valid_count = cleaned.notna().sum()
            if valid_count == 0:
                # print(f"❌ {col} has no valid numbers → skipping", file=sys.stderr)
                mapping[key] = None
            else:
                # print(f"✅ {col} → {valid_count} valid numbers", file=sys.stderr)
                pass
        else:
            mapping[key] = None
    return mapping

# Main
def process_file(file_path):
    if not os.path.exists(file_path):
        print(json.dumps({"error": "File not found"}, indent=2))
        return

    df_sample = read_file_sample(file_path)
    df_full = pd.read_csv(file_path) if file_path.lower().endswith('.csv') else pd.read_excel(file_path)

    # Step 1: Try Ollama
    mapping = ask_ollama_for_mapping(df_sample)
    if not mapping or not mapping.get("state"):
        # print("⚠️ Ollama failed → using fallback", file=sys.stderr)
        mapping = detect_columns_fallback(df_sample)

    # Step 2: Validate
    mapping = validate_and_choose(df_full, mapping)

    if not mapping["state"]:
        # print(json.dumps({"error": "State column not found"}, indent=2))
        return

    if mapping["state"] not in df_full.columns:
        # print(json.dumps({"error": f"State column '{mapping['state']}' missing"}, indent=2))
        return

    # Clean state
    df_full[mapping["state"]] = df_full[mapping["state"]].astype(str).str.strip()
    df_full = df_full[df_full[mapping["state"]].str.lower().isin(['nan', '']) == False]

    # Group
    grouped = df_full.groupby(mapping["state"])
    result = {}

    for state, group in grouped:
        if not state or state.lower() in ['nan', '']:
            continue

        # Clean and sum
        inv_amt = 0.0
        if mapping["invoice_amount"]:
            inv_amt = to_numeric_clean(group[mapping["invoice_amount"]]).sum()

        tax_amt = 0.0
        if mapping["tax_amount"]:
            tax_amt = to_numeric_clean(group[mapping["tax_amount"]]).sum()

        disc_amt = 0.0
        if mapping["discount_amount"]:
            disc_amt = to_numeric_clean(group[mapping["discount_amount"]]).sum()

        result[state] = {
            "total_invoice_amount": round(float(inv_amt), 2),
            "total_tax_amount": round(float(tax_amt), 2),
            "total_discount_amount": round(float(disc_amt), 2),
            "total_item_count": int(len(group))
        }

    print(json.dumps({"state": result}, indent=2))

# --- MAIN ---
if __name__ == "__main__":
    file_path = r"c:\Users\nilka\Desktop\amzone_messo\myntra\D4NQzbSW_2024-11-05_Seller_Orders_Report_17172_2024-10-01_2024-10-31.csv"
    if len(sys.argv) == 2:
        file_path = sys.argv[1]
    process_file(file_path)





# import pandas as pd
# import json
# import ollama

# EXCEL_FILE = r"c:\Users\nilka\Desktop\amzone_messo\myntra\D4NQzbSW_2024-11-05_Seller_Orders_Report_17172_2024-10-01_2024-10-31.csv"
# df = pd.read_csv(EXCEL_FILE)

# # sirf thoda data bhejna hai prompt me
# sample_data = df.head(20).to_dict(orient="records")
# columns = df.columns.tolist()

# prompt = f"""
# You are an expert data analyst. Below is a sample of a sales report (CSV/Excel).

# Identify the column for:
# - **state**: Customer's shipping state (e.g., Maharashtra, Karnataka, UP)
# - **invoice_amount**: Total item/order value before tax/discount
# - **tax_amount**: Total tax (GST, VAT, CGST+SGST, etc.)
# - **discount_amount**: Any discount applied (promotional, coupon, etc.)

# Return ONLY a JSON object like:
# {{
#   "state": "Ship State",
#   "invoice_amount": "Total Price",
#   "tax_amount": "GST",
#   "discount_amount": "Discount"
# }}

# If not found, use null. Be accurate.

# Data:
# {sample_data}
# """

# response = ollama.chat(
#     model="mistral:7b",   # ya "qwen2.5:7b"
#     messages=[{"role": "user", "content": prompt}],
#     options={"temperature": 0}
# )

# raw_output = response["message"]["content"]
# print("\n🔹 Raw Model Output:\n", raw_output)

# try:
#     result_json = json.loads(raw_output)
#     print("\n✅ Parsed JSON:\n", json.dumps(result_json, indent=2))
# except:
#     print("\n⚠️ JSON parse error. Raw output above.\n")
