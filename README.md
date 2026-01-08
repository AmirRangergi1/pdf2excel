# pdf2excel

Small utility to send a PDF to an AI endpoint (Liara / Google Gemini via a compatible API)
or convert locally to an Excel file when no API is configured.

Usage

- Remote (send to AI service):

```bash
export LIARA_API_ENDPOINT="<base_url_or_upload_endpoint>"
export LIARA_API_KEY="<your_key>"
python liara_pdf2excel.py input.pdf output.xlsx
```

You must provide the correct `LIARA_API_ENDPOINT` and `LIARA_API_KEY` as described in the Liara docs: https://docs.liara.ir/ai/google-gemini/

Tip: the app will automatically load environment variables from a `.env` file (if present) using `python-dotenv`. Alternatively export variables in your shell before running.


Notes
- The script will attempt to POST the PDF as `file` to `LIARA_API_ENDPOINT` with form fields `model`, `task=pdf_to_excel`, and `response_format=excel`.
- By default the app is in "remote-only" mode and will NOT perform local conversion. To allow local fallback, set `REMOTE_ONLY=0` in your environment or pass `--remote-only` appropriately (CLI defaults to remote-only unless `--remote-only` is omitted).
- Adjust `LIARA_MODEL` env var if you want a different Gemini model.
