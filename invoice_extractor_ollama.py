"""
LOCAL-OFFLINE INVOICE -> STRICT JSON (Ollama Vision) + Batch Folder Processing
Windows friendly | Core Python | No OCR libraries required (model reads image)

✅ Features
- Processes 1 image OR a whole folder (50-60 images)
- Strict JSON output only
- Two-pass mode (optional): first "image details" then "strict JSON" (improves accuracy)
- Never calculates, never guesses (tries best; missing -> "")
- Saves one JSON per image + one combined JSONL

Requirements:
  pip install ollama pillow

Ollama must be running:
  ollama serve
Model:
  ollama pull llama3.2-vision:11b

Run:
  python invoice_extractor_ollama.py --input "C:\\path\\to\\images" --out "C:\\path\\to\\out" --model "llama3.2-vision:11b" --two-pass
Or single file:
  python invoice_extractor_ollama.py --input "C:\\path\\to\\img.jpg" --out "C:\\path\\to\\out"
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image

try:
    import ollama
except ImportError:
    print("❌ Missing dependency: ollama\nRun: pip install ollama")
    sys.exit(1)


# ===================== PROMPTS =====================

SYSTEM_PROMPT_JSON = """
You are a strict JSON API.

Return ONLY valid JSON.
No explanation. No markdown. No extra text.
If a value is not clearly visible, return "".
Do NOT guess. Do NOT calculate.
Numbers must be exactly as printed (keep commas/₹/minus if present).
"""

# PASS-1: "Image details" (helps model understand layout; still no guessing)
USER_PROMPT_DETAILS = """
You are an invoice image reader.

Task: Read the invoice and list ONLY what is clearly visible.
Do NOT guess. Do NOT calculate. If unclear, write "".

Output in this exact format:

SELLER:
- name:
- gstin:
- address:
- mobile:

BUYER:
- name:
- gstin:
- address:
- mobile:

INVOICE:
- invoice_no:
- date:
- due_date:
- place_of_supply:

ITEMS (each line):
- description | hsn | qty | rate | amount | discount

TAX SUMMARY:
- cgst_rate:
- cgst_amount:
- sgst_rate:
- sgst_amount:
- igst_rate:
- igst_amount:
- total_tax:
- round_off:

TOTAL:
- taxable_amount:
- grand_total:
- outstanding:
"""

# PASS-2: strict JSON extraction. Optionally include DETAILS text to guide.
USER_PROMPT_JSON_TEMPLATE = """
Read this invoice image and extract structured data.

STRICT RULES:
- Extract ONLY what is visible in the image.
- Do NOT guess. Do NOT calculate.
- If not visible, return "".
- Items: include only actual product/service rows (not CGST/SGST/rounded/total rows).

Return exactly this JSON schema (same keys):

{
  "seller": {"name":"","gstin":"","address":"","mobile":""},
  "buyer": {"name":"","gstin":"","address":"","mobile":""},
  "invoice": {"number":"","date":"","due_date":"","place_of_supply":""},
  "items": [
    {"description":"","hsn_code":"","quantity":"","rate":"","amount":"","discount":""}
  ],
  "tax_details": {
    "cgst_rate":"",
    "cgst_amount":"",
    "sgst_rate":"",
    "sgst_amount":"",
    "igst_rate":"",
    "igst_amount":"",
    "total_tax_amount":"",
    "round_off":""
  },
  "totals": {
    "subtotal":"",
    "taxable_amount":"",
    "grand_total":"",
    "outstanding":""
  }
}

