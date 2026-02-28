import os
import json
import re
import time
from paddleocr import PaddleOCR
import ollama

MODEL = "gemma2:9b"
IMAGE_PATH = r"C:\Users\Hello\Desktop\Images\7.jpeg"

os.environ["OMP_NUM_THREADS"] = "1"

ocr = PaddleOCR(lang='en', use_angle_cls=True)


# ---------------- OCR ----------------
def extract_text(image_path):
    result = ocr.ocr(image_path)
    return "\n".join([line[1][0] for line in result[0]])


# ---------------- SMART FILTER ----------------
def smart_filter(text):
    important_words = [
        "invoice", "gst", "total", "amount",
        "tax", "qty", "quantity", "rate", "bill"
    ]

    lines = text.split("\n")
    filtered = [
        line for line in lines
        if any(w in line.lower() for w in important_words)
    ]

    return "\n".join(filtered) if filtered else text[:3500]


# ---------------- JSON CLEANER ----------------
def extract_json_from_text(text):
    # remove markdown
    text = re.sub(r"```.*?```", lambda m: m.group(0).replace("```json", "").replace("```", ""), text, flags=re.DOTALL)

    # remove comments
    text = re.sub(r"//.*", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        return None

    return text[start:end+1]


# ---------------- LLM CALL ----------------
def call_llm(text):

    prompt = f"""
    You are a JSON generator.

    Extract invoice data.

    STRICT RULES:
    - Output MUST be valid JSON.
    - No explanation.
    - No markdown.
    - No comments.
    - No text before or after JSON.
    - If value not found, return empty string "".
    - items must be a list (can be empty).

    Return only JSON.

    Schema:
    {{
    "seller": {{"name": "", "gstin": "", "address": "", "mobile": ""}},
    "buyer": {{"name": "", "gstin": "", "address": "", "mobile": ""}},
    "invoice_details": {{
        "bill_number": "",
        "bill_date": "",
        "due_date": "",
        "place_of_supply": ""
    }},
    "items": [],
    "total_items": "",
    "taxable_amount": "",
    "tax_amount": "",
    "grand_total": "",
    "outstanding_amount": ""
    }}

    Invoice Text:
    {text}
    """

    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": 0,
            "num_predict": 1200
        }
    )

    return response["message"]["content"]


# ---------------- MAIN ----------------
if __name__ == "__main__":

    print("🔍 Running OCR...")
    text = extract_text(IMAGE_PATH)

    filtered = smart_filter(text)
    filtered = text[:4000]  # limit length only

    print("🤖 Calling LLM...")
    start = time.time()
    raw_output = call_llm(filtered)
    elapsed = time.time() - start

    json_text = extract_json_from_text(raw_output)

    print("\n📦 Final Output:\n")

    try:
        data = json.loads(json_text)
        print(json.dumps(data, indent=2))
    except:
        print("⚠ JSON Parsing Failed")
        print(raw_output)

    print(f"\n⏱ Response Time: {elapsed:.2f} sec")