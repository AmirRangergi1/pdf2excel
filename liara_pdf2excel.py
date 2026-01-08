#!/usr/bin/env python3
"""
Simple CLI to send a PDF to an AI endpoint (configurable) or fall back
to a local PDF->Excel conversion using `pdfplumber` and `pandas`.

Usage:
  LIARA_API_ENDPOINT=<url> LIARA_API_KEY=<key> python liara_pdf2excel.py input.pdf output.xlsx
or (no API keys):
  python liara_pdf2excel.py input.pdf output.xlsx
"""
import os
import sys
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()


def send_to_remote(api_endpoint, api_key, model, in_path, out_path):
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
    with open(in_path, "rb") as f:
        files = {"file": (Path(in_path).name, f, "application/pdf")}
        data = {"model": model, "task": "pdf_to_excel", "response_format": "excel"}
        print(f"Uploading to {api_endpoint} using model={model}...")
        resp = requests.post(api_endpoint, headers=headers, files=files, data=data, timeout=300)

    if resp.status_code == 200:
        with open(out_path, "wb") as out:
            out.write(resp.content)
        print(f"Saved result to {out_path}")
        return True

    print(f"Remote conversion failed: {resp.status_code} {resp.reason}\n{resp.text}")
    return False


def convert_locally(in_path, out_path):
    try:
        import pdfplumber
        import pandas as pd
    except Exception as e:
        print("Local conversion requires `pdfplumber` and `pandas`. See requirements.txt.")
        raise
    tables_found = 0
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        with pdfplumber.open(in_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                try:
                    tables = page.extract_tables()
                except Exception:
                    tables = []
                for j, table in enumerate(tables, start=1):
                    df = pd.DataFrame(table)
                    sheet_name = f"p{i}_t{j}"
                    df.to_excel(writer, sheet_name=sheet_name[:31], index=False, header=False)
                    tables_found += 1

    if tables_found == 0:
        print("No tables found by pdfplumber. Output file will be empty or minimal.")
    print(f"Local conversion finished, wrote {tables_found} tables to {out_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Send PDF to AI (Liara/Gemini) or convert locally to Excel")
    parser.add_argument("input", help="Input PDF file")
    parser.add_argument("output", help="Output Excel file (.xlsx)")
    parser.add_argument("--remote-only", action="store_true", help="Require remote AI conversion and do not fall back to local conversion")
    parser.add_argument("--model", default=os.getenv("LIARA_MODEL", "google/gemini-2.0-flash-lite-001"), help="Model name (used only for remote API)")
    args = parser.parse_args()

    in_path = args.input
    out_path = args.output

    endpoint = os.getenv("LIARA_API_ENDPOINT")
    api_key = os.getenv("LIARA_API_KEY")
    remote_only_env = os.getenv("REMOTE_ONLY")
    remote_only = args.remote_only or (remote_only_env is None or remote_only_env == "1")

    if remote_only and not (endpoint and api_key):
        print("Remote-only mode is enabled but LIARA_API_ENDPOINT or LIARA_API_KEY is not set.\nPlease set these environment variables to use remote AI conversion.")
        sys.exit(3)
    # Attempt remote conversion
    ok = False
    if endpoint and api_key:
        ok = send_to_remote(endpoint, api_key, args.model, in_path, out_path)

    if not ok:
        print("Remote conversion failed or returned non-200.\nNo local fallback because remote-only mode is enabled." if remote_only else "Remote conversion failed; attempting local conversion...")
        if remote_only:
            sys.exit(2)
        try:
            convert_locally(in_path, out_path)
        except Exception as e:
            print("Local conversion failed:", e)
            sys.exit(4)


if __name__ == "__main__":
    main()