{details_block}
""".strip()


# ===================== UTILS =====================

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}

@dataclass
class RunConfig:
    model: str
    input_path: Path
    out_dir: Path
    max_size: int = 1400
    quality: int = 90
    temperature: float = 0.0
    top_p: float = 0.9
    num_predict: int = 1800
    two_pass: bool = False
    timeout_s: int = 0  # 0 = no custom timeout here


def safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def encode_image(image_path: Path, max_size: int = 1400, quality: int = 90) -> str:
    img = Image.open(image_path)
    if img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    if max(w, h) > max_size:
        scale = max_size / float(max(w, h))
        img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def strip_code_fences(text: str) -> str:
    text = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```\s*", "", text)
    return text.strip()


def extract_first_json_object(text: str) -> Optional[Dict[str, Any]]:
    """
    Robust JSON extraction:
    - Try direct parse
    - Strip markdown fences
    - Try to locate first {...} block and parse
    """
    if not text:
        return None

    text = strip_code_fences(text)

    # direct
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass

    # find first { ... } region
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        return None

    candidate = m.group(0)
    try:
        obj = json.loads(candidate)
        if isinstance(obj, dict):
            return obj
    except Exception:
        return None


def normalize_schema(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Ensure all keys exist and types are correct.
    """
    template: Dict[str, Any] = {
        "seller": {"name": "", "gstin": "", "address": "", "mobile": ""},
        "buyer": {"name": "", "gstin": "", "address": "", "mobile": ""},
        "invoice": {"number": "", "date": "", "due_date": "", "place_of_supply": ""},
        "items": [],
        "tax_details": {
            "cgst_rate": "",
            "cgst_amount": "",
            "sgst_rate": "",
            "sgst_amount": "",
            "igst_rate": "",
            "igst_amount": "",
            "total_tax_amount": "",
            "round_off": "",
        },
        "totals": {
            "subtotal": "",
            "taxable_amount": "",
            "grand_total": "",
            "outstanding": "",
        },
    }

    out = template.copy()

    # merge dict sections
    for k in ["seller", "buyer", "invoice", "tax_details", "totals"]:
        if isinstance(data.get(k), dict):
            out[k] = {**out[k], **{kk: ("" if data[k].get(kk) is None else str(data[k].get(kk))) for kk in out[k].keys()}}

    # items
    items = data.get("items")
    if isinstance(items, list):
        cleaned = []
        for it in items[:50]:
            if not isinstance(it, dict):
                continue
            cleaned.append({
                "description": str(it.get("description", "") or ""),
                "hsn_code": str(it.get("hsn_code", "") or ""),
                "quantity": str(it.get("quantity", "") or ""),
                "rate": str(it.get("rate", "") or ""),
                "amount": str(it.get("amount", "") or ""),
                "discount": str(it.get("discount", "") or ""),
            })
        out["items"] = cleaned

    return out


def ollama_chat(model: str, system_prompt: str, user_prompt: str, image_b64: Optional[str], *,
               temperature: float, top_p: float, num_predict: int) -> str:
    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_prompt.strip()},
    ]
    if image_b64:
        messages[-1]["images"] = [image_b64]

    resp = ollama.chat(
        model=model,
        format="json" if "strict JSON" in system_prompt.lower() or "strict json" in system_prompt.lower() or "JSON API" in system_prompt else None,
        messages=messages,
        options={
            "temperature": temperature,
            "top_p": top_p,
            "num_predict": num_predict,
        }
    )
    return resp["message"]["content"]


# ===================== CORE PIPELINE =====================

def extract_invoice_from_image(cfg: RunConfig, image_path: Path) -> Tuple[Optional[Dict[str, Any]], Dict[str, Any]]:
    """
    Returns:
      (result_json_or_none, debug_info)
    """
    debug: Dict[str, Any] = {
        "image": str(image_path),
        "model": cfg.model,
        "two_pass": cfg.two_pass,
        "status": "init",
        "details_text": "",
        "raw_json_text": "",
        "error": "",
        "elapsed_s": 0.0
    }

    t0 = time.time()

    try:
        image_b64 = encode_image(image_path, max_size=cfg.max_size, quality=cfg.quality)
    except Exception as e:
        debug["status"] = "fail"
        debug["error"] = f"Image encode error: {e}"
        debug["elapsed_s"] = round(time.time() - t0, 3)
        return None, debug

    details_text = ""
    if cfg.two_pass:
        try:
            details_text = ollama_chat(
                model=cfg.model,
                system_prompt="You are a careful document reader. Do NOT guess. Do NOT calculate.",
                user_prompt=USER_PROMPT_DETAILS,
                image_b64=image_b64,
                temperature=0.0,
                top_p=0.9,
                num_predict=900
            )
            details_text = strip_code_fences(details_text)
            debug["details_text"] = details_text
        except Exception as e:
            # two-pass is optional; continue to JSON pass even if details fails
            debug["details_text"] = ""
            debug["error"] = f"Details pass error (ignored): {e}"

    details_block = ""
    if details_text:
        # provide details as context to help the model stick to visible facts
        details_block = "\n\nCONTEXT (visible details extracted):\n" + details_text + "\n"

    user_prompt_json = USER_PROMPT_JSON_TEMPLATE.format(details_block=details_block)

    try:
        raw = ollama_chat(
            model=cfg.model,
            system_prompt=SYSTEM_PROMPT_JSON,
            user_prompt=user_prompt_json,
            image_b64=image_b64,
            temperature=cfg.temperature,
            top_p=cfg.top_p,
            num_predict=cfg.num_predict
        )
        debug["raw_json_text"] = raw
    except Exception as e:
        debug["status"] = "fail"
        debug["error"] = f"Ollama chat error: {e}"
        debug["elapsed_s"] = round(time.time() - t0, 3)
        return None, debug

    data = extract_first_json_object(raw)
    if not data:
        debug["status"] = "fail"
        debug["error"] = "Model did not return valid JSON object."
        debug["elapsed_s"] = round(time.time() - t0, 3)
        return None, debug

    debug["status"] = "ok"
    debug["elapsed_s"] = round(time.time() - t0, 3)
    return normalize_schema(data), debug


