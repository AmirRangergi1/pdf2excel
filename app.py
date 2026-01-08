from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

from liara_pdf2excel import send_to_remote, convert_locally

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["OUTPUT_FOLDER"] = OUTPUT_FOLDER
app.secret_key = os.getenv("FLASK_SECRET", "devkey")


@app.route("/", methods=["GET"])
def index():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    model = request.form.get("model") or os.getenv("LIARA_MODEL")
    if not file:
        flash("No file uploaded")
        return redirect(url_for("index"))

    filename = Path(file.filename).name
    in_path = Path(app.config["UPLOAD_FOLDER"]) / filename
    file.save(in_path)

    out_name = filename.rsplit(".", 1)[0] + ".xlsx"
    out_path = Path(app.config["OUTPUT_FOLDER"]) / out_name

    endpoint = os.getenv("LIARA_API_ENDPOINT")
    api_key = os.getenv("LIARA_API_KEY")
    remote_only_env = os.getenv("REMOTE_ONLY")
    remote_only = True if remote_only_env is None or remote_only_env == "1" else False

    if not (endpoint and api_key):
        flash("Remote conversion requires LIARA_API_ENDPOINT and LIARA_API_KEY to be set in environment.")
        return redirect(url_for("index"))

    ok = send_to_remote(endpoint, api_key, model, str(in_path), str(out_path))
    if not ok:
        flash("Remote conversion failed and local fallback is disabled.")
        return redirect(url_for("index"))

    return redirect(url_for("download", filename=out_name))


@app.route("/downloads/<path:filename>")
def download(filename):
    return send_from_directory(app.config["OUTPUT_FOLDER"], filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