def list_images(input_path: Path) -> List[Path]:
    if input_path.is_file():
        return [input_path]

    files: List[Path] = []
    for p in sorted(input_path.rglob("*")):
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            files.append(p)
    return files
 

def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Image file path OR folder path")
    ap.add_argument("--out", required=True, help="Output folder path")
    ap.add_argument("--model", default="llama3.2-vision:11b", help="Ollama vision model name")
    ap.add_argument("--two-pass", action="store_true", help="Enable details->json two-pass extraction (recommended)")
    ap.add_argument("--max-size", type=int, default=1400, help="Resize longest side to this (improves OCR clarity)")
    ap.add_argument("--quality", type=int, default=90, help="JPEG quality for sending to model")
    ap.add_argument("--num-predict", type=int, default=1800, help="Max tokens to generate")
    args = ap.parse_args()

    cfg = RunConfig(
        model=args.model,
        input_path=Path(args.input),
        out_dir=Path(args.out),
        max_size=args.max_size,
        quality=args.quality,
        num_predict=args.num_predict,
        two_pass=args.two_pass,
    )

    if not cfg.input_path.exists():
        print("❌ Input path not found:", cfg.input_path)
        sys.exit(1)

    safe_mkdir(cfg.out_dir)

    images = list_images(cfg.input_path)
    if not images:
        print("❌ No images found in:", cfg.input_path)
        sys.exit(1)

    combined_jsonl = cfg.out_dir / "combined.jsonl"
    combined_debug = cfg.out_dir / "debug.jsonl"

    ok_count = 0
    fail_count = 0

    print(f"🧾 Starting extraction | images={len(images)} | model={cfg.model} | two_pass={cfg.two_pass}")
    print(f"📁 Output: {cfg.out_dir}")

    with combined_jsonl.open("w", encoding="utf-8") as fj, combined_debug.open("w", encoding="utf-8") as fd:
        for i, img in enumerate(images, start=1):
            print(f"\n[{i}/{len(images)}] 📄 {img.name}")
            result, dbg = extract_invoice_from_image(cfg, img)

            # per-image filenames
            base = img.stem
            out_json = cfg.out_dir / f"{base}.json"
            out_dbg = cfg.out_dir / f"{base}.debug.json"

            if result:
                write_json(out_json, result)
                fj.write(json.dumps({"file": str(img), "data": result}, ensure_ascii=False) + "\n")
                ok_count += 1
                print(f"✅ OK  | saved: {out_json.name} | time: {dbg['elapsed_s']}s")
            else:
                fail_count += 1
                # save debug even if failed
                write_json(out_dbg, dbg)
                print(f"❌ FAIL | saved debug: {out_dbg.name}")
                print("   reason:", dbg.get("error", ""))

            # always write debug line
            fd.write(json.dumps(dbg, ensure_ascii=False) + "\n")

    print("\n" + "=" * 60)
    print(f"✅ Done | OK={ok_count} | FAIL={fail_count}")
    print(f"📄 Combined JSONL : {combined_jsonl}")
    print(f"🪵 Debug JSONL    : {combined_debug}")
    print("=" * 60)


if __name__ == "__main__":
    main()